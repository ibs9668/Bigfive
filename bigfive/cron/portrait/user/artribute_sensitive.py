# -*- coding: UTF-8 -*-

import os
import time
import numpy as np
import math
import json

import sys
sys.path.append('../../../')
from config import *
from time_utils import *

    

def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    #print (uid_list)
    return uid_list

# sensitive_words
def createWordTree():
    wordTree = [None for x in range(256)]

    wordTree.append(0)
    nodeTree = [wordTree, 0]

    awords = []

    for b in open('sensitive_words.txt', 'rb'):
        awords.append(b.strip().split('\t')[0])
        #所有敏感词列表


    for word in awords:
        temp = wordTree
        for a in range(0,len(word)):
            index = ord(word[a])
            if a < (len(word) - 1):
                if temp[index] == None:
                    node = [[None for x in range(256)],0]

                    temp[index] = node
                elif temp[index] == 1:
                    node = [[None for x in range(256)],1]

                    temp[index] = node
                
                temp = temp[index][0]
            else:
                temp[index] = 1

    return nodeTree 


def searchWord(str, nodeTree):#分词
    temp = nodeTree
    words = []
    word = []
    a = 0
    while a < len(str):
        index = ord(str[a])

        temp = temp[0][index]
        if temp == None:
            temp = nodeTree
            a = a - len(word)
            word = []
        elif temp == 1 or temp[1] == 1:
            word.append(index)
            words.append(word)
            a = a - len(word) + 1 
            word = []
            temp = nodeTree
        else:
            word.append(index)
        a = a + 1
    
    map_words = {}

    for w in words:
        iter_word = "".join([chr(x) for x in w])
        if not map_words.__contains__(iter_word):
            map_words[iter_word] = 1
        else:
            map_words[iter_word] = map_words[iter_word] + 1

    
    return map_words


def cal_sensitive(today_sensitive_words_dict):

    #print (aaa)
    #node = createWordTree()

    #sensitive_words_dict = searchWord(text.encode('utf-8', 'ignore'), node)

    sensitive_score_dict = { "1": 1,"2": 5,"3": 10}
    sensitive_words_weight = dict()
    for b in open('sensitive_words.txt', 'rb'):
        word = b.strip().split('\t')[0]
        weight =  b.strip().split('\t')[1]
        sensitive_words_weight[word] =  weight
    score = 0
    if today_sensitive_words_dict:
        for k,v in today_sensitive_words_dict.iteritems():
            tmp_stage = sensitive_words_weight.get(k, 0)

            if tmp_stage:
                score += v*sensitive_score_dict[str(tmp_stage)]

    return score

def get_sensitive(uid_list,ES_INDEX_LIST):
    for j in ES_INDEX_LIST:
        for n,user in enumerate(uid_list):#一个索引为一天
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
            es_timestamp = date2ts(j.split("_")[-1])
            id_es = str(user) +"_" + str(es_timestamp)
            try :
                user_influence_result = es.get(index="user_influence", doc_type="text",id =id_es)
                es_result = es_weibo.search(index=j, doc_type="text", body=query_body)["hits"]["hits"]
                sensitive = 0.0
                if len(es_result) != 0:#当前发了微博
                    print (len(es_result))
                    node = createWordTree()
                    today_sensitive_words_dict = {}
                    for weibo_item in es_result:#每一条微博
                        text = weibo_item["_source"]['text']
                        sensitive_words_dict = searchWord(text.encode('utf-8', 'ignore'), node)
                        for word in sensitive_words_dict :
                            if word not in today_sensitive_words_dict:
                                today_sensitive_words_dict[word] = 1
                    print (today_sensitive_words_dict)
                    sensitive = cal_sensitive(today_sensitive_words_dict)
                else:
                    sensitive = 0.0
                
                es.update(index = "user_influence",doc_type = "text",id = id_es, body ={"doc":{"sensitivity":sensitive}})
                print (sensitive,es_timestamp)
            except:
                pass

if __name__ == '__main__':

    #uid_list = get_uidlist()
    uid_list = ["2146717162"]
    ES_INDEX_LIST = ["flow_text_2016-11-13"]
    get_sensitive(uid_list,ES_INDEX_LIST)
                 


