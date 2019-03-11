# -*- coding: UTF-8 -*-

import os
import time
import numpy as np
import math

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

def get_max_fansnum():
    query_body = {"aggs": {"max_fansnum": {"max": {"field": "fans_num"}}}}
    #uid_list = ["2396658275"]
    max_fansnum  = es.search(index="user_information", doc_type="text", body = query_body)["aggregations"]["max_fansnum"]["value"]
    
    return max_fansnum

'''
domain:最终身份领域 topic
'''
def cal_importance(domain, topic_list, user_fansnum, fansnum_max):
    result = 0
    domain_result = 0
    domain_result = DOMAIN_WEIGHT_DICT[domain]
    print (domain_result)
    topic_result = 0
    try :
        for topic in topic_list:
            topic_result += TOPIC_WEIGHT_DICT[topic]
    except :
        topic_result = 0
    result = (IMPORTANCE_WEIGHT_DICT['fansnum']*math.log(float(user_fansnum)/ fansnum_max*9+1, 10) + \
            IMPORTANCE_WEIGHT_DICT['domain']*domain_result + IMPORTANCE_WEIGHT_DICT['topic']*(topic_result / 3))*100


    return result

def get_importance(uid_list,max_fansnum,ES_INDEX_LIST):
    for j in ES_INDEX_LIST:
        for i,_ in enumerate(uid_list):#一个索引为一天
            es_timestamp = date2ts(j.split("_")[-1])
            id_es = str(_) +"_" + str(es_timestamp)
            importance = 0
            try:
                domain_topic_result = es.get(index="user_domain_topic", doc_type="text", id = id_es)["_source"]
                topic_list = []
                for key in domain_topic_result.keys():
                    if "topic_" in key:
                        value = float(domain_topic_result[key])
                        if value > 0:
                            topic_list.append(key)
                domain = domain_topic_result["main_domain"]
                user_info = es.get(index="user_information", doc_type="text", id = _)["_source"]
                user_fansnum = user_info["fans_num"]
                importance = cal_importance(domain, topic_list, user_fansnum, max_fansnum)
                
            except:
                importance = 0
            es.update(index = "user_influence",doc_type = "text",id = id_es, body ={"doc":{"importance":importance}})

if __name__ == '__main__':
    #uid_list = get_uidlist()
    uid_list = ["2713343591"]
    max_fansnum = get_max_fansnum()
    ES_INDEX_LIST = ["flow_text_2016-11-13"]
    get_importance(uid_list,max_fansnum,ES_INDEX_LIST)
