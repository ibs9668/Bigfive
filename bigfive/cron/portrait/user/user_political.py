#-*-coding=utf-8-*-

import os
import sys
import csv
import re
import time
import math
import random
from decimal import *

import sys
sys.path.append('../../../')

from config import *
from time_utils import *
from cron.scws_utils import *


def load_word():#加载词典

    domain_dict = dict()
    for name in POLITICAL_LABELS:
        word_dict = dict()
        reader = csv.reader(open('political_bias_word_dict/%s.csv' % name, 'r'))
        for count,word in reader:
            word = word.strip('\r\t\n')
            count = count.strip('\r\t\n')
            word_dict[word] = Decimal(str(count))
        domain_dict[name] = word_dict
    
    return domain_dict

DOMAIN_DICT = load_word()


def get_word_count_dict(uid_weibo):

    uid_word_dict = dict()
    fc = fenci()
    fc.init_fenci()
    words = fc.get_text_fc(uid_weibo.decode(encoding='utf-8'))
    for word in words:
        if word in uid_word_dict.keys():
            uid_word_dict[word] = uid_word_dict[word] + 1
        else:
            uid_word_dict[word] = 1

    return uid_word_dict

#######得到用户列表 、用户微博，并得词频字典
def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    return uid_list

def get_uid_weibo(uid,list_index):

    uid_word_dict = dict()

    uid_text = ""

    query_body = {"query":{"bool":{"must":[{"term":{"uid":uid}}]}},"from":0,"size":10000}
    search_result = es_weibo.search(index=list_index, doc_type="text",body=query_body)["hits"]["hits"]

    if search_result != []:
        for i in search_result:
            uid_text = uid_text + i["_source"]["text"]

        word_count_dict = get_word_count_dict(uid_text.encode("utf-8"))
        uid_word_dict[uid] = word_count_dict

    return uid_word_dict

################用户政治倾向判断
def com_p(word_list,domain_dict):

    p = 0
    test_word = set(word_list.keys())
    train_word = set(domain_dict.keys())
    c_set = test_word & train_word
    p = sum([Decimal(domain_dict[k])*Decimal(word_list[k]) for k in c_set])

    return p

def political_classify(uid,uid_weibo):
    '''
    用户政治倾向分类主函数
    输入数据示例：
    uid_list:uid列表 [uid1,uid2,uid3,...]
    uid_weibo:分词之后的词频字典  {uid1:{'key1':f1,'key2':f2...}...}

    输出数据示例：
    domain：政治倾向标签字典
    {uid1:label,uid2:label2...}
    '''
    if not len(uid_weibo):
        domain = dict()
        r_domain = dict()
        domain[uid] = 'mid'
        return domain
    else:
        pass

    domain_dict = dict()
    r_domain = dict()
    for k,v in uid_weibo.items():
        dis = 0
        l = 'mid'
        r_dict = dict() #存储用户语料 与 每种倾向 的权重比值
        for la in POLITICAL_LABELS:
            re_weight = com_p(DOMAIN_DICT[la],v) #比较用户词频字典 和 语料库词频字典 相同词的个数
            r_dict[la] = re_weight
            if la == 'left' and re_weight >= LEFT_STA and re_weight > dis:
                dis = re_weight
                l = la
            if la == 'right' and re_weight >= RIGHT_STA and re_weight > dis:
                dis = re_weight
                l = la
        domain_dict[k] = l #存储最终政治倾向（）
        r_domain[k] = r_dict#存储各个政治倾向的权值

    return domain_dict

def get_user_political_bias(date):
    uid_list = get_uidlist()
    list_index = ["flow_text_"+str(ts2date(date2ts(date)-i*DAY)) for i in range(7)]
    count = 0

    for uid in uid_list[:10]:
        uid_word_dict = get_uid_weibo(uid,list_index)
        politic_result = political_classify(uid,uid_word_dict)
              
        es.update(index='user_information', doc_type='text', id=str(uid), body = {
        "doc":{
        "political_bias":list(politic_result.values())[0]
                } })

        count+=1


def get_user_political(uid,date,days):
    index_list = []
    for day in get_datelist_v2(ts2date(date2ts(date) - (days-1)*24*3600), date):
        index_list.append('flow_text_%s' % day)
    uid_word_dict = get_uid_weibo(uid,index_list)
    politic_result = political_classify(uid,uid_word_dict)
    es.update(index='user_information', doc_type='text', id=str(uid), body = {"doc":{"political_bias":politic_result.values()[0]}})

 
if __name__ == '__main__':
    get_user_political_bias("2016-11-20")
