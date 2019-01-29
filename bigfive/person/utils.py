# -*- coding: utf-8 -*-
import json
import re

from elasticsearch import Elasticsearch

from bigfive.config import ES_HOST, ES_PORT
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=600)


def judge_uid_or_nickname(keyword):
    return True if re.findall('^\d+$', keyword) else False


def index_to_score_rank(index):
    index_to_score_rank_dict = {
        0: [0, 101],
        1: [0, 20],
        2: [20, 40],
        3: [40, 60],
        4: [60, 80],
        5: [80, 101],
    }
    return index_to_score_rank_dict[int(index)]


def portrait_table(keyword, page, size, order_name, order_type, sensitive_index, machiavellianism_index, narcissism_index, psychopathy_index, extroversion_index, nervousness_index, openn_index, agreeableness_index, conscientiousness_index):

    page = page if page else '1'
    size = size if size else '10'
    order_name = order_name if order_name else 'username'
    order_type = order_type if order_type else 'asc'
    machiavellianism_index = machiavellianism_index if machiavellianism_index else 0
    narcissism_index = narcissism_index if narcissism_index else 0
    psychopathy_index = psychopathy_index if psychopathy_index else 0
    extroversion_index = extroversion_index if extroversion_index else 0
    nervousness_index = nervousness_index if nervousness_index else 0
    openn_index = openn_index if openn_index else 0
    agreeableness_index = agreeableness_index if agreeableness_index else 0
    conscientiousness_index = conscientiousness_index if conscientiousness_index else 0

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
        query['query']['bool']['must'].append({"range": {
            "machiavellianism_index": {"gte": str(machiavellianism_rank[0]), "lt": str(machiavellianism_rank[1])}}})
    if narcissism_index:
        query['query']['bool']['must'].append(
            {"range": {"narcissism_index": {"gte": str(narcissism_rank[0]), "lt": str(narcissism_rank[1])}}})
    if psychopathy_index:
        query['query']['bool']['must'].append(
            {"range": {"psychopathy_index": {"gte": str(psychopathy_rank[0]), "lt": str(psychopathy_rank[1])}}})
    if extroversion_index:
        query['query']['bool']['must'].append(
            {"range": {"extroversion_index": {"gte": str(extroversion_rank[0]), "lt": str(extroversion_rank[1])}}})
    if nervousness_index:
        query['query']['bool']['must'].append(
            {"range": {"nervousness_index": {"gte": str(nervousness_rank[0]), "lt": str(nervousness_rank[1])}}})
    if openn_index:
        query['query']['bool']['must'].append(
            {"range": {"openn_index": {"gte": str(openn_rank[0]), "lt": str(openn_rank[1])}}})
    if agreeableness_index:
        query['query']['bool']['must'].append(
            {"range": {"agreeableness_index": {"gte": str(agreeableness_rank[0]), "lt": str(agreeableness_rank[1])}}})
    if conscientiousness_index:
        query['query']['bool']['must'].append({"range": {
            "conscientiousness_index": {"gte": str(conscientiousness_rank[0]), "lt": str(conscientiousness_rank[1])}}})
    if keyword:
        user_query = '{"wildcard":{"uid": "%s*"}}' % keyword if judge_uid_or_nickname(
            keyword) else '{"wildcard":{"username": "*%s*"}}' % keyword
        query['query']['bool']['must'].append(json.loads(user_query))
    if sensitive_index:
        sensitive_query = '{"range":{"sensitive_index":{"gte":60}}}' if eval(
            sensitive_index) else '{"range":{"sensitive_index":{"lt": 60}}}'
        query['query']['bool']['must'].append(json.loads(sensitive_query))

    total = int(es.count(index='user_ranking', doc_type='text', body=query)['count'])
    query['from'] = str((int(page) - 1) * int(size))
    query['size'] = str(size)
    query['sort'] = [{order_name: {"order": order_type}}]

    result = {'rows': [], 'total': total}
    for item in es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']:
        item['_source']['name'] = item['_source']['username']
        result['rows'].append(item)
    return result


def delete_by_id(index, doc_type, id):
    result = es.delete(index=index, doc_type=doc_type, id=id)
    return result


def user_emotion(user_uid):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term": {
                                    "uid": user_uid

                                }
                            }
                            ]
                        }
                    }
                }
            },
        "size": 1000
    }

    es_result = es.search(index="user_emotion", doc_type="text", body=query_body)["hits"]["hits"]  # 默认取第0条一个用户的最新一条

    return es_result


def user_influence(user_uid):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "uid": user_uid

                                }
                            }
                            ]
                        }
                    }
                }
            },
        "size": 1000
    }

    es_result = es.search(index="user_influence", doc_type="text", body=query_body)["hits"]["hits"]  # 默认取第0条一个用户的最新一条

    return es_result


def user_social_contact(user_uid,map_type):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term": {
                                    "uid": user_uid
                                }
                            },
                                {
                                "term":{
                                    "map_type": map_type
                                }
                            },
                            ]
                        }
                    }
                }
            },
        "size": 1000
    }

    es_result= es.search(index="user_social_contact", doc_type="text", body=query_body)["hits"]["hits"][0]#默认取第0条一个用户的最新一条

    return es_result


def user_preference(user_uid):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term": {
                                    "uid": user_uid

                                }
                            }
                            ]
                        }
                    }
                }
            },
        "size": 1000
    }

    es_result = es.search(index="user_preference", doc_type="text", body=query_body)["hits"]["hits"][0]#默认取第0条一个用户的最新一条
    return es_result

