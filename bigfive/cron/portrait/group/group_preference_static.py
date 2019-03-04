#-*-coding=utf-8-*-
import os
import sys
import time
import csv
import heapq
import random
from decimal import *

import sys
sys.path.append('../../../')

from config import *
from time_utils import *
# import uniout
def get_group_dict(): ###得到群体字典：{id1:[],id2:[]}
    group_dict = dict()
    query_body = {"query":{"bool":{"must":[{"match_all":{}}],"must_not":[],"should":[]}},"from":0,"size":15000,"sort":[],"aggs":{}}
    es_result = es.search(index = GROUP_INFORMATION,doc_type = "text",body = query_body)["hits"]["hits"]
    for k,v in enumerate(es_result):
        group_dict[v["_source"]["group_id"]] = v["_source"]["userlist"]

    return group_dict


def domain_topic_static(group_dict,timestamp):  
    
    for k in group_dict:
        topic_list = []
        domain_list = []
        domain_dict = {j:0 for j in labels}
        topic_dict = {i:0 for i in TOPIC_LIST}

        for uid in group_dict[k]:
            query_body = {
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                        "term": {
                                        "uid": uid
                                        }
                                        },
                                        {
                                        "term": {
                                        "timestamp": timestamp
                                        }
                                        }
                                    ],
                            "must_not": [ ],
                            "should": [ ]
                            }
                        }
                    }
            es_result = es.search(index = USER_DOMAIN_TOPIC, doc_type = "text",body = query_body)["hits"]["hits"]
            
            ##########domain and topic
            if es_result != [] :
                # print 1
                domain_dict[es_result[0]["_source"]["main_domain"]] += 1


                for j in topic_dict:
                    if j not in ["anti-corruption","fear-of-violence","social-security"]:
                        topic_dict[j] += es_result[0]["_source"]["topic_"+j]
                    elif j=="anti-corruption":
                        topic_dict[j] += es_result[0]["_source"]["topic_anti_corruption"]

                    elif j== "fear-of-violence":
                        topic_dict[j] += es_result[0]["_source"]["topic_violence"]
                    elif j=="social-security":
                        topic_dict[j] += es_result[0]["_source"]["topic_social_security"]
            else:
                    domain_dict["other"] += 1
                    topic_dict["life"] += 1


        for domain in domain_dict:
            domain_list.append({"domain":domain,"count":domain_dict[domain]})
        for topic in topic_dict:
            topic_list.append({"topic":topic,"count":topic_dict[topic]/len(group_dict[k])})
        
        es.index(index=GROUP_DOMAIN_TOPIC ,doc_type="text" ,id=str(k)+"_"+str(timestamp) ,body= {
            "date":ts2date(float(timestamp)),
            "timestamp":timestamp,
            "group_id":k,
            "domain_static":domain_list,
            "topic_static":topic_list
            })


def group_word_static(group_dict,timestamp):
    for group_id in group_dict:
        # print (i)
        hastags_list = []
        keywords_list = []
        sensitive_words_list = []

        for uid in group_dict[group_id]:
            query_body = {
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                        "term": {
                                        "uid": uid
                                        }
                                        },
                                        {
                                        "term": {
                                        "timestamp": timestamp
                                        }
                                        }
                                    ],
                            "must_not": [ ],
                            "should": [ ]
                            }
                        }
                    }
            es_result = es.search(index = USER_TEXT_ANALYSIS_STA, doc_type="text",body=query_body)["hits"]["hits"]
            if es_result != []:
                for i in es_result[0]["_source"]["hastags"]:
                    hastags_list.extend(es_result[0]["_source"]["hastags"])
                    keywords_list.extend(es_result[0]["_source"]["keywords"])
                    sensitive_words_list.extend(es_result[0]["_source"]["sensitive_words"])
            else:
                pass

        hastags_dict = {j["hastag"]:0 for j in hastags_list}
        for h in hastags_list:
            hastags_dict[h["hastag"]] += h["count"]

        keywords_dict = {j["keyword"]:0 for j in keywords_list}
        for h in keywords_list:
            keywords_dict[h["keyword"]] += h["count"]

        sensitive_words_dict = {j["sensitive_word"]:0 for j in sensitive_words_list}
        for h in sensitive_words_list:
            sensitive_words_dict[h["sensitive_word"]] += h["count"]

        hastags_dict = dict(sorted(hastags_dict.items(), key=lambda d: d[1], reverse=True)[:50])
        keywords_dict = dict(sorted(keywords_dict.items(), key=lambda d: d[1], reverse=True)[:50])
        sensitive_words_dict =dict(sorted(sensitive_words_dict.items(), key=lambda d: d[1], reverse=True)[:50])

        hastag_result =  [{"hastag": h,"count": hastags_dict[h]} for h in hastags_dict]
        sensitive_word_result =  [{"sensitive_word": h,"count": sensitive_words_dict[h]} for h in sensitive_words_dict]
        keyword_result =  [{"keyword": h,"count": keywords_dict[h]} for h in keywords_dict]


        es.index(index=GROUP_TEXT_ANALYSIS_STA,doc_type="text" ,id=str(group_id)+"_"+str(timestamp) ,body= {
            "date":ts2date(float(timestamp)),
            "timestamp":timestamp,
            "group_id":group_id,
            "keywords":keyword_result,
            "hastags":hastag_result,
            "sensitive_words":sensitive_word_result
            })


if __name__ == '__main__':
    group_dict =  get_group_dict()
    domain_topic_static(group_dict,"1480176000")
    group_word_static(group_dict,"1480176000")