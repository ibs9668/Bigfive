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
from sentiment_classification.triple_sentiment_classifier import triple_classifier


# 0中性 1积极 2生气 3焦虑 4悲伤 5厌恶 6消极其他

def cal_user_emotion(uid,weibo_data_dict):
    for day,weibo_list in weibo_data_dict.items():#value 为列表  key为日期
        es_timestamp = date2ts(day)
        sentiment_dict = {}
        sum_r = len(weibo_list)
        if sum_r :#此天有微博数据
            for weibo_item in weibo_list: #weibo_item为字典
                tweet = {}
                tweet["text"] = weibo_item["_source"]["text"]
                sentiment = triple_classifier(tweet) 
                es_weibo.update(index = weibo_item["_index"],doc_type = weibo_item["_type"],id = weibo_item["_id"],body = {"doc":{"sentiment":sentiment}})
                if sentiment not in sentiment_dict:
                    sentiment_dict[sentiment] = 1
                else:
                    sentiment_dict[sentiment] += 1
            for j in range(0,7):
                if j not in sentiment_dict:
                    sentiment_dict[j] = 0
            es.index(index = "user_emotion",doc_type = "text",id = uid+ "_"+str(es_timestamp), body = {"timestamp":es_timestamp,"uid": uid, "nuetral":  sentiment_dict[0], "positive": sentiment_dict[1], "negtive":sum_r-sentiment_dict[0]-sentiment_dict[1],"date":day})
            #print(uid,es_timestamp,sentiment_dict,sentiment_dict[0],sum_r,day)
            #print("================")
        else:
            es.index(index = "user_emotion",doc_type = "text",id = uid+ "_"+str(es_timestamp), body = {"timestamp":es_timestamp,"uid": uid, "nuetral":  0, "positive": 0, "negtive":0,"date":day})
            #print("no data")
        




if __name__ == '__main__':
    pass 
