# -*- coding: utf-8 -*-

import json
import time
from collections import Counter
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from bigfive.person.utils import es, judge_uid_or_nickname, index_to_score_rank, user_emotion, user_influence, \
    user_social_contact, user_preference, portrait_table

mod = Blueprint('person', __name__, url_prefix='/person')


@mod.route('/test/')
def test():
    result = 'This is person!'
    return json.dumps(result, ensure_ascii=False)


# portrait表格
@mod.route('/portrait/', methods=['POST', 'GET'])
def return_portrait_table():
    keyword = request.args.get("keyword", default='').lower()
    page = request.args.get('page', default='1')
    size = request.args.get('size', default='10')

    order_name = request.args.get('order_name', default='username')
    order_type = request.args.get('order_type', default='asc')

    sensitive_index = request.args.get('sensitive_index', default='')
    machiavellianism_index = request.args.get('machiavellianism_index', default=0)
    narcissism_index = request.args.get('narcissism_index', default=0)
    psychopathy_index = request.args.get('psychopathy_index', default=0)
    extroversion_index = request.args.get('extroversion_index', default=0)
    nervousness_index = request.args.get('nervousness_index', default=0)
    openn_index = request.args.get('openn_index', default=0)
    agreeableness_index = request.args.get('agreeableness_index', default=0)
    conscientiousness_index = request.args.get('conscientiousness_index', default=0)

    result = portrait_table(keyword, page, size, order_name, order_type, sensitive_index, machiavellianism_index, narcissism_index, psychopathy_index, extroversion_index, nervousness_index, openn_index, agreeableness_index, conscientiousness_index)

    if conscientiousness_index == '':
        conscientiousness_index = 0

    machiavellianism_rank = index_to_score_rank(machiavellianism_index)
    narcissism_rank = index_to_score_rank(narcissism_index)
    psychopathy_rank = index_to_score_rank(psychopathy_index)
    extroversion_rank = index_to_score_rank(extroversion_index)
    nervousness_rank = index_to_score_rank(nervousness_index)
    openn_rank = index_to_score_rank(openn_index)
    agreeableness_rank = index_to_score_rank(agreeableness_index)
    conscientiousness_rank = index_to_score_rank(conscientiousness_index)

    query = {"query": {"bool": {"must": []}}}
    if machiavellianism_index:
        query['query']['bool']['must'].append({"range": {"machiavellianism_index": {"gte": str(machiavellianism_rank[0]), "lt": str(machiavellianism_rank[1])}}})
    if narcissism_index:
        query['query']['bool']['must'].append({"range": {"narcissism_index": {"gte": str(narcissism_rank[0]), "lt": str(narcissism_rank[1])}}})
    if psychopathy_index:
        query['query']['bool']['must'].append({"range": {"psychopathy_index": {"gte": str(psychopathy_rank[0]), "lt": str(psychopathy_rank[1])}}})
    if extroversion_index:
        query['query']['bool']['must'].append({"range": {"extroversion_index": {"gte": str(extroversion_rank[0]), "lt": str(extroversion_rank[1])}}})
    if nervousness_index:
        query['query']['bool']['must'].append({"range": {"nervousness_index": {"gte": str(nervousness_rank[0]), "lt": str(nervousness_rank[1])}}})
    if openn_index:
        query['query']['bool']['must'].append({"range": {"openn_index": {"gte": str(openn_rank[0]), "lt": str(openn_rank[1])}}})
    if agreeableness_index:
        query['query']['bool']['must'].append({"range": {"agreeableness_index": {"gte": str(agreeableness_rank[0]), "lt": str(agreeableness_rank[1])}}})
    if conscientiousness_index:
        query['query']['bool']['must'].append({"range": {"conscientiousness_index": {"gte": str(conscientiousness_rank[0]), "lt": str(conscientiousness_rank[1])}}})
    if keyword:
        user_query = '{"wildcard":{"uid": "%s*"}}' % keyword if judge_uid_or_nickname(keyword) else '{"wildcard":{"username": "*%s*"}}' % keyword
        query['query']['bool']['must'].append(json.loads(user_query))
    if sensitive_index:
        sensitive_query = '{"range":{"sensitive_index":{"gte":60}}}' if eval(sensitive_index) else '{"range":{"sensitive_index":{"lt": 60}}}'
        query['query']['bool']['must'].append(json.loads(sensitive_query))

    total = int(es.count(index='user_ranking', doc_type='text', body=query)['count'])
    query['from'] = str((int(page) - 1) * int(size))
    query['size'] = str(size)
    query['sort'] = [{order_name: {"order": order_type}}]
    print(query)
    result = []
    for item in es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']:
        item['_source']['name'] = item['_source']['username']
        result.append(item['_source'])

    result = {'rows': result, 'total': total}
    return json.dumps(result, ensure_ascii=False)


# 根据uid删除一条记录
@mod.route('/delete_user/', methods=['POST'])
def delete_user():
    uid = request.json.get('uid')
    result = es.delete(index='user_ranking', doc_type='text', id=uid)

    # return json.dumps(result, ensure_ascii=False)
    return jsonify(1)

@mod.route('/user_personality', methods=['POST', 'GET'])
def user_personality():
    uid = request.args.get("uid")

    query_body = {
        "query": {
            "bool": {
                "must": {
                    "term": {"uid": uid}
                }
            }
        }
    }
    user_index = es.search(index='user_ranking', doc_type='text', body=query_body)['hits']['hits'][0]["_source"]
    user_information = es.search(index="user_information", doc_type="text", body=query_body)["hits"]["hits"][0][
        "_source"]

    user_dict = dict()
    user_dict["user_index"] = user_index
    user_dict["user_information"] = user_information

    return json.dumps(user_dict, ensure_ascii=False)


@mod.route('/user_activity', methods=['POST', 'GET'])  # 1098650354
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
                            "lt": int(time.time())
                        }
                    }
                },
                    {
                        "term": {"uid": uid}
                    }
                ]
            }
        }
    }
    activity_table = es.search(index='user_activity', doc_type='text', body=query_body)['hits']['hits']
    activity_lst = [i["_source"] for i in activity_table]

    geo_lst = [i["_source"]["location"].split("&")[1] for i in activity_table]
    geo_dict = dict(Counter(geo_lst))

    query_body2 = {
        "query": {
            "bool": {
                "must": {
                    "term": {"uid": uid}
                }
            }
        }
    }
    source_location = \
        es.search(index='user_information', doc_type='text', body=query_body2)['hits']['hits'][0]["_source"][
            "belong_home"].split(u"国")[1]

    activity_dict = dict()
    activity_dict["table"] = activity_lst
    activity_dict["geo_dict"] = geo_dict
    activity_dict["source_location"] = source_location

    return json.dumps(activity_dict, ensure_ascii=False)


@mod.route('/perference_identity', methods=['POST', 'GET'])
def perference_identity():
    uid = request.args.get('uid')
    user_inf = user_preference(uid)
    node = []
    link = []
    user_pre_identity = {}
    main_domain = user_inf["_source"]["main_domain"]
    for key, value in user_inf["_source"]["domain"].items():
        link_dict = {}
        link_dict["source"] = main_domain
        link_dict["target"] = value
        link_dict["relation"] = key
        node.append(value)
        link.append(link_dict)
    user_pre_identity["node"] = node
    user_pre_identity["link"] = link
    return json.dumps(user_pre_identity, ensure_ascii=False)


@mod.route('/perference_topic', methods=['POST', 'GET'])
def perference_topic():
    uid = request.args.get('uid')
    user_inf = user_preference(uid)
    topic = user_inf["_source"]["topic"]
    return json.dumps(topic, ensure_ascii=False)


@mod.route('/perference_word', methods=['POST', 'GET'])
def perference_word():
    uid = request.args.get('uid')
    user_inf = user_preference(uid)
    word = {}
    word['sensitive_words'] = user_inf["_source"]["sensitive_words"]
    word["key_words"] = user_inf["_source"]["key_words"]
    word["micro_words"] = user_inf["_source"]["micro_words"]
    return json.dumps(word, ensure_ascii=False)


@mod.route('/social_contact', methods=['POST', 'GET'])
def social_contact():
    uid = request.args.get('uid')
    map_type = request.args.get("type")
    user_inf = user_social_contact(uid, map_type)

    social_contact = {}
    social_contact["node"] = user_inf["_source"]["node"]
    social_contact["link"] = user_inf["_source"]["link"]

    return json.dumps(social_contact, ensure_ascii=False)


@mod.route('/influence_feature', methods=['POST', 'GET'])
def influence_feature():
    uid = request.args.get('uid')
    user_inf = user_influence(uid)
    dict_inf = {}
    time_list = []
    activity = []
    sensitivity = []
    influence = []
    warning = []
    for i, _ in enumerate(user_inf):
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

    return json.dumps(dict_inf, ensure_ascii=False)


@mod.route('/emotion_feature', methods=['POST', 'GET'])
def emotion_feature():
    uid = request.args.get('uid')

    user_inf = user_emotion(uid)
    nuetral = []
    negtive = []
    positive = []
    time_list = []
    dict_emo = {}
    for i, _ in enumerate(user_inf):
        print(_)
        time_list.append(_["_source"]["timestamp"])
        nuetral.append(_["_source"]["nuetral"])
        negtive.append(_["_source"]["negtive"])
        positive.append(_["_source"]["positive"])
    dict_emo["time"] = time_list
    dict_emo["nuetral_line"] = nuetral
    dict_emo["negtive_line"] = negtive
    dict_emo["positive_line"] = positive

    return json.dumps(dict_emo, ensure_ascii=False)
