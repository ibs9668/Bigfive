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
from global_utils import ESIterator

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

def load_word():#加载词典

    domain_dict = dict()
    for name in POLITICAL_LABELS:
        word_dict = dict()
        reader = csv.reader(open(os.path.join(ABS_PATH, 'political_bias_word_dict/%s.csv' % name), 'r'))
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


def get_uid_weibo(uid,index_name):

    uid_word_dict = dict()
    uid_text = ""

    for index_item in index_name:

        query_body ={"query": {"bool": {"must":[{"term": {"uid": uid}}]}}}
        sort_dict = {'_id':{'order':'asc'}}
        try:
            ESIterator1 = ESIterator(0,sort_dict,1000,index_item,"text",query_body,es_weibo)
            while True:
                try:
                    #一千条es数据
                    es_result = next(ESIterator1)
                    if len(es_result):
                        for i in range(len(es_result)):
                            uid_text += es_result[i]["_source"]["text"] 
                    else:
                        pass
                       
                except StopIteration:
                    #遇到StopIteration就退出循环
                    break
        except:
            continue

    if uid_text != "":
        word_count_dict = get_word_count_dict(uid_text.encode("utf-8"))
        uid_word_dict[uid] = word_count_dict
    else:
        return uid_word_dict

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



def get_user_political(uid,start_date,end_date):
    for day in get_datelist_v2(start_date,end_date):
        timestamp = date2ts(day)
        index_list = []
        for i in range(7):
            date = ts2date(date2ts(day) - i*DAY)
            index_list.append('flow_text_%s' % date)
        uid_word_dict = get_uid_weibo(uid,index_list)
        politic_result = political_classify(uid,uid_word_dict)
        es.update(index='user_information', doc_type='text', id=str(uid), body = {"doc":{"political_bias":list(politic_result.values())[0]}})


 
if __name__ == '__main__':
    get_user_political_bias("2016-11-20")
