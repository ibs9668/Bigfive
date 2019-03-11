# -*- coding: UTF-8 -*-

import os
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
#input: user_activeness_geo {geo1:count, geo2:count,...} for the latest dat  ,user_activeness_time {'statusnum':value, 'activity_time':value}
def get_day_activeness(user_day_activeness_geo, user_day_activeness_time,uid):
    result = 0
    # get day geo dict by ip-timestamp result
    max_freq = user_day_activeness_time[uid]['activity_time']

    statusnum = user_day_activeness_time[uid]['statusnum']
    activity_geo_count = len(user_day_activeness_geo.keys())
    result = activeness_weight_dict['activity_time'] * math.log(max_freq  + 1) + \
             activeness_weight_dict['activity_geo'] * math.log(activity_geo_count + 1) +\
             activeness_weight_dict['statusnum'] * math.log(statusnum + 1)
    return result




def get_day_activity_time(user_day_activity_time):
    results = {}
    activity_list_dict = {} # {uid:[activity_list]}
    uid = user_day_activity_time["uid"]
    activity_list_dict[uid] = []
                
    for i in range(0, 96):
        try:
            count = user_day_activity_time["time_segment"][i]
        except:
            count = 0
        activity_list_dict[uid].append(count)
    #print (activity_list_dict)
    activity_list = activity_list_dict[uid]
    statusnum = sum(activity_list)

    signal = np.array(activity_list)

    fftResult = np.abs(np.fft.fft(signal))**2
    n = signal.size
    freq = np.fft.fftfreq(n, d=1)
    i = 0
    max_val = 0
    max_freq = 0
    for val in fftResult:
        if val>max_val and freq[i]>0:
            max_val = val
            max_freq = freq[i]
        i += 1

    results[uid] = {'statusnum': statusnum, 'activity_time': math.log(max_freq + 1)}
    
    return results
    #{uid: {'activity_time':x, 'statusnum':y}}

#计算用户活跃度 每一个用户每一天（索引）一个活跃度 找出一天的全部微博 遍历微博
#输入 uid_list = ["2713343591"],ES_INDEX_LIST = ["flow_text_2016-11-13"]
def cal_activeness(uid_list,ES_INDEX_LIST):
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
                
                    },
                    "size" : 10000
                }
            es_result = es_weibo.search(index=j, doc_type="text", body=query_body)["hits"]["hits"]#一个用户一天发的所有微博
            #print (es_result)
            if len(es_result) != 0:
                user_day_activity_time = {}
                user_day_activity_time["uid"] = _ 
                timestamp = es_result[0]["_source"]['timestamp']
                date  = ts2date(timestamp)
                ts = date2ts(date)
                user_day_activity_time["timestamp"] = ts
                time_segment_dict = {}
                user_day_activeness_geo = {}
                for weibo_item in es_result:#每一条微博
                    timestamp = weibo_item["_source"]['timestamp']
                    date_1  = ts2date(timestamp)
                    ts_1 = date2ts(date_1)
                    time_segment = (timestamp - ts_1) / Fifteenminutes
                    if time_segment not in time_segment_dict:
                        time_segment_dict[time_segment] = 1
                    else:
                    	time_segment_dict[time_segment] += 1
                    geo = weibo_item["_source"]['geo']
                    if geo not in user_day_activeness_geo:
                        user_day_activeness_geo[geo] = 1
                    else:
                        user_day_activeness_geo[geo] += 1
                #print (time_segment_dict)
                #print (user_day_activeness_geo)
                #user_day_activeness_geo :{u'\u4e2d\u56fd&\u5c71\u897f&\u4e34\u6c7e': 4}
                user_day_activity_time["time_segment"] = time_segment_dict
                #user_day_activity_time : {'timestamp': 1478448000, 'uid': '2396658275', 'time_segment': {93: 2, 94: 2}})
                #print (j,user_day_activity_time)

                user_day_activeness_time = get_day_activity_time(user_day_activity_time)
                #user_day_activeness_time:{'2396658275': {'activity_time': 0.010362787035546658, 'statusnum': 4}}
                activeness = get_day_activeness(user_day_activeness_geo,user_day_activeness_time,_)
                print (activeness)
                
            else:
                activeness = 0
            es_timestamp = date2ts(j.split("_")[-1])
            
            id_es = str(_) +"_" + str(es_timestamp)
            es.update(index = "user_influence",doc_type = "text",id = id_es, body ={"doc": {"activity": activeness}})





if __name__ == '__main__':

    #uid_list = get_uidlist()
    uid_list = ["2713343591"]
    ES_INDEX_LIST = ["flow_text_2016-11-13"]
    cal_activeness(uid_list,ES_INDEX_LIST)
