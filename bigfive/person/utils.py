# -*- coding: utf-8 -*-

import json
import re
import time

from elasticsearch.helpers import scan

from bigfive.config import es


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


def portrait_table(keyword, page, size, order_name, order_type, sensitive_index, machiavellianism_index,
                   narcissism_index, psychopathy_index, extroversion_index, nervousness_index, openn_index,
                   agreeableness_index, conscientiousness_index):
    page = page if page else '1'
    size = size if size else '10'
    if order_name == 'name':
        order_name = 'username'
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

    query['from'] = str((int(page) - 1) * int(size))
    query['size'] = str(size)
    query['sort'] = [{order_name: {"order": order_type}}]

    hits = es.search(index='user_ranking', doc_type='text', body=query)['hits']

    result = {'rows': [], 'total': hits['total']}
    for item in hits['hits']:
        item['_source']['name'] = item['_source']['username']
        result['rows'].append(item['_source'])
    return result


def delete_by_id(index, doc_type, id):
    result = es.delete(index=index, doc_type=doc_type, id=id)
    return result


def user_emotion(uid, interval):
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "uid": uid
                        }
                    }
                ]
            }
        },
        "from": 0,
        "size": 0,
        "sort": [],
        "aggs": {
            "groupDate": {
                "date_histogram": {
                    "field": "date",
                    "interval": interval,
                    "format": "yyyy-MM-dd"
                },
                "aggs": {
                    "nuetral": {
                        "stats": {
                            "field": "nuetral"
                        }
                    },
                    "negtive": {
                        "stats": {
                            "field": "negtive"
                        }
                    },
                    "positive": {
                        "stats": {
                            "field": "positive"
                        }
                    }
                }
            }
        }
    }

    buckets = es.search(index="user_emotion", doc_type="text", body=query_body)['aggregations']['groupDate']['buckets']
    result = {
        'time': [],
        "positive_line": [],
        "negtive_line": [],
        "nuetral_line": []
    }
    for bucket in buckets:
        result['time'].append(bucket['key_as_string'], )
        result["positive_line"].append(bucket['positive']['sum'], )
        result["negtive_line"].append(bucket['negtive']['sum'], )
        result["nuetral_line"].append(bucket['nuetral']['sum'])
    return result


def get_user_activity(uid):
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    a_week_ago = time.strftime('%Y-%m-%d', time.localtime(time.time() - 7 * 24 * 60 * 60))
    result = {}

    # ip一天排名
    one_day_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "uid": str(uid)
                        }
                    },
                    {
                        "term": {
                            "date": "2016-11-21"
                            # "date": str(today)
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "count": {
                    "order": "desc"
                }
            }
        ]
    }

    one_day_result_list = []
    one_day_rank = 1
    one_day_result = es.search(index='user_activity', doc_type='text', body=one_day_query)['hits']['hits']
    for one_day_data in one_day_result:
        item = {'rank': one_day_rank, 'count': one_day_data['_source']['count'], 'ip': one_day_data['_source']['ip']}
        one_day_result_list.append(item)
        one_day_rank += 1

    # ip一周排名
    one_week_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "uid": str(uid)
                        }
                    },
                    {
                        "range": {
                            "date": {
                                "gte": "2016-11-14",
                                # "gte": a_week_ago,
                                "lte": "2016-11-21"
                                # "lte": today
                            }
                        }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "ip_count": {
                "terms": {
                    "field": "ip"
                },
                "aggs": {
                    "ip_count": {
                        "stats": {
                            "field": "count"
                        }
                    }
                }
            }
        }
    }

    print(one_week_query)
    one_week_result_list = []
    one_week_result = es.search(index='user_activity', doc_type='text', body=one_week_query)['aggregations']['ip_count']['buckets']
    one_week_dic = {}
    for one_week_data in one_week_result:
        one_week_dic[one_week_data['key']] = one_week_data['ip_count']['sum']

    l = sorted(one_week_dic.items(), key=lambda x: x[1], reverse=True)
    for i in range(len(l)):
        item = {'rank': i + 1, 'count': int(l[i][1]), 'ip': l[i][0]}
        one_week_result_list.append(item)

    # 活跃度分析
    geo_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "uid": str(uid)
                        }
                    },
                    {
                        "range": {
                            "date": {
                                "gt": "2016-11-14",
                                "lte": "2016-11-21"
                            }
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "size": 1000,
        "sort": [
            {
                "timestamp": {
                    "order": "asc"
                }
            }
        ]
    }

    geo_result = es.search(index='user_activity', doc_type='text', body=geo_query)['hits']['hits']
    if geo_result:
        geo_dict = {}
        print(geo_query)
        for geo_data in geo_result:
            # item = {}
            # item.setdefault(geo_data['_source']['geo'].split('&')[1], 0)
            # item[geo_data['_source']['geo'].split('&')[1]] += geo_data['_source']['count']
            geo_dict.setdefault(geo_data['_source']['date'], {})
            try:
                if geo_data['_source']['geo'].split('&')[1] == '其他':
                    continue
                geo_dict[geo_data['_source']['date']].setdefault(geo_data['_source']['geo'].split('&')[1], 0)
            except:
                continue
            geo_dict[geo_data['_source']['date']][geo_data['_source']['geo'].split('&')[1]] += geo_data['_source']['count']

        print(geo_dict)
        geo_dict_item = list(geo_dict.items())
        print(geo_dict_item)
        route_list = []
        for i in range(len(geo_dict_item)):
            if not geo_dict_item[i][1]:
                continue
            item = {'s': max(geo_dict_item[i][1], key=geo_dict_item[i][1].get), 'e': ''}
            route_list.append(item)
            print('maxmaxmax', max(geo_dict_item[i][1], key=geo_dict_item[i][1].get))
            if i > 0:
                route_list[i-1]['e'] = max(geo_dict_item[i][1], key=geo_dict_item[i][1].get)

        if len(route_list) > 1:
            del (route_list[-1])
        else:
            route_list[0]['e'] = route_list[0]['s']
        print(route_list)
    else:
        route_list = []

    result['one_day_rank'] = one_day_result_list
    result['one_week_rank'] = one_week_result_list
    result['route_list'] = route_list

    return result


def get_influence_feature(uid):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "uid": str(uid)
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "timestamp": {
                    "order": "asc"
                }
            }
        ],
        "size": 1000
    }
    result_list = []
    es_result = scan(client=es, index='user_influence', doc_type='text', query=query)
    for data in es_result:
        item = {}
        item['sensitivity'] = data['_source']['sensitivity']
        item['influence'] = data['_source']['influence']
        item['activity'] = data['_source']['activity']
        item['importance'] = data['_source']['importance']
        item['timestamp'] = data['_source']['timestamp']
        item['date'] = time.strftime('%Y-%m-%d', time.localtime(item['timestamp']))
        result_list.append(item)

    return result_list


# def user_influence(user_uid):
#     query_body = {
#         "query": {
#                 "filtered": {
#                     "filter": {
#                         "bool": {
#                             "must": [{
#                                 "term":{
#                                     "uid": user_uid
#
#                                 }
#                             }
#                             ]
#                         }
#                     }
#                 }
#             },
#         "size": 1000
#     }
#
#     es_result = es.search(index="user_influence", doc_type="text", body=query_body)["hits"]["hits"]  # 默认取第0条一个用户的最新一条
#
#     return es_result


def user_social_contact(uid, map_type):
    # map_type 1 2 3 4 转发 被转发 评论 被评论
    # message_type 1 原创 2 评论 3转发
    if map_type in ['1', '2']:
        message_type = 3
    else:
        message_type = 2
    if map_type in ['1', '3']:
        key = 'target'
        key2 = 'source'
    else:
        key = 'source'
        key2 = 'target'
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "message_type": message_type
                        }
                    },
                    {
                        "term": {
                            key: uid
                        }
                    }
                ]
            }
        },
        "size": 1000,
    }
    r = []
    r1 = es.search(index="user_social_contact", doc_type="text",
                   body=query_body)["hits"]["hits"]
    node = []
    link = []
    for one in r1:
        item = one['_source']
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "message_type": message_type
                            }
                        },
                        {
                            "term": {
                                key: item[key2]
                            }
                        }
                    ]
                }
            },
            "size": 1000,
        }
        r2 = es.search(index="user_social_contact",
                       doc_type="text", body=query_body)["hits"]["hits"]
        r += r2
    r += r1
    for one in r:
        item = one['_source']
        a = {'id': item['target'], 'name': item['target_name']}
        b = {'id': item['source'], 'name': item['source_name']}
        c = {'source': item['source_name'], 'target': item['target_name']}
        if a not in node:
            node.append(a)
        if b not in node:
            node.append(b)
        if c not in link and c['source'] != c['target']:
            link.append(c)
    social_contact = {'node': node, 'link': link}
    if node:
        return social_contact
    return {}


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

    es_result = es.search(index="user_preference", doc_type="text", body=query_body)["hits"]["hits"][
        0]  # 默认取第0条一个用户的最新一条
    return es_result
