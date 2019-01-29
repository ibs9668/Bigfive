# -*- coding: utf-8 -*-
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

