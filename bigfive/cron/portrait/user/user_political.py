#-*-coding=utf-8-*-

import os
import sys
import csv
import scws
import re
import time
# import heapq
import math
import random
from decimal import *

import sys
sys.path.append('../../../')

from config import *
from time_utils import *


SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1

ABSOLUTE_DICT_PATH = './dict'
# os.path.abspath(os.path.join(abs_path, 
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'black.txt')

labels = ['left','right','mid']
LEFT_STA = 6000
RIGHT_STA = 3000

def load_word():#加载词典

    domain_dict = dict()
    for name in labels:
        word_dict = dict()
        reader = csv.reader(open('political_bias_word_dict/%s.csv' % name, 'rb'))
        for count,word in reader:
            word = word.strip('\r\t\n')
            count = count.strip('\r\t\n')
            word_dict[word] = Decimal(str(count))
        domain_dict[name] = word_dict
    
    return domain_dict

DOMAIN_DICT = load_word()


def load_scws():
    s = scws.Scws()
    s.set_charset(SCWS_ENCODING)

    s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

    # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
    s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
    # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
    s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

    s.set_rules(SCWS_RULES)
    s.set_ignore(IGNORE_PUNCTUATION)
    return s

def cut_filter(text):
    pattern_list = [r'\（分享自 .*\）', r'http://\w*']
    for i in pattern_list:
        p = re.compile(i)
        text = p.sub('', text)
    return text

def re_cut(w_text):#根据一些规则把无关内容过滤掉
    
    w_text = cut_filter(w_text)
    a1 = re.compile(r'回复' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\:' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\s' )
    w_text = a1.sub('',w_text)
    if w_text == '转发微博':
        w_text = ''

    return w_text


sw = load_scws()

def get_word_count_dict(uid_weibo):

    uid_word_dict = dict()
    words = sw.participle(uid_weibo)
    for word in words:
        if uid_word_dict.has_key(word[0]):
            uid_word_dict[word[0]] = uid_word_dict[word[0]] + 1
        else:
            uid_word_dict[word[0]] = 1

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

def political_classify(uid_list,uid_weibo):
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
        # print 1
        domain = dict()
        r_domain = dict()
        domain[uid] = 'mid'
        return domain
    # elif len(uid_weibo) and not len(uid_list):
    #     uid_list = uid_weibo.keys()
    elif not len(uid_weibo) and not len(uid_list):
        domain = dict()
        return domain
    else:
        pass

    domain_dict = dict()
    r_domain = dict()
    for k,v in uid_weibo.items():
        # print 2
        dis = 0
        l = 'mid'
        r_dict = dict() #存储用户语料 与 每种倾向 的权重比值
        for la in labels:
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
    
    # for uid in uid_list:
    #     if not domain_dict.has_key(uid):
    #         domain_dict[uid] = 'mid'

    return domain_dict
 

####################################
 
if __name__ == '__main__':

    uid_list = get_uidlist()
    list_index = [ 'flow_text_2016-11-14', 'flow_text_2016-11-15', 'flow_text_2016-11-16',\
                 'flow_text_2016-11-17', 'flow_text_2016-11-18', 'flow_text_2016-11-19', 'flow_text_2016-11-20']

    count = 0

    for uid in uid_list:
        uid_word_dict = get_uid_weibo(uid,list_index)
        # print uid_word_dict
        politic_result = political_classify(uid,uid_word_dict)
        
        es.update(index='user_information', doc_type='text', id=str(uid), body = {
        "doc":{
        "political_bias":politic_result.values()[0]
                } })
        count+=1
        print (count)


