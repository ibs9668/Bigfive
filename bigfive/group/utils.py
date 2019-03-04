# coding=utf-8

from bigfive.time_utils import *
from xpinyin import Pinyin

from bigfive.config import es


def create_group_task(data):
    """创建组"""
    p = Pinyin()
    data['group_pinyin'] = p.get_pinyin(data['group_name'], '')
    data['create_time'] = nowts()
    data['create_date'] = ts2date(data['create_time'])
    group_id = '{}_{}'.format(data['group_pinyin'], data['create_time'])
    for k, v in data['create_condition'].items():
        data['create_condition'][k] = int(v)
    # 计算进度 0未完成 1计算中 2完成
    data['progress'] = 0
    # 建立计算任务group_task
    es.index(index='group_task', doc_type='text', id=group_id, body=data)
    return data


def search_group_task(group_name, remark, create_time, page, size, order_name, order, index):
    """通过group名称,备注,创建时间查询"""
    """因为字段基本一样,使用index 用于区分task 和info 表,不再复写该函数"""
    # 判断page的合法性
    if page.isdigit():
        page = int(page)
        if page <= 0:
            return {}
    else:
        return {}
    # 基础查询语句
    query = {"query": {"bool": {"must": [], "must_not": [], "should": []}},
             "from": (int(page) - 1) * int(size), "size": size, "sort": []}
    if order and order_name:
        query['sort'].append({order_name: {"order": order}})
    # 添加组名查询
    if group_name:
        query['query']['bool']['should'].append(
            {"wildcard": {"group_name": "*{}*".format(group_name.lower())}})
        query['query']['bool']['should'].append(
            {"wildcard": {"keyword": "*{}*".format(group_name.lower())}})
    # 添加备注查询
    if remark:
        query['query']['bool']['must'].append(
            {"wildcard": {"remark": "*{}*".format(remark.lower())}})
    # 添加时间查询
    if create_time:
        # 转换前端传的日期为时间戳
        st = date2ts(create_time)
        et = st + 86400
        query['query']['bool']['must'].append(
            {"range": {"create_time": {"gt": st, "lt": et}}})
    if index == 'task':
        index = 'group_task'
    elif index == 'info':
        index = 'group_information'
    else:
        raise ValueError("index is error!")
    r = es.search(index=index, doc_type='text', body=query, _source_include=[
                  'group_name,create_time,remark,keyword,progress,create_condition'])['hits']['hits']
    # 结果为空
    if not r:
        return {}
    # 正常返回
    result = []
    for hit in r:
        item = hit['_source']
        # 为前端返回es的_id字段,为删除功能做支持
        item['id'] = hit['_id']
        item['create_time'] = ts2date(item['create_time'])
        result.append(item)
    return {'rows': result, 'total': len(result)}


def delete_by_id(index, doc_type, id):
    """通过es的_id删除一条记录"""
    if index == 'task':
        r = es.get(index='group_task', doc_type=doc_type, id=id)
        if r['_source']['progress'] != 0:
            raise ValueError('progress is not 0')
    elif index == 'info':
        es.delete(index='group_information', doc_type=doc_type, id=id)
    es.delete(index='group_task', doc_type=doc_type, id=id)
    return r2


def search_group_ranking():
    query = {"query": {"bool": {"must": [{"match_all": {}}], "must_not": [
    ], "should": []}}, "from": 0, "size": 6, "sort": [], "aggs": {}}
    r = es.search(index='group_ranking', doc_type='text', body=query)
    total = r['hits']['total']
    # 结果为空
    if not total:
        return {}
    r = r['hits']['hits']
    # 正常返回
    result = []
    for hit in r:
        item = hit['_source']
        # 为前端返回es的_id字段,为删除功能做支持
        item['id'] = hit['_id']
        item['name'] = item['group_name']
        result.append(item)
    return {'rows': result, 'total': total}


def group_preference(group_id):
    query = {"query":{"bool":{"must":[{"term":{"group_id":group_id}}],"must_not":[],"should":[]}},"from":0,"size":1,"sort":[],"aggs":{}}
    hits = es.search(index='group_domain_topic',doc_type='text',body=query)['hits']['hits']
    if not hits:
        return {}

    item = hits[0]['_source']
    domain_static = {one['domain']:one['count'] for one in item['domain_static'] if one['count']}
    topic_static = {one['topic']:one['count'] for one in item['topic_static'] if one['count']}
    result = {'domain_static':domain_static,'topic_static':topic_static}
    return result


def group_influence(group_id):
    query_body = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [{
                            "term": {
                                "group_id": group_id

                            }
                        }
                        ]
                    }
                }
            }
        },
        "size": 1000
    }

    es_result = es.search(index="group_influence", doc_type="text", body=query_body)[
        "hits"]["hits"]  # 默认取第0条一个用户的最新一条

    return es_result


def group_emotion(group_id, interval):
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "group_id": group_id
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

    buckets = es.search(index="group_emotion", doc_type="text", body=query_body)[
        'aggregations']['groupDate']['buckets']
    result = {
        'time': [],
        "positive_line": [],
        "negtive_line": [],
        "nuetral_line": []
    }
    for bucket in buckets:
        result['time'].append(bucket['key_as_string'],)
        result["positive_line"].append(bucket['positive']['sum'],)
        result["negtive_line"].append(bucket['negtive']['sum'],)
        result["nuetral_line"].append(bucket['nuetral']['sum'])
    return result


def group_social_contact(group_id, map_type):
    user_list = es.get(index='group_information', doc_type='text', id=group_id)[
        '_source']['userlist']
    if map_type in ['1', '2']:
        message_type = 3
    else:
        message_type = 2
    if map_type in ['1', '3']:
        key = 'target'
    else:
        key = 'source'
    query_body = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "message_type": message_type
                                }
                            },
                            {
                                "terms": {
                                    key: user_list
                                }
                            }
                        ]}
                }}
        },
        "size": 3000,
    }
    r = es.search(index="user_social_contact", doc_type="text",
                  body=query_body)["hits"]["hits"]
    node = []
    link = []
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

def get_group_activity(group_id):
    query = {"query":{"bool":{"must":[{"term":{"group_id":group_id}}],"must_not":[],"should":[]}},"from":0,"size":1,"sort":[],"aggs":{}}
    hits = es.search(index='group_activity',doc_type='text',body=query)['hits']['hits']
    if not hits:
        return {}
    return hits