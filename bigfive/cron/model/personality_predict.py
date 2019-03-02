# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
import os
import numpy as np
import pandas as pd
import jieba
import re
import json
import time
import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.externals import joblib
from elasticsearch import Elasticsearch

from config import *
from time_utils import *

father_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")

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



def read_weibo_text_data(uid_list,start_date,end_date):
    users_weibo = {}
    es_date = get_datelist_v2(start_date,end_date)
    es_index_list = []
    for date in es_date:
        es_index_list.append("flow_text_"+date)


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


def get_user_else_feature(uid_list):
    follow = []
    follower = []
    weibo_count  = []
    for user in uid_list:
        user_info = es.get(index="user_information", doc_type="text",id = user)["_source"]
        follow.append(int(user_info['friends_num']))
        follower.append(int(user_info['fans_num']))
        weibo_count.append(int(user_info['weibo_num']))
    else_feature = np.transpose([follow, follower, weibo_count])

    return else_feature



# 微博数据的相关清洗处理，为分词做准备
def weibo_clean(weibo):
    # 去表情并提出保存
    emo_pattern = re.compile(r'\[.*?\]')
    emos = emo_pattern.findall(weibo)
    weibo = emo_pattern.sub('', weibo)

    # 去@
    at_pattern = re.compile(r'@[\w-]+|@.*?\s|@.*?:')
    weibo = at_pattern.sub('', weibo)

    # 去链接
    url_pattern = r'http://t.cn/\w+'
    weibo = re.sub(url_pattern, '', weibo)

    # 去回复
    huifu_pattern = r'回复:'
    weibo = re.sub(huifu_pattern, '', weibo)

    if weibo == '转发微博':
        weibo = ''
    return weibo, emos



def cut_text(text):

    text, emo = weibo_clean(text)
    seg_list = jieba.cut(text)  # 结巴分词
    stopwords_filepath = '%s/model/stopwords.txt' % father_path
    stopwords = [line.strip() for line in open(stopwords_filepath, 'r', encoding='utf-8').readlines()]  # 读取停用词表
    stopwords.extend(['(', ')', '\\', '/', '|', '[', ']', ' '])
    word_list = [w.strip() for w in seg_list if (w not in set(stopwords))]  # 去停用词
    word_list.extend(emo)

    return word_list


#得到每位用户的文本特征表示
def get_word_feature(user_weibo, user_list, keywords_filepath):
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

    keywords = np.load(keywords_filepath)
    vectorizer = CountVectorizer(vocabulary=keywords)
    words_feature = vectorizer.fit_transform(words_list).toarray()

    return words_feature


def save_predict_result(y):  # 将预测结果存入文件
    np.save('%s/result/per_result.npy' % father_path, y)  #numpy格式保存

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
    #[['2146717162'，"uid2"], [2.850552158006373,a], [3.674095918821599,b], [3.2880626149813974], [3.1653211890612742], [3.246121272128871], [3.324488726243067], [2.726574264907801], [2.4002086889189544]]
    '''
#预测用户的人格得分，返回对应用户的人格得分列表，使用时调用此函数,
def predict_personality(uid_list,start_time,end_time):

    bigfive_keywords_filepath = '%s/model/bigfive_keywords.npy' % father_path
    dark_keywords_filepath = '%s/model/dark_keywords.npy' % father_path

    print('Start getting weibo data...')
    user_weibo = read_weibo_text_data(uid_list,start_time,end_time)


    user_list = list(user_weibo.keys())
    print('Start getting user else feature...')
    else_feature = get_user_else_feature(user_list)

    per_predict = []
    per_predict.append(user_list)
    per_name = ['Extraversion','Agreeableness','Conscientiousness','Neuroticism','Openness','马基雅维利主义','自恋','精神病态']

    for i in range(8):
        print('Predict %s...' % per_name[i])
        if i < 5:
            word_feature = get_word_feature(user_weibo, user_list, bigfive_keywords_filepath)
        else:
            word_feature = get_word_feature(user_weibo, user_list, dark_keywords_filepath)

        x = np.concatenate((word_feature, else_feature), axis=1)
        model_name = father_path + '/model/'+per_name[i] + '_regression_model.pkl'
        regression_model = joblib.load(model_name)
        y = regression_model.predict(x)
        per_predict.append(list(y))

    # save_predict_result(per_predict)

    return per_predict

if __name__ == "__main__":
    
    #uid_list = get_uidlist()
    uid_list = ["2396658275"]
    per_predict = predict_personality(uid_list,1478966400,1480176000)
    print(per_predict)
    '''
    输入 ：需要计算人格的uid列表 ，计算开始时间，计算结束时间
    输出格式 用户ID，和8个人格维度 每个小列表相对应位置为一个用户的数据
    #[['2396658275'，"uid2"], [2.850552158006373,a], [3.674095918821599,b], [3.2880626149813974], [3.1653211890612742], [3.246121272128871], [3.324488726243067], [2.726574264907801], [2.4002086889189544]]
    '''



