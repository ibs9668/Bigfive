# -*- coding: utf-8 -*-

import json
import time
from collections import Counter
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from bigfive.person.utils import es, user_emotion, user_social_contact, user_preference, portrait_table, \
    delete_by_id, get_influence_feature, get_user_activity, get_preference_identity, get_basic_info

mod = Blueprint('person', __name__, url_prefix='/person')


@mod.route('/test/')
def test():
    result = 'This is person!'
    return json.dumps(result, ensure_ascii=False)


# portrait表格
@mod.route('/portrait/', methods=['POST'])
def return_portrait_table():
    # keyword = request.args.get("keyword", default='').lower()
    # page = request.args.get('page', default='1')
    # size = request.args.get('size', default='10')
    #
    # order_name = request.args.get('order_name', default='username')
    # order_type = request.args.get('order_type', default='asc')
    #
    # sensitive_index = request.args.get('sensitive_index', default='')
    # machiavellianism_index = request.args.get('machiavellianism_index', default=0)
    # narcissism_index = request.args.get('narcissism_index', default=0)
    # psychopathy_index = request.args.get('psychopathy_index', default=0)
    # extroversion_index = request.args.get('extroversion_index', default=0)
    # nervousness_index = request.args.get('nervousness_index', default=0)
    # openn_index = request.args.get('openn_index', default=0)
    # agreeableness_index = request.args.get('agreeableness_index', default=0)
    # conscientiousness_index = request.args.get('conscientiousness_index', default=0)
    # print(request.json())
    # parameters = json.loads(request.json())
    keyword = request.json.get('keyword')
    page = request.json.get('page')
    size = request.json.get('size')
    order_dict = request.json.get('order_dict')
    sensitive_index = request.json.get('sensitive_index')
    machiavellianism_index = request.json.get('machiavellianism_index')
    narcissism_index = request.json.get('narcissism_index')
    psychopathy_index = request.json.get('psychopathy_index')
    extroversion_index = request.json.get('extroversion_index')
    nervousness_index = request.json.get('nervousness_index')
    openn_index = request.json.get('openn_index')
    agreeableness_index = request.json.get('agreeableness_index')
    conscientiousness_index = request.json.get('conscientiousness_index')
    order_name = request.json.get('order_name')
    order_type = request.json.get('order_type')

    result = portrait_table(keyword, page, size, order_name, order_type, sensitive_index, machiavellianism_index, narcissism_index, psychopathy_index, extroversion_index, nervousness_index, openn_index, agreeableness_index, conscientiousness_index, order_dict)

    return json.dumps(result, ensure_ascii=False)


# 根据uid删除一条记录
@mod.route('/delete_user/', methods=['POST'])
def delete_user():
    uid = request.json.get('person_id')
    result = es.delete(index='user_ranking', doc_type='text', id=uid)
    # return json.dumps(result, ensure_ascii=False)
    return jsonify(1)


@mod.route('/basic_info/', methods=['POST'])
def basic_info():
    uid = request.args.get('person_id')
    result = get_basic_info(uid)
    return json.dumps(result, ensure_ascii=False)


# 活动特征
@mod.route('/person_activity', methods=['POST', 'GET'])
def user_activity():
    uid = request.args.get('person_id')
    result = get_user_activity(uid)
    return json.dumps(result, ensure_ascii=False)


@mod.route('/preference_identity', methods=['POST', 'GET'])
def preference_identity():
    uid = request.args.get('person_id')
    result = get_preference_identity(uid)
    return json.dumps(result, ensure_ascii=False)


# 影响力特征
@mod.route('/influence_feature', methods=['POST', 'GET'])
def influence_feature():
    uid = request.args.get('person_id')
    result = get_influence_feature(uid)
    return json.dumps(result, ensure_ascii=False)


@mod.route('/person_personality', methods=['POST', 'GET'])
def user_personality():
    uid = request.args.get("person_id")

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


# @mod.route('/person_activity', methods=['POST', 'GET'])  # 1098650354
# def user_activity():
#     uid = request.args.get("person_id")
#
#     day = datetime.today().date() - timedelta(days=6)
#     ts = int(time.mktime(time.strptime(str(day), '%Y-%m-%d')))
#
#     query_body = {
#         "query": {
#             "bool": {
#                 "must": [{
#                     "range": {
#                         "timestamp": {
#                             "gt": ts,
#                             "lt": int(time.time())
#                         }
#                     }
#                 },
#                     {
#                         "term": {"uid": uid}
#                     }
#                 ]
#             }
#         }
#     }
#     activity_table = es.search(index='user_activity', doc_type='text', body=query_body)['hits']['hits']
#     activity_lst = [i["_source"] for i in activity_table]
#
#     geo_lst = [i["_source"]["location"].split("&")[1] for i in activity_table]
#     geo_dict = dict(Counter(geo_lst))
#
#     query_body2 = {
#         "query": {
#             "bool": {
#                 "must": {
#                     "term": {"uid": uid}
#                 }
#             }
#         }
#     }
#     source_location = \
#         es.search(index='user_information', doc_type='text', body=query_body2)['hits']['hits'][0]["_source"][
#             "belong_home"].split(u"国")[1]
#
#     activity_dict = dict()
#     activity_dict["table"] = activity_lst
#     activity_dict["geo_dict"] = geo_dict
#     activity_dict["source_location"] = source_location
#
#     return json.dumps(activity_dict, ensure_ascii=False)


# @mod.route('/perference_identity', methods=['POST', 'GET'])
# def perference_identity():
#     uid = request.args.get('person_id')
#     user_inf = user_preference(uid)
#     node = []
#     link = []
#     user_pre_identity = {}
#     main_domain = user_inf["_source"]["main_domain"]
#     for key, value in user_inf["_source"]["domain"].items():
#         link_dict = {}
#         link_dict["source"] = main_domain
#         link_dict["target"] = value
#         link_dict["relation"] = key
#         node.append(value)
#         link.append(link_dict)
#     user_pre_identity["node"] = node
#     user_pre_identity["link"] = link
#     return json.dumps(user_pre_identity, ensure_ascii=False)


@mod.route('/perference_topic', methods=['POST', 'GET'])
def perference_topic():
    uid = request.args.get('person_id')
    user_inf = user_preference(uid)
    topic = user_inf["_source"]["topic"]
    return json.dumps(topic, ensure_ascii=False)


@mod.route('/perference_word', methods=['POST', 'GET'])
def perference_word():
    uid = request.args.get('person_id')
    user_inf = user_preference(uid)
    word = {}
    word['sensitive_words'] = user_inf["_source"]["sensitive_words"]
    word["key_words"] = user_inf["_source"]["key_words"]
    word["micro_words"] = user_inf["_source"]["micro_words"]
    return json.dumps(word, ensure_ascii=False)


@mod.route('/social_contact', methods=['POST', 'GET'])
def social_contact():
    # type 1 2 3 4 转发 被转发 评论 被评论
    uid = request.args.get('person_id')
    map_type = request.args.get("type")
    social_contact = user_social_contact(uid, map_type)
    return jsonify(social_contact)


# @mod.route('/influence_feature', methods=['POST', 'GET'])
# def influence_feature():
#     uid = request.args.get('person_id')
#     user_inf = user_influence(uid)
#     dict_inf = {}
#     time_list = []
#     activity = []
#     sensitivity = []
#     influence = []
#     warning = []
#     for i, _ in enumerate(user_inf):
#         time_list.append(_["_source"]["timestamp"])
#         activity.append(_["_source"]["activity"])
#         sensitivity.append(_["_source"]["sensitivity"])
#         influence.append(_["_source"]["influence"])
#         warning.append(_["_source"]["warning"])
#     dict_inf["time"] = time_list
#     dict_inf["activity_line"] = activity
#     dict_inf["sensitivity_line"] = sensitivity
#     dict_inf["influence_line"] = influence
#     dict_inf["warning_line"] = warning
#
#     return json.dumps(dict_inf, ensure_ascii=False)


@mod.route('/emotion_feature', methods=['POST', 'GET'])
def emotion_feature():
    uid = request.args.get('person_id')
    interval = request.args.get('type','day')
    result = user_emotion(uid,interval)
    return jsonify(result)
