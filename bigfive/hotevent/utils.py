import json
import re
import time
from collections import OrderedDict
from elasticsearch.helpers import scan

from bigfive.config import *
from bigfive.cache import cache
from bigfive.time_utils import *


def get_time_hot(s, e):
    # if not s or not e:
    #     e = today()
    #     s = get_before_date(30)
    query = {"query": {"bool": {"must": [{"range": {"date": {"gte": s, "lte": e}}}], "must_not": [
    ], "should": []}}, "from": 0, "size": 1000, "sort": [{"date": {"order": "asc"}}], "aggs": {}}
    hits = es.search(index='event_message_type',
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return {}
    result = {'1': [], '2': [], '3': [], 'time': []}

    for hit in hits:
        item = hit['_source']
        result[str(item['message_type'])].append(item['message_count'])
        if item['date'] not in result['time']:
            result['time'].append(item['date'])
    return result


def get_browser_by_date(date):
    if date:
        st = date2ts(date)
        et = date2ts(get_before_date(-1, date))
        query = {"query": {"bool": {"must": [{"range": {"timestamp": {"gte": st, "lt": et}}}], "must_not": [
        ], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    else:
        query = {"query": {"bool": {"must": [{"match_all": {}}], "must_not": [], "should": [
        ]}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    hits = es.search(index='event_ceshishijiansan_1551942139',
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return []
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result


def get_geo(s, e):
    if not s or not e:
        e = today()
        s = get_before_date(30)
    st = date2ts(s)
    et = date2ts(e)
    # query= {"query":{"bool":{"must":[{"wildcard":{"geo":"中国*"}}],"must_not":[],"should":[]}},"from":0,"size":5000,"sort":[],"aggs":{}}
    query = {"query": {"bool": {"must": [{"wildcard": {"geo": "中国*"}}, {"range": {"timestamp": {
        "gte": st, "lte": et}}}], "must_not": [], "should": []}}, "from": 0, "size": 5000, "sort": [], "aggs": {}}
    hits = es.search(index='event_ceshishijiansan_1551942139',
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return {}
    result = {}
    for hit in hits:
        item = hit['_source']
        geo_list = item['geo'].split('&')
        if len(geo_list) == 1:
            continue
        if len(geo_list) > 1:
            province = geo_list[1]
        if province == '中国':
            continue
        if province not in result:
            result.update({province: {'count': 1, 'cities': {}}})
        else:
            result[province]['count'] += 1
        if len(geo_list) > 2:
            city = geo_list[2]
            if city not in result[province]['cities']:
                result[province]['cities'].update({city: 1})
            else:
                result[province]['cities'][city] += 1
    result = [{'provice': i[0], 'count':i[1]['count'], 'cities':i[1]['cities']}
              for i in sorted(result.items(), key=lambda x:x[1]['count'], reverse=True)]
    return result


def get_browser_by_geo(geo, s, e):
    if not s or not e:
        e = today()
        s = get_before_date(30)
    st = date2ts(s)
    et = date2ts(e)
    if not geo:
        # query= {"query":{"bool":{"must":[{"wildcard":{"geo":"中国*"}}],"must_not":[],"should":[]}},"from":0,"size":5,"sort":[{"timestamp":{"order":"desc"}}],"aggs":{}}
        query = {"query": {"bool": {"must": [{"wildcard": {"geo": "中国*"}}, {"range": {"timestamp": {"gte": st, "lte": et}}}],
                                    "must_not": [], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    else:
        # query= {"query":{"bool":{"must":[{"wildcard":{"geo":"*{}*".format(geo)}}],"must_not":[],"should":[]}},"from":0,"size":5,"sort":[{"timestamp":{"order":"desc"}}],"aggs":{}}
        query = {"query": {"bool": {"must": [{"wildcard": {"geo": "*{}*".format(geo)}}, {"range": {"timestamp": {"gte": st, "lte": et}}}], "must_not": [
        ], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    hits = es.search(index='event_ceshishijiansan_1551942139',
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return {}
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result


def get_renge():
    query = {
        "size": 0,
        "aggs": {
            "uids": {
                "terms": {
                    "field": "uid",
                    "size": 1000
                }
            }
        }
    }
    buckets = es.search(index='event_ceshishijiansan_1551942139',
                        doc_type='text', body=query)["aggregations"]["uids"]['buckets']
    if not buckets:
        return {}
    uids = [bucket['key'] for bucket in buckets]
    query = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {
                                "terms": {
                                    'uid': uids
                                }
                            }
                        ]}
                }}
        },
        "size": 0,
        "aggs": {
        }
    }
    personality_index_list = ["machiavellianism_index","narcissism_index","psychopathy_index","extroversion_index","nervousness_index","openn_index","agreeableness_index","conscientiousness_index"]
    personality_label_list = ["machiavellianism_label","narcissism_label","psychopathy_label","extroversion_label","nervousness_label","openn_label","agreeableness_label","conscientiousness_label"]

    result =  {}
    for i in personality_index_list:
        query["aggs"].update({i.split("_")[0]:{'avg':{'field':i}}})
    result = es.search(index="user_ranking", doc_type="text", body = query)["aggregations"]

    query = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {
                                "terms": {
                                    'uid': uids
                                }
                            }
                        ]}
                }}
        },
        "size": 0,
        "aggs": {
        }
    }

    for i in personality_label_list:
        query["aggs"].update({i.split("_")[0]:{'terms':{'field':i}}})
    aggregations = es.search(index="user_ranking", doc_type="text", body = query)["aggregations"]
    map_dic = {0:'low',2:'high'}
    for k,v in aggregations.items():
        for bucket in v['buckets']:
            # print(bucket)
            if bucket['key'] not in map_dic.keys():
                continue
            result[k][map_dic[bucket['key']]] = bucket['doc_count']
    return result
