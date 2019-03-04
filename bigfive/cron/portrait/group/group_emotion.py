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


ES_INDEX_LIST = ["flow_text_2016-11-13","flow_text_2016-11-14","flow_text_2016-11-15","flow_text_2016-11-16","flow_text_2016-11-17","flow_text_2016-11-18","flow_text_2016-11-19","flow_text_2016-11-20","flow_text_2016-11-21","flow_text_2016-11-22","flow_text_2016-11-23","flow_text_2016-11-24","flow_text_2016-11-25","flow_text_2016-11-26","flow_text_2016-11-27"]

def get_time_list(es_list):
    time_list = []
    for n in ES_INDEX_LIST:
        ts = date2ts(n.split("_")[-1])
        time_list.append(ts)
    print (time_list)

    return time_list

def group_emotion(uid_list,group_id):
    time_list = get_time_list(ES_INDEX_LIST)
    for j in time_list:
        emotion_dict = {}
        emotion_dict["nuetral"] = 0
        emotion_dict["positive"] = 0
        emotion_dict["negtive"] = 0
        for i, user in enumerate(uid_list):
            query_body = {
                    "query": {
                        "bool": {
                        "must":[{
                            "term": {
                                "uid": user
                            }},
                            {
                            "term":{
                                "timestamp" : int(j)
                            }

                            }]
                        }},
                    "size":10000
                }
            es_result = es.search(index = "user_emotion",doc_type = "text",body = query_body)["hits"]["hits"][0]["_source"]
            emotion_dict["nuetral"] += es_result["nuetral"]
            emotion_dict["positive"] += es_result["positive"]
            emotion_dict["negtive"] += es_result["negtive"]
        emotion_dict["nuetral"] = float(emotion_dict["nuetral"])/len(uid_list)
        emotion_dict["positive"] = float(emotion_dict["positive"])/len(uid_list)
        emotion_dict["negtive"] = float(emotion_dict["negtive"])/len(uid_list)
        id_es = str(group_id) + "_" + str(j)
        #es.index(index = "group_emotion",doc_type = "text",id = id_es,body = {"timestamp":j,"nuetral":emotion_dict["nuetral"],"positive":emotion_dict["positive"],"negtive":emotion_dict["negtive"],"date":ts2date(j),group_id:group_id})
        print ({"timestamp":j,"nuetral":emotion_dict["nuetral"],"positive":emotion_dict["positive"],"negtive":emotion_dict["negtive"],"date":ts2date(j),group_id:group_id})


if __name__ == '__main__':

    query_body = {"query": {"bool": {"must": [{"match_all": {}}]}}}
    es_result = es.search(index = "group_information",doc_type = "text",body =query_body)["hits"]["hits"]
    for result in es_result:
        group_id = result["_source"]["group_id"]
        uid_list = result["_source"]["userlist"]
        group_emotion(uid_list,group_id)
	