# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
import os
import numpy as np
import pandas as pd
import jieba
import re
import random
import time
import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
from elasticsearch import Elasticsearch

from config import *
from time_utils import *

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

stopwords_filepath = os.path.join(ABS_PATH, 'model/stopwords.txt')

def ts2date(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))


def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    #print (uid_list)
    return uid_list


def read_weibo_text_data(uid_list,start_time,end_time):
    users_weibo = {}
    #start_date = ts2date(start_time)
    end_date = datetime.datetime.fromtimestamp(end_time)
    next_date = datetime.datetime.fromtimestamp(start_time)
    es_date = []
    es_date.append(next_date.strftime("%Y-%m-%d"))
    while next_date != end_date:
       next_date = next_date + datetime.timedelta(days=1)
       date_r = next_date.strftime("%Y-%m-%d")
       es_date.append(date_r)
    es_index_list = []
    for date in es_date:
        es_index_list.append("flow_text_"+str(date))

    for user in uid_list:
        users_weibo[user] = []
        for j in es_index_list:
            query_body = {
                "query": {
                    "bool": {
                    "must":[{
                        "term": {
                            "uid": user
                        }}]
                    }},
                "size":10000
            }
            weibo_result = es_weibo.search(index=j, doc_type="text", body=query_body)["hits"]["hits"]
            if len(weibo_result) != 0:
                for weibo_item in weibo_result:
                    users_weibo[user].append(weibo_item["_source"]["text"])
            else:
                continue
    return users_weibo



# 微博数据的相关清洗处理，为分词做准备
def weibo_clean(weibo):
    if weibo.find('扇贝打卡') >= 0:
        weibo = ''

    # 去链接
    url_pattern = r'http://t.cn/\w+'
    weibo = re.sub(url_pattern, '', weibo)

    if weibo.find('//') >= 0:
        weibo = weibo.split('//')[0]

    # 去表情并提出保存
    emo_pattern = re.compile(r'\[.*?\]')
    weibo = emo_pattern.sub('', weibo)

    # 去@
    at_pattern = re.compile(r'@[\w-]+|@.*?\s|@.*?:')
    weibo = at_pattern.sub('', weibo)

    # 去问号等
    weibo = weibo.replace('?', '')
    weibo = weibo.replace('？','')
    weibo = weibo.replace('转发微博', '')
    weibo = weibo.replace('回复:', '')

    return weibo


# 分词
def cut_text(text):
    text = weibo_clean(text)
    seg_list = jieba.cut(text)  # 结巴分词
    stopwords = [line.strip() for line in open(stopwords_filepath, 'r', encoding='utf-8').readlines()]  # 读取停用词表
    stopwords.extend(['(', ')', '\\', '/', '|', '[', ']', ' '])
    word_list = [w.strip() for w in seg_list if (w not in set(stopwords))]  # 去停用词

    return word_list


#得到每位用户的文本特征表示
def get_word_feature(user_weibo, user_list, unique_keywords, tfidf_keywords):
    texts_list = []
    for u in user_list:
        texts_list.append(user_weibo[u])

    words_list = []
    for texts in texts_list:
        wt = []
        for t in texts:
            word = cut_text(t)
            wt.extend(word)
        words_list.append(" ".join(str(w) for w in wt))

    vectorizer = CountVectorizer(vocabulary=unique_keywords)
    unique_words_feature = vectorizer.fit_transform(words_list).toarray()

    vectorizer = CountVectorizer(vocabulary=tfidf_keywords)
    tfidf_words_feature = vectorizer.fit_transform(words_list).toarray()

    return unique_words_feature, tfidf_words_feature


#将预测结果存入文件
def save_predict_result(y):
    np.save('result/per_result.npy', y)  #numpy格式保存

    # excel形式输出
    t = {'uid':y[0],'Extraversion':y[1],'Agreeableness':y[2],'Conscientiousness':y[3],'Neuroticism':y[4],'Openness':y[5],'马基雅维利主义':y[6],'自恋':y[7],'精神病态':y[8]}
    df = pd.DataFrame(t)
    output_file = 'result/personality_predoct_result.xlsx'
    writer = pd.ExcelWriter(output_file)
    df.to_excel(writer, 'Sheet1')
    writer.close()

    return None


'''
输入 ：需要计算人格的uid列表 ，计算开始时间，计算结束时间
输出格式 用户ID，和8个人格维度 每个小列表相对应位置为一个用户的数据
per_score是具体人格得分，per_label是标注的-1，0，1的人格标签
#per_score:[[2396658275, 2146717162], [2.258750345202391, 2.4233166202732423], [3.222510234200444, 4.037989694706863], [3.2753118582277914, 2.4988223398561185], [2.6164536741214057, 2.7531023608864453], [2.883958173402279, 3.3925144752876024], [3.122643872238177, 3.677871838264575], [2.7396718735876875, 2.3361247854887925]]
#per_label:[[2396658275, 2146717162], [-1, 0], [0, 0], [0, -1], [-1, 0], [0, 0], [0, 0], [0, 0], [-1, 0]]
'''
#预测用户的人格得分，返回对应用户的人格得分列表，使用时调用此函数,
def predict_personality(uid_list,start_time,end_time):

    tfidf_keywords = np.load(os.path.join(ABS_PATH, 'model/tfidf_keywords.npy'))
    unique_keywords = np.load(os.path.join(ABS_PATH, 'model/unique_keywords.npy'))
    threshold = np.load(os.path.join(ABS_PATH, 'model/threshold_all.npy'))
    
    user_weibo = read_weibo_text_data(uid_list,start_time,end_time)
    user_list = list(user_weibo.keys())

    per_label_predict = []
    per_score_predict = []
    per_label_predict.append(user_list)
    per_score_predict.append(user_list)
    per_name = ['Extraversion','Agreeableness','Conscientiousness','Neuroticism','Openness','马基雅维利主义','自恋','精神病态']

    for i in range(8):
        unique_word_feature, tfidf_word_feature = get_word_feature(user_weibo, user_list, unique_keywords[i], tfidf_keywords[i])

        model_name = os.path.join(ABS_PATH, 'model/' + per_name[i] + '_NBmodel_0.pkl')
        clf_0 = joblib.load(model_name)
        y = clf_0.predict(unique_word_feature)
        y_prob = clf_0.predict_proba(unique_word_feature)

        idx_1 = np.where(y == 1)
        if len(idx_1[0]) > 0:
            unique_word_feature_1 = unique_word_feature[idx_1]
            tfidf_word_feature_1 = tfidf_word_feature[idx_1]
            model_name = os.path.join(ABS_PATH, 'model/' + per_name[i] + '_NBmodel_1.pkl')
            clf_1 = joblib.load(model_name)
            if i == 0 or i == 2 or i == 6:
                y_1 = clf_1.predict(unique_word_feature_1)
                y_prob_1 = clf_1.predict_proba(unique_word_feature_1)
            else:
                y_1 = clf_1.predict(tfidf_word_feature_1)
                y_prob_1 = clf_1.predict_proba(tfidf_word_feature_1)
            y[idx_1] = y_1
            y_prob[idx_1] = y_prob_1

        y_score = []
        for yidx, yl in enumerate(y):
            if yl == 0:
                y_score.append(random.uniform(threshold[i][1], threshold[i][2]))
            elif yl == 1:
                y_score.append(threshold[i][2] + y_prob[yidx][1]*(threshold[i][3]-threshold[i][2]))
            elif yl == -1:
                y_score.append(threshold[i][1] - y_prob[yidx][-1]*(threshold[i][1]-threshold[i][0]))

        per_label_predict.append(list(y))
        per_score_predict.append(y_score)

    # save_predict_result(per_label_predict)
    return per_label_predict, per_score_predict


if __name__ == "__main__":

    #uid_list = get_uidlist()
    uid_list = [2396658275,2146717162]
    per_label, per_score = predict_personality(uid_list,1478966400,1478966400)
    print(per_label, per_score)
    # save_predict_result(per_score)
    '''
    输入 ：需要计算人格的uid列表 ，计算开始时间，计算结束时间
    输出格式 用户ID，和8个人格维度 每个小列表相对应位置为一个用户的数据
           per_score是具体人格得分，per_label是标注的-1，0，1的人格标签
    #per_score:[[2396658275, 2146717162], [2.258750345202391, 2.4233166202732423], [3.222510234200444, 4.037989694706863], [3.2753118582277914, 2.4988223398561185], [2.6164536741214057, 2.7531023608864453], [2.883958173402279, 3.3925144752876024], [3.122643872238177, 3.677871838264575], [2.7396718735876875, 2.3361247854887925]]
    #per_label:[[2396658275, 2146717162], [-1, 0], [0, 0], [0, -1], [-1, 0], [0, 0], [0, 0], [0, 0], [-1, 0]]
    '''



