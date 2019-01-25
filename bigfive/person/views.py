# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.person.utils import *
from elasticsearch import Elasticsearch
import time
from datetime import datetime, timedelta
from collections import Counter

es = Elasticsearch("219.224.134.220:9200", timeout=600)

mod = Blueprint('person',__name__,url_prefix='/person')

@mod.route('/user_personality',methods=['POST','GET'])
def user_personality():
    uid = request.args.get("uid")

    query_body = {
        "query":{
            "bool":{
                "must":{
                    "term":{"uid":uid}
                }
            }
        }
    }
    user_index = es.search(index = 'user_ranking', doc_type = 'text', body = query_body)['hits']['hits'][0]["_source"]
    user_information = es.search(index = "user_information", doc_type = "text", body = query_body)["hits"]["hits"][0]["_source"]

    user_dict = dict()
    user_dict["user_index"] = user_index
    user_dict["user_information"] = user_information

    return json.dumps(user_dict,ensure_ascii=False)

@mod.route('/user_activity',methods=['POST','GET'])  #  1098650354
def user_activity():
    uid = request.args.get("uid")

    day = datetime.today().date() - timedelta(days=6)
    ts = int(time.mktime(time.strptime(str(day), '%Y-%m-%d')))

    query_body = {
        "query": {
            "bool": {
                "must": [{
                    "range": {
                    "timestamp": {
                    "gt": ts,
                    "lt": int(time.time())                                }
                        }
                    },
                {
                "term": {"uid": uid}
                }
                ]
            }
        }
    }
    activity_table = es.search(index = 'user_activity', doc_type = 'text', body = query_body)['hits']['hits']
    activity_lst = [i["_source"] for i in activity_table]

    geo_lst = [i["_source"]["location"].split("&")[1] for i in activity_table]
    geo_dict = dict(Counter(geo_lst))

    query_body2= {
        "query":{
            "bool":{
                "must":{
                    "term":{"uid":uid}
                }
            }
        }
    }
    source_location = es.search(index = 'user_information', doc_type = 'text', body = query_body2)['hits']['hits'][0]["_source"]["belong_home"].split(u"国")[1]

    activity_dict = dict()
    activity_dict["table"] = activity_lst
    activity_dict["geo_dict"] = geo_dict
    activity_dict["source_location"] = source_location

    return json.dumps(activity_dict,ensure_ascii=False)

def user_preference(user_uid):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "uid" : user_uid

                                }
                            }
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result = es.search(index="user_preference", doc_type="text", body=query_body)["hits"]["hits"][0]#默认取第0条一个用户的最新一条
    return es_result


@mod.route('/test/')
def test():
    result = 'This is person!'
    return json.dumps(result,ensure_ascii=False)


@mod.route('/perference_identity', methods=['POST','GET'])
def perference_identity():
    uid=request.args.get('uid')
    user_inf = user_preference(uid)
    node = []
    link = []
    user_pre_identity = {}
    main_domain = user_inf["_source"]["main_domain"]
    for key,value in user_inf["_source"]["domain"].items():
        link_dict = {}
        link_dict["source"] = main_domain
        link_dict["target"] = value
        link_dict["relation"] = key
        node.append(value)
        link.append(link_dict)
    user_pre_identity["node"] = node
    user_pre_identity["link"] = link
    return json.dumps(user_pre_identity,ensure_ascii=False)

@mod.route('/perference_topic', methods=['POST','GET'])
def perference_topic():
    uid=request.args.get('uid')
    user_inf = user_preference(uid)
    topic = user_inf["_source"]["topic"]
    return json.dumps(topic,ensure_ascii=False)


@mod.route('/perference_word', methods=['POST','GET'])
def perference_word():
    uid=request.args.get('uid')
    user_inf = user_preference(uid)
    word = {}
    word['sensitive_words'] = user_inf["_source"]["sensitive_words"]
    word["key_words"] = user_inf["_source"]["key_words"]
    word["micro_words"] = user_inf["_source"]["micro_words"]
    return json.dumps(word,ensure_ascii=False)

def user_social_contact(user_uid,map_type):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "uid" : user_uid
                                }
                            },
                                {
                                "term":{
                                    "map_type" : map_type
                                }
                            },
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result= es.search(index="user_social_contact", doc_type="text", body=query_body)["hits"]["hits"][0]#默认取第0条一个用户的最新一条

    return es_result

def user_influence(user_uid):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "uid" : user_uid

                                }
                            }
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result = es.search(index="user_influence", doc_type="text", body=query_body)["hits"]["hits"]#默认取第0条一个用户的最新一条

    return es_result

def user_emotion(user_uid):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "uid" : user_uid

                                }
                            }
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result = es.search(index="user_emotion", doc_type="text", body=query_body)["hits"]["hits"]#默认取第0条一个用户的最新一条

    return es_result


@mod.route('/social_contact', methods=['POST','GET'])
def social_contact():
    uid=request.args.get('uid')
    map_type = request.args.get("type")
    user_inf = user_social_contact(uid,map_type)

    social_contact = {}
    social_contact["node"] = user_inf["_source"]["node"]
    social_contact["link"] = user_inf["_source"]["link"]

    return json.dumps(social_contact,ensure_ascii=False)


@mod.route('/influence_feature', methods=['POST','GET'])
def influence_feature():
    uid=request.args.get('uid')
    user_inf = user_influence(uid)
    dict_inf = {}
    time_list = []
    activity = []
    sensitivity = []
    influence = []
    warning = []
    for i ,_ in enumerate(user_inf):
        time_list.append(_["_source"]["timestamp"])
        activity.append(_["_source"]["activity"])
        sensitivity.append(_["_source"]["sensitivity"])
        influence.append(_["_source"]["influence"])
        warning.append(_["_source"]["warning"])
    dict_inf["time"] = time_list
    dict_inf["activity_line"] = activity
    dict_inf["sensitivity_line"] = sensitivity
    dict_inf["influence_line"] = influence
    dict_inf["warning_line"] = warning

    return json.dumps(dict_inf,ensure_ascii=False)


@mod.route('/emotion_feature', methods=['POST','GET'])
def emotion_feature():
    uid=request.args.get('uid')

    user_inf = user_emotion(uid)
    nuetral = []
    negtive = []
    positive =[]
    time_list = []
    dict_emo = {}
    for i ,_ in enumerate(user_inf):
        print(_)
        time_list.append(_["_source"]["timestamp"])
        nuetral.append(_["_source"]["nuetral"])
        negtive.append(_["_source"]["negtive"])
        positive.append(_["_source"]["positive"])
    dict_emo["time"] = time_list
    dict_emo["nuetral_line"] = nuetral
    dict_emo["negtive_line"] = negtive
    dict_emo["positive_line"] = positive

    return json.dumps(dict_emo,ensure_ascii=False)
