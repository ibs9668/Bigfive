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

def group_emotion(group_id,uid_list,date):
    date_ts = date2ts(date)
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
                            "timestamp" : date_ts
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
    id_es = str(group_id) + "_" + str(date_ts)
    es.index(index = "group_emotion",doc_type = "text",id = id_es,body = {"timestamp":date_ts,"nuetral":emotion_dict["nuetral"],"positive":emotion_dict["positive"],"negtive":emotion_dict["negtive"],"date":ts2date(date_ts),"group_id":group_id})

def group_emotion_long(group_id, uid_list, start_date, end_date):
    for day in get_datelist_v2(start_date, end_date):
        try:
            group_emotion(group_id,uid_list,day)
        except:
            pass

if __name__ == '__main__':

    query_body = {"query": {"bool": {"must": [{"match_all": {}}]}}}
    es_result = es.search(index = "group_information",doc_type = "text",body =query_body)["hits"]["hits"]
    for result in es_result:
        group_id = result["_source"]["group_id"]
        uid_list = result["_source"]["userlist"]
        group_emotion(uid_list,group_id)
	