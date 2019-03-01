#-*-coding=utf-8-*-
import os
import sys
import time
import csv
import heapq
import random
from decimal import *
import jieba

import sys
sys.path.append('../../../')
from config import *
from time_utils import *

def load_train():#读取生成之后的tfidf文档，对新的用户进行话题分类

    domain_dict = dict()
    domain_count = dict()
    for i in TOPIC_LIST:
        reader = csv.reader(open('topic_dict/%s_tfidf.csv' % i, 'r'))
        word_dict = dict()
        count = 0
        for f,w_text in reader:
            f = f.strip('\xef\xbb\xbf')
            word_dict[str(w_text)] = Decimal(f)
            count = count + Decimal(f)
        domain_dict[i] = word_dict
        domain_count[i] = count

    len_dict = dict()
    total = 0
    for k,v in domain_dict.items():
        len_dict[k] = len(v)
        total = total + len(v)
    
    return domain_dict,domain_count,len_dict,total

DOMAIN_DICT,DOMAIN_COUNT,LEN_DICT,TOTAL = load_train()


def sta_dict():#标准化话题字典

    topic_dict = dict()
    for name in TOPIC_LIST:
        topic_dict[name] = 0

    return topic_dict

TOPIC_DICT = sta_dict()


class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in range(len(self.data))])]

def com_p(word_list,domain_dict,domain_count,len_dict,total):

    p = 0
    test_word = set(word_list.keys())
    train_word = set(domain_dict.keys())
    c_set = test_word & train_word
    p = sum([float(domain_dict[k]*word_list[k])/float(domain_count) for k in c_set])

    return p

def load_weibo(uid_weibo):

    result_data = dict()
    p_data = dict()
    for k,v in uid_weibo.items():
        domain_p = TOPIC_DICT
        for d_k in domain_p.keys():
            domain_p[d_k] = com_p(v,DOMAIN_DICT[d_k],DOMAIN_COUNT[d_k],LEN_DICT[d_k],TOTAL)#计算文档属于每一个类的概率

            end_time = time.time()

        result_data[k] = domain_p
        p_data[k] = rank_result(domain_p)

    return result_data,p_data

def rank_dict(has_word):

    n = len(has_word)
    keyword = TopkHeap(n)
    count = 0
    for k,v in has_word.items():
        keyword.Push((v,k))
        count = count + v

    keyword_data = keyword.TopK()
    return keyword_data,count    

def rank_result(domain_p):
    
    data_v,count = rank_dict(domain_p)
    if count == 0:
        uid_topic = ['life']
    else:
        uid_topic = [data_v[0][1],data_v[1][1],data_v[2][1]]

    return uid_topic

def topic_classfiy(uid_list,uid_weibo):#话题分类主函数
    '''
    用户话题分类主函数
    输入数据示例：
    uidlist:uid列表（[uid1,uid2,uid3,...]）
    uid_weibo:分词之后的词频字典（{uid1:{'key1':f1,'key2':f2...}...}）

    输出数据示例：字典
    用户18个话题的分布：
    {uid1:{'art':0.1,'social':0.2...}...}
    用户关注较多的话题（最多有3个）：
    {uid1:['art','social','media']...}
    '''
    if not len(uid_weibo) and len(uid_list):
        result_data = dict()
        uid_topic = dict()
        for uid in uid_list:
            result_data[uid] = TOPIC_DICT
            uid_topic[uid] = ['life']
        return result_data,uid_topic
    elif len(uid_weibo) and not len(uid_list):
        uid_list = uid_weibo.keys()
    elif not len(uid_weibo) and not len(uid_list):
        result_data = dict()
        uid_topic = dict()
        return result_data,uid_topic
    else:
        pass        
        
    result_data,uid_topic = load_weibo(uid_weibo)#话题分类主函数

    for uid in uid_list:
        if uid not in result_data.keys():
            result_data[uid] = TOPIC_DICT
            uid_topic[uid] = ['life']
    
    return result_data,uid_topic


####################################

def stopwordslist():
    stopwords = [line.strip() for line in open('stop_words.txt').readlines()]
    return stopwords


def segment(doc):
    '''
    用jieba分词对输入文档进行分词，并保存至本地（根据情况可跳过）
    '''
    seg_list = " ".join(jieba.cut(doc, cut_all=False)) #seg_list为str类型

    return seg_list


def wordCount(segment_list):
    '''
        该函数实现词频的统计，并将统计结果存储至本地。
        在制作词云的过程中用不到，主要是在画词频统计图时用到。
    '''
    stopwords = stopwordslist()
    word_lst = []
    word_dict = {}
   
    word_lst.append(segment_list.split(' ')) 
    for item in word_lst:
        for item2 in item :
            if item2 not in stopwords:
                if item2 not in word_dict: 
                    word_dict[item2] = 1
                else:
                    word_dict[item2] += 1

    word_dict_sorted = dict(sorted(word_dict.items(), \
    key = lambda item:item[1], reverse=True))#按照词频从大到小排序

    return word_dict_sorted

def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index=USER_INFORMATION, doc_type="text",body=query_body,timeout=50)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    return uid_list

def get_weibo_index(RUN_TYPE,start_date,last_time): #start_date:开始日期前一天

    weibo_index_pre = "flow_text_"
    if RUN_TYPE == 1:       
        now_date = ts2datetime(time.time())
        now_date_ts = date2ts(now_date)+DAY#今天零点时间戳
    elif RUN_TYPE == 2:
        start_date_ts = date2ts(start_date) #开始时间戳

        weibo_index_list = []
        for i in range(last_time):
            start_date_ts = int(start_date_ts+ DAY)
            start_date = ts2datetime(start_date_ts)
            if es_weibo.indices.exists(index=str(weibo_index_pre)+str(start_date)) :
                weibo_index_list.append(str(weibo_index_pre)+str(start_date))

    return weibo_index_list

def save_topic(uid_list,timestamp,index_list):
    for uid in uid_list:
        uid_word_dict = dict()
        uid_list2 = []
        uid_list2.append(uid) ####转换成列表，传给topic_classify
        uid_text = ""

        query_body = {"query":{"bool":{"must":[{"term":{"uid":uid}}]}},"from":0,"size":10000}
        search_result = es_weibo.search(index=index_list, doc_type="text",body=query_body,timeout=50)["hits"]["hits"]

        if search_result != []:
            time_n = time.time()
            for i in search_result:
                uid_text = uid_text + i["_source"]["text"]

            segment_list = segment(uid_text)

            word_count_dict = wordCount(segment_list)

            uid_word_dict[uid] = word_count_dict

            result_data,uid_topic = topic_classfiy(uid_list2,uid_word_dict)

            for m in result_data:
                topic_list = []
                id_body = {
                                "query":{
                                    "ids":{
                                        "type":"text",
                                        "values":[
                                            str(m)+"_"+str(timestamp)
                                        ]
                                    }
                                }
                            }
                if es.search(index=USER_DOMAIN_TOPIC, doc_type='text', body= id_body)["hits"]["hits"] != []:#1970833007_1479484800
                    
                    es.update(index=USER_DOMAIN_TOPIC, doc_type='text', id=str(m)+"_"+str(timestamp), body = {
                    "doc":
                    {"timestamp": timestamp,
                    "uid":m,
                    "topic_art":result_data[m]["art"],
                    "topic_computer":result_data[m]["computer"],
                    "topic_economic":result_data[m]["economic"],
                    "topic_education":result_data[m]["education"],
                    "topic_environment":result_data[m]["environment"],
                    "topic_medicine":result_data[m]["medicine"],
                    "topic_military":result_data[m]["military"],
                    "topic_politics":result_data[m]["politics"],
                    "topic_sports":result_data[m]["sports"],
                    "topic_traffic":result_data[m]["traffic"],
                    "topic_life":result_data[m]["life"],
                    "topic_anti_corruption":result_data[m]["anti-corruption"],
                    "topic_employment":result_data[m]["employment"],
                    "topic_violence":result_data[m]["fear-of-violence"],
                    "topic_house":result_data[m]["house"],
                    "topic_law":result_data[m]["law"],
                    "topic_peace":result_data[m]["peace"],
                    "topic_religion":result_data[m]["religion"],
                    "topic_social_security":result_data[m]["social-security"]
                 
                        }},timeout=50)
                else:

                    es.index(index=USER_DOMAIN_TOPIC,doc_type="text",id=str(m)+"_"+str(timestamp),
                    body={
                    "timestamp": timestamp,
                    "uid":m,
                    "topic_art":result_data[m]["art"],
                    "topic_computer":result_data[m]["computer"],
                    "topic_economic":result_data[m]["economic"],
                    "topic_education":result_data[m]["education"],
                    "topic_environment":result_data[m]["environment"],
                    "topic_medicine":result_data[m]["medicine"],
                    "topic_military":result_data[m]["military"],
                    "topic_politics":result_data[m]["politics"],
                    "topic_sports":result_data[m]["sports"],
                    "topic_traffic":result_data[m]["traffic"],
                    "topic_life":result_data[m]["life"],
                    "topic_anti_corruption":result_data[m]["anti-corruption"],
                    "topic_employment":result_data[m]["employment"],
                    "topic_violence":result_data[m]["fear-of-violence"],
                    "topic_house":result_data[m]["house"],
                    "topic_law":result_data[m]["law"],
                    "topic_peace":result_data[m]["peace"],
                    "topic_religion":result_data[m]["religion"],
                    "topic_social_security":result_data[m]["social-security"]
                 
                            },timeout=50)
                # count += 1
                # print (count)

        else:
            pass


if __name__ == '__main__':

    date_list= ["2016-11-13","2016-11-14","2016-11-15","2016-11-16","2016-11-17","2016-11-18",\
        "2016-11-19","2016-11-20","2016-11-21","2016-11-22","2016-11-23","2016-11-24","2016-11-25",\
        "2016-11-26","2016-11-27"]

    timestamp = date2ts("2016-11-19")

    uid_list = get_uidlist()
    index_list = get_weibo_index(2,"2016-11-12",7)
    save_topic(uid_list,timestamp,index_list)
