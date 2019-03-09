# -*- coding: UTF-8 -*-

import os
import time


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
	

#情绪计算 一个用户 一天一条数据（一个索引为一天）
def cal_sentiment(uid_list,ES_INDEX_LIST):
    for i,_ in enumerate(uid_list):
        for j in ES_INDEX_LIST:
            query_body = {
                    "query": {
                        "bool": {
                        "must":[{
                            "term": {
                                "uid": _
                            }}]
                        }
                
                    }
                }
            sum_r = es_weibo.count(index=j, doc_type="text", body=query_body)["count"]
            
            es_timestamp = date2ts(j.split("_")[-1])
            if sum_r != 0:
                sentiment_value = []
                for val in SENTIMENT_INDEX_LIST:
                    query_body_1 = {
                        "query": {
                            "bool": {
                                "must":[{
                                    "term": {
                                        "uid": _
                                    }},
                                   {
                                    "term": {
                                    "sentiment": val
                                    }
                                    }]}}
                    }
                    result = es_weibo.count(index=j, doc_type="text", body=query_body_1)["count"]
                    sentiment_value.append(result)
               
                #用户uid 时间 中性 积极 消极
                es.index(index = "user_emotion",doc_type = "text",id = _+ "_"+str(es_timestamp), body = {"timestamp":es_timestamp,"uid": _, "nuetral":  sentiment_value[0], "positive": sentiment_value[1], "negtive":sum_r-sentiment_value[0]-sentiment_value[1]})                 
            else:
               
                es.index(index = "user_emotion",doc_type = "text",id = _+ "_"+str(es_timestamp), body = {"timestamp":es_timestamp,"uid": _, "nuetral":  0, "positive": 0, "negtive":0})


def cal_social(uid_list,ES_INDEX_LIST):
    for i,_ in enumerate(uid_list):
        for j in ES_INDEX_LIST:
            for val in MESSAGE_TYPE_LIST:
                query_body = {
                    "query": {
                        "bool": {
                        "must":[{
                            "term": {
                                "uid": _
                            }},
                            {
                            "term": {
                                "message_type": val
                            }
                            }
                            ]
                        }
                
                    },
                    "size": 10000
                }
                result = es_weibo.search(index=j, doc_type="text", body=query_body)["hits"]["hits"]
                if result:
                    #print (len(result))
                    for n in result:
                    	uid_list = []
                        #print (target_name)
                        source = n["_source"]["root_uid"]
                        try:
                            es_timestamp = date2ts(j.split("_")[-1])
                            source_inf = es.get(index="weibo_user", doc_type="type1",id = source)
                            if source_inf["found"] == True:
                                source_name = source_inf["_source"]["name"].encode("utf-8")
                            message_type = val
                            
                            target = _ 
                            target_inf = es.get(index="user_information", doc_type="text",id = _)
                            if target_inf["found"] == True:
                                target_name = target_inf["_source"]["username"].encode("utf-8")
                            else:
                                target_name = target
                            
                            id_es = str(target)+"_"+ str(source) +"_"+str(es_timestamp)+"_"+str(message_type)
                            #print (id_es)
                            es.index(index = "user_social_contact",doc_type = "text",id = id_es, body = {"timestamp":es_timestamp,"source": source, "target": target, "source_name": source_name, "target_name":target_name,"message_type":message_type})
                        except:
                            print ("no")
                        #print (source_name)
                        
                        



if __name__ == '__main__':

    #uid_list = get_uidlist()
    #cal_sentiment(uid_list)
    uid_list = ["2396658275"]
    ES_INDEX_LIST = ["flow_text_2016-11-13"]
    cal_social(uid_list,ES_INDEX_LIST)
    cal_sentiment(uid_list,ES_INDEX_LIST)
