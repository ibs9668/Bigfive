# -*- coding: utf-8 -*-

import json
import time
from collections import Counter
from flask import Blueprint, request
from datetime import datetime, timedelta

from bigfive.person.utils import es, judge_uid_or_nickname, index_to_score_rank, user_emotion, user_influence, \
                                user_social_contact, user_preference

mod = Blueprint('person', __name__, url_prefix='/person')


@mod.route('/test/')
def test():
    result = 'This is person!'
    return json.dumps(result, ensure_ascii=False)


# 进入页面时默认展示的表
@mod.route('/portrait/', methods=['POST', 'GET'])
def default():
    page = request.args.get('page', default='1')  # 当前页页码
    size = request.args.get('size', default='10')  # 每页展示的条数
    order_name = request.args.get('order_name', default='username')
    order_type = request.args.get('order_type', default='asc')

    query = '{"query": {"bool": {"must": [{"match_all": {}}]}}, "from": %s, "size": %s, "sort": [{"%s": {"order": "%s"}}]}' % (
        str((int(page) - 1) * int(size)), str(size), order_name, order_type)
    result = es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']
    print(result)
    return json.dumps([item['_source'] for item in result], ensure_ascii=False)


# 基本搜索
@mod.route('/portrait/basic_search/', methods=['POST', 'GET'])
def basic_search():
    keyword = request.args.get("keyword")
    page = request.args.get('page', default='1')  # 当前页页码
    size = request.args.get('size', default='10')  # 每页展示的条数
    order_name = request.args.get('order_name', default='username')
    order_type = request.args.get('order_type', default='asc')

    query = '{"query": {"bool": {"must": [{"wildcard": {"%s": "%s"}}]}}, "from": %s, "size": %s, "sort": [{"%s": {"order": "%s"}}]}'

    # 判断关键词是昵称还是uid(通过judge_uid_or_nickname函数判断，若为uid返回True，若为昵称返回False)
    # 若为昵称使用"wildcard" : {"username": "*keyword*"}查询
    # 若为uid使用"wildcard" : {"uid": "keyword*"}查询
    query = query % ("uid", keyword + '*', str((int(page) - 1) * int(size)), str(size)) if judge_uid_or_nickname(
        keyword) else query % ("username", '*' + keyword + '*', str((int(page) - 1) * int(size)), str(size), order_name,
                               order_type)
    print(query)

    result = es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']
    print(result)
    return json.dumps([item['_source'] for item in result], ensure_ascii=False)


# 高级搜索
@mod.route('/portrait/advanced_search/', methods=['POST', 'GET'])
def advanced_search():
    keyword = request.args.get("keyword", default='')
    page = request.args.get('page', default='1')
    size = request.args.get('size', default='10')
    order_name = request.args.get('order_name', default='username')
    order_type = request.args.get('order_type', default='asc')

    sensitive_index = request.args.get('sensitive_index', default=True)
    machiavellianism_index = request.args.get('machiavellianism_index', default=-1)
    narcissism_index = request.args.get('narcissism_index', default=-1)
    psychopathy_index = request.args.get('psychopathy_index', default=-1)
    extroversion_index = request.args.get('extroversion_index', default=-1)
    nervousness_index = request.args.get('nervousness_index', default=-1)
    openn_index = request.args.get('openn_index', default=-1)
    agreeableness_index = request.args.get('agreeableness_index', default=-1)
    conscientiousness_index = request.args.get('conscientiousness_index', default=-1)

    machiavellianism_rank = index_to_score_rank(machiavellianism_index)
    narcissism_rank = index_to_score_rank(narcissism_index)
    psychopathy_rank = index_to_score_rank(psychopathy_index)
    extroversion_rank = index_to_score_rank(extroversion_index)
    nervousness_rank = index_to_score_rank(nervousness_index)
    openn_rank = index_to_score_rank(openn_index)
    agreeableness_rank = index_to_score_rank(agreeableness_index)
    conscientiousness_rank = index_to_score_rank(conscientiousness_index)

    sensitive_query = '"gte":60' if sensitive_index else '"lt": 2153321'
    user_query = '"uid": "%s*"' % keyword if judge_uid_or_nickname(keyword) else '"username": "*%s*"' % keyword

    query = r'{"query":{"bool":{"must":[{"range":{"machiavellianism_index":{"gte":"%s","lt":"%s"}}},{"range":{"narcissism_index":{"gte":"%s","lt":"%s"}}},{"range":{"psychopathy_index":{"gte":"%s","lt":"%s"}}},{"range":{"extroversion_index":{"gte":"%s","lt":"%s"}}},{"range":{"nervousness_index":{"gte":"%s","lt":"%s"}}},{"range":{"openn_index":{"gte":"%s","lt":"%s"}}},{"range":{"agreeableness_index":{"gte":"%s","lt":"%s"}}},{"range":{"conscientiousness_index":{"gte":"%s","lt":"%s"}}},{"range":{"sensitive_index":{%s}}},{"wildcard":{%s}}]}},"from":%s,"size":%s,"sort": [{"%s": {"order": "%s"}}]}'
    query = query % (
        machiavellianism_rank[0],
        machiavellianism_rank[1],

        narcissism_rank[0],
        narcissism_rank[1],

        psychopathy_rank[0],
        psychopathy_rank[1],

        extroversion_rank[0],
        extroversion_rank[1],

        nervousness_rank[0],
        nervousness_rank[1],

        openn_rank[0],
        openn_rank[1],

        agreeableness_rank[0],
        agreeableness_rank[1],

        conscientiousness_rank[0],
        conscientiousness_rank[1],

        sensitive_query,
        user_query,

        str((int(page) - 1) * int(size)),
        str(size),

        order_name,
        order_type
    )
    print(query)

    result = es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']
    print(result)
    return json.dumps([item['_source'] for item in result], ensure_ascii=False)


# 根据uid删除一条记录
@mod.route('/delete_user/', methods=['POST'])
def delete_user():
    uid = request.form.get('uid')
    result = es.delete(index='user_ranking', doc_type='text', id=uid)
    return json.dumps(result, ensure_ascii=False)


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
