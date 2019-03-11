#-*-coding=utf-8-*-
# -*- coding: UTF-8 -*-

import sys
sys.path.append('../')
from config import *
from time_utils import *
from global_utils import * 
import operator

#######事件名
EVENT_INFORMATION_2 = "event_ceshishijiansan_1551942139"

def get_user_list(event_name):
    user_list = []
    iter_num = 0
    iter_get_user = USER_ITER_COUNT
    while (iter_get_user == USER_ITER_COUNT):
        query_body = {
                "_source":["uid"],
                "query": {
                    "bool": {
                        "must": [
                        {
                        "match_all": { }
                        }
                    ]
                }
            },
            'sort':{
                '_id':{
                    'order':'asc'
                }
            },
            "size":USER_ITER_COUNT,
            "from":iter_num * USER_ITER_COUNT
        }
        es_result = es.search(index=event_name,doc_type='text',body=query_body)['hits']['hits']
        iter_get_user = len(es_result)
        iter_num += 1

        user_list.extend([hit['_source']['uid'] for hit in es_result])
        if len(user_list) == 0:
            break

    user_list_set = list(set(user_list))

    return user_list_set


def get_event_personality(user_list,event_id,start_date,end_date):
    #起止时间
    start_ts = int(date2ts(start_date))
    end_ts = int(date2ts(end_date))+DAY

    personality_dict = dict()
    for personality_label in PERSONALITY_LABEL_LIST:
        query_body_low = {
                    "query":{
                        "bool":{
                            "must":[
                                    {"terms":{"uid":user_list}},
                                    {"term":{personality_label:0}}
                                    ]
                                }
                        },
                    "size":MAX_VALUE

        }
        query_body_high = {
                    "query":{
                        "bool":{
                            "must":[
                                    {"terms":{"uid":user_list}},
                                    {"term":{personality_label:2}}
                                    ]
                                }
                        } ,
                    "size":MAX_VALUE
        }

        es_result_low = es.search(index= USER_RANKING ,doc_type="text",body=query_body_low)["hits"]["hits"]
        es_result_high = es.search(index= USER_RANKING ,doc_type="text",body=query_body_high)["hits"]["hits"]

        high_user_list = [i["_id"] for i in es_result_low]
        low_user_list = [i["_id"] for i in es_result_high]

        event_query_body_high = {
                    "query":{
                        "bool":{
                            "must":[
                                    {"terms":{"uid":high_user_list}},
                                    {"range": {
                                        "timestamp": {
                                            "gte": start_ts,
                                            "lt": end_ts
                                                }
                                            }
                                        }
                                    ]
                                }
                        } ,
                    "aggs":{"sentiment_aggs":{"terms":{"field":"sentiment"}}}
        }

        event_result_high = es.search(index=EVENT_INFORMATION_2,doc_type="text",body=event_query_body_high)["aggregations"]["sentiment_aggs"]["buckets"]
        es_result = es.search(index=EVENT_INFORMATION_2,doc_type="text",body=event_query_body_high)["hits"]["hits"]

        if es_result != []:
            event_content = [i["_source"] for i in es_result]
            mid_list = [i["mid"] for i in sorted(event_content,key = operator.itemgetter("timestamp"),reverse = True)[:5]]
        event_result_high.append({"mid_list":mid_list})



        event_query_body_low = {
                    "query":{
                        "bool":{
                            "must":[
                                    {"terms":{"uid":low_user_list}},
                                     {"range": {
                                        "timestamp": {
                                            "gte": start_ts,
                                            "lt": end_ts
                                                }
                                            }
                                        }
                                    ]
                                }
                        } ,
                    "aggs":{"sentiment_aggs":{"terms":{"field":"sentiment"}}}
        }

        event_result_low = es.search(index=EVENT_INFORMATION_2,doc_type="text",body=event_query_body_low)["aggregations"]["sentiment_aggs"]["buckets"]
        es_result_1 = es.search(index=EVENT_INFORMATION_2,doc_type="text",body=event_query_body_high)["hits"]["hits"]

        if es_result_1 != []:
            event_content = [i["_source"] for i in es_result_1]
            mid_list_1 = [i["mid"] for i in sorted(event_content,key = operator.itemgetter("timestamp"),reverse = True)[:5]]
        event_result_low.append({"mid_list": mid_list_1})

        id_body = {
                                "query":{
                                    "ids":{
                                        "type":"text",
                                        "values":[
                                            str(event_id)+"_"+str(date2ts(end_date))
                                        ]
                                    }
                                }
                            }
        if es.search(index='event_personality', doc_type='text', body= id_body)["hits"]["hits"] != []:
            es.update(index='event_personality', doc_type='text', id=str(event_id)+"_"+str(date2ts(end_date)), body = {
            "doc":{
                str(personality_label.split("_label")[0])+"_high":event_result_high,
                str(personality_label.split("_label")[0])+"_low":event_result_low
                    } })
        else:
            es.index(index='event_personality', doc_type='text', id=str(event_id)+"_"+str(date2ts(end_date)), body = {
            "event_id":event_id,
            "timestamp":int(date2ts(end_date)),
            "date":end_date,
            str(personality_label.split("_label")[0])+"_high":event_result_high,
            str(personality_label.split("_label")[0])+"_low":event_result_low
                    } )



if __name__ == '__main__':

    user_list = get_user_list(EVENT_INFORMATION_2)
    get_event_personality(user_list,EVENT_INFORMATION_2,"2016-11-13","2016-11-27")
    