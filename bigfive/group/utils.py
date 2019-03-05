# coding=utf-8
import json
import re

from bigfive.time_utils import *
from xpinyin import Pinyin

from bigfive.config import es
from bigfive.cache import cache

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
        es.delete(index='group_task', doc_type=doc_type, id=id)
    elif index == 'info':
        es.delete(index='group_ranking', doc_type=doc_type, id=id)


def search_group_ranking(keyword, page, size, order_name, order_type, order_dict):

    page = page if page else '1'
    size = size if size else '10'
    sort_list = []
    if order_dict:
        for order_name, order_type in json.loads(order_dict).items():
            sort_list.append({order_name: {"order": "desc"}}) if order_type else sort_list.append(
                {order_name: {"order": "asc"}})

    order_name = order_name if order_name else 'group_name'
    order_type = order_type if order_type else 'asc'
    sort_list.append({order_name: {"order": order_type}})

    query = {"query": {"bool": {"must": [{"match_all": {}}], "must_not": [{
        "constant_score": {
        "filter": {
        "missing": {
        "field": "extroversion_label"
        }
        }
        }
        }
    ], "should": []}}, "from": 0, "size": 6, "sort": [], "aggs": {}}

    if keyword:
        user_query = '{"wildcard":{"group_id": "*%s*"}}' % keyword
        query['query']['bool']['must'].append(json.loads(user_query))

    query['from'] = str((int(page) - 1) * int(size))
    query['size'] = str(size)
    query['sort'] = sort_list

    r = es.search(index='group_ranking', doc_type='text', body=query)

    total = r['hits']['total']
    # 结果为空
    if not total:
        return {}
    r = r['hits']['hits']
    # 正常返回
    result = []
    for hit in r:

        hit['_source']['big_five_list'] = []
        hit['_source']['dark_list'] = []

        if hit['_source']['extroversion_label'] == 0:
            hit['_source']['big_five_list'].append({'外倾性': '0'})  # 0代表极端低
        if hit['_source']['extroversion_label'] == 2:
            hit['_source']['big_five_list'].append({'外倾性': '1'})  # 1代表极端高
        if hit['_source']['openn_label'] == 0:
            hit['_source']['big_five_list'].append({'开放性': '0'})
        if hit['_source']['openn_label'] == 2:
            hit['_source']['big_five_list'].append({'开放性': '1'})
        if hit['_source']['agreeableness_label'] == 0:
            hit['_source']['big_five_list'].append({'宜人性': '0'})
        if hit['_source']['agreeableness_label'] == 2:
            hit['_source']['big_five_list'].append({'宜人性': '1'})
        if hit['_source']['conscientiousness_label'] == 0:
            hit['_source']['big_five_list'].append({'尽责性': '0'})
        if hit['_source']['conscientiousness_label'] == 2:
            hit['_source']['big_five_list'].append({'尽责性': '1'})
        if hit['_source']['nervousness_label'] == 0:
            hit['_source']['big_five_list'].append({'神经质': '0'})
        if hit['_source']['nervousness_label'] == 2:
            hit['_source']['big_five_list'].append({'神经质': '1'})

        if hit['_source']['machiavellianism_label'] == 0:
            hit['_source']['dark_list'].append({'马基雅维里主义': '0'})
        if hit['_source']['machiavellianism_label'] == 2:
            hit['_source']['dark_list'].append({'马基雅维里主义': '1'})
        if hit['_source']['psychopathy_label'] == 0:
            hit['_source']['dark_list'].append({'精神病态': '0'})
        if hit['_source']['psychopathy_label'] == 2:
            hit['_source']['dark_list'].append({'精神病态': '1'})
        if hit['_source']['narcissism_label'] == 0:
            hit['_source']['dark_list'].append({'自怜': '0'})
        if hit['_source']['narcissism_label'] == 2:
            hit['_source']['dark_list'].append({'自恋': '1'})

        hit['_source']['name'] = hit['_source']['group_name']


        item = hit['_source']
        # 为前端返回es的_id字段,为删除功能做支持
        item['id'] = hit['_id']
        item['name'] = item['group_name']
        result.append(item)
    return {'rows': result, 'total': total}


def get_group_user_list(gid):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "group_id": gid
                        }
                    }
                ]
            }
        }
    }
    result = es.search(index='group_information', doc_type='text', body=query)['hits']['hits'][0]['_source']['userlist']
    return result


def get_group_basic_info(gid, remark):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "group_id": gid
                        }
                    }
                ]
            }
        }
    }
    group_item = {}
    print(query)
    result = es.search(index='group_information', doc_type='text', body=query)['hits']['hits'][0]['_source']
    group_ranking_result = es.search(index='group_ranking', doc_type='text', body=query)['hits']['hits'][0]['_source']
    print(group_ranking_result)
    group_item['machiavellianism'] = group_ranking_result['machiavellianism_index']
    group_item['narcissism'] = group_ranking_result['narcissism_index']
    group_item['psychopathy'] = group_ranking_result['psychopathy_index']

    group_item['extroversion'] = group_ranking_result['extroversion_index']
    group_item['conscientiousness'] = group_ranking_result['conscientiousness_index']
    group_item['agreeableness'] = group_ranking_result['agreeableness_index']
    group_item['openn'] = group_ranking_result['openn_index']
    group_item['nervousness'] = group_ranking_result['nervousness_index']

    group_item['group_name'] = result['group_name']
    group_item['user_count'] = len(result['userlist'])
    group_item['keyword'] = result['keyword']
    group_item['create_time'] = result['create_time']
    group_item['remark'] = result['remark']

    group_item['liveness_star'] = group_ranking_result['liveness_star']
    group_item['importance_star'] = group_ranking_result['importance_star']
    group_item['sensitive_star'] = group_ranking_result['sensitive_star']
    group_item['influence_star'] = group_ranking_result['influence_star']
    group_item['compactness_star'] = group_ranking_result['compactness_star']


    if remark:
        es.update(index='group_information', id=gid, doc_type='text', body={'doc': {'remark': remark}})
    return group_item


def group_preference(group_id):
    query = {"query":{"bool":{"must":[{"term":{"group_id":group_id}}],"must_not":[],"should":[]}},"from":0,"size":1,"sort":[],"aggs":{}}
    hits = es.search(index='group_domain_topic',doc_type='text',body=query)['hits']['hits']
    sta_hits = es.search(index='group_text_analysis_sta', doc_type='text', body=query)['hits']['hits']
    print(query)
    if not hits or not sta_hits:
        return {}

    item = hits[0]['_source']
    domain_static = {one['domain']:one['count'] for one in item['domain_static'] if one['count']}
    topic_static = {one['topic']:one['count'] for one in item['topic_static'] if one['count']}

    sta_item = sta_hits[0]['_source']
    keywords = {one['keyword']:one['count'] for one in sta_item['keywords']}
    hastags = {one['hastag']:one['count'] for one in sta_item['hastags']}
    sensitive_words = {one['sensitive_word']:one['count'] for one in sta_item['sensitive_words']}

    result = {'domain_static':domain_static,'topic_result':topic_static, 'keywords': keywords, 'hastags': hastags, 'sensitive_words': sensitive_words}
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

    es_result = es.search(index="group_influence", doc_type="text", body=query_body)["hits"]["hits"]
    result_list = []
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
        result['time'].append(bucket['key_as_string'], )
        result["positive_line"].append(bucket['positive']['sum'], )
        result["negtive_line"].append(bucket['negtive']['sum'], )
        result["nuetral_line"].append(bucket['nuetral']['sum'])
    return result

@cache.memoize(60)
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
    result = {'one':[],'two':[],'three':[],'four':[]}
    item = hits[0]['_source']
    activity_direction = sorted(item['activity_direction'],key=lambda x:x['count'],reverse=True)[:5]
    for i in activity_direction:
        start_end = i['geo2geo'].split('&')
        result['one'].append({'start':start_end[0],'end':start_end[1],'count':i['count']})

        # s_end

    start_geo_item = {}
    end_geo_item = {}
    route_list = []
    for i in sorted(item['activity_direction'],key=lambda x:x['count'],reverse=True):
        try:
            if i['geo2geo'].split('&')[0].split(' ')[1] == '其他' or i['geo2geo'].split('&')[1].split(' ')[1] == '其他':
                continue
            if i['geo2geo'].split('&')[0].split(' ')[0] != '中国' or i['geo2geo'].split('&')[1].split(' ')[0] != '中国':
                continue
        except:
            continue
        start_geo_item.setdefault(re.sub(r'省|市|内蒙古|壮族|维吾尔族|回族|(自治区)', r'', i['geo2geo'].split('&')[0].split(' ')[1]), 0)
        start_geo_item[re.sub(r'省|市|内蒙古|壮族|维吾尔族|回族|(自治区)', '', i['geo2geo'].split('&')[0].split(' ')[1])] += i['count']
        end_geo_item.setdefault(re.sub(r'省|市|内蒙古|壮族|维吾尔族|回族|(自治区)', '', i['geo2geo'].split('&')[1].split(' ')[1]), 0)
        end_geo_item[re.sub(r'省|市|内蒙古|壮族|维吾尔族|回族|(自治区)', '', i['geo2geo'].split('&')[1].split(' ')[1])] += i['count']
        route_dict = {'s': re.sub(r'省|市|内蒙古|壮族|维吾尔族|回族|(自治区)', '', i['geo2geo'].split('&')[0].split(' ')[1]), 'e': re.sub(r'省|市|内蒙古|壮族|维吾尔族|回族|(自治区)', '', i['geo2geo'].split('&')[1].split(' ')[1])}
        if route_dict not in route_list:
            route_list.append(route_dict)

    geo_item = {}
    for ks,vs in start_geo_item.items():
        for ke, ve in end_geo_item.items():
            if ks == ke:
                geo_item[ks] = vs + ve
                break
    result['two'] = sorted(item['main_start_geo'],key=lambda x:x['count'],reverse=True)[:5]
    result['three'] = sorted(item['main_end_geo'],key=lambda x:x['count'],reverse=True)[:5]
    result['four'] = {'route_list': route_list, 'geo_count': geo_item}
    return result

