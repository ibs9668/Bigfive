import json
import re
import time
from collections import OrderedDict
from elasticsearch.helpers import scan
from xpinyin import Pinyin

from bigfive.config import *
from bigfive.cache import cache
from bigfive.time_utils import *


def get_hot_event_list(keyword, page, size, order_name, order_type):
    query = {"query": {"bool": {"must": [], "must_not": [], "should": []}}, "from": 0, "size": 10, "sort": [], "aggs": {}}
    page = page if page else '1'
    size = size if size else '10'
    order_name = 'event_name' if order_name == 'name' else order_name
    order_name = order_name if order_name else 'event_name'
    order_type = order_type if order_type else 'asc'
    query['sort'] += [{order_name: {"order": order_type}}]
    query['from'] = str((int(page) - 1) * int(size))
    query['size'] = str(size)
    if keyword:
        query['query']['bool']['should'] += [{"wildcard":{"event_name": "*{}*".format(keyword)}},{"match":{"keywords": "{}".format(keyword)}}]
    print(query)
    hits = es.search(index='event_information', doc_type='text', body=query)['hits']

    result = {'rows': [], 'total': hits['total']}
    for item in hits['hits']:
        try:
            del item['_source']['userlist']
        except:
            pass
        item['_source']['name'] = item['_source']['event_name']
        result['rows'].append(item['_source'])
    return result


def post_create_hot_event(event_name, keywords, location, start_date, end_date):
    event_pinyin = Pinyin().get_pinyin(event_name, '')
    create_date = time.strftime('%Y-%m-%d', time.localtime(int(time.time())))
    create_time = int(time.mktime(time.strptime(create_date, '%Y-%m-%d')))
    progress = 1
    event_id = '{}_{}'.format(event_pinyin, str(create_time))
    hot_event = {
        "event_name": event_name,
        "event_pinyin": event_pinyin,
        "create_time": create_time,
        "create_date": create_date,
        "keywords": keywords,
        "progress": progress,
        "event_id": event_id,
        "location": location,
        "start_date": start_date,
        "end_date": end_date
    }
    es.index(index='event_information', doc_type='text', body=hot_event, id=event_id)
def post_delete_hot_event(event_id):
    es.delete(index='event_information', doc_type='text', id=event_id)

def get_time_hot(event_id,s, e):
    if not s or not e:
        e = today()
        s = get_before_date(30)
    query = {"query": {"bool": {"must": [{"range": {"date": {"gte": s, "lte": e}}},{"term":{"event_id":event_id}}], "must_not": [
    ], "should": []}}, "from": 0, "size": 1000, "sort": [{"date": {"order": "asc"}}], "aggs": {}}
    hits = es.search(index='event_message_type',
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return {}
    # 1 原创 2评论 3转发 time 时间列表
    # 正常来说每个列表长度相等
    result = {'1': [], '2': [], '3': [], 'time': []}

    for hit in hits:
        item = hit['_source']
        result[str(item['message_type'])].append(item['message_count'])
        if item['date'] not in result['time']:
            result['time'].append(item['date'])
    return result


def get_browser_by_date(event_id,date):
    # 按日期查询微博浏览区的微博
    if date:
        # 按具体日期查询,选最新的5条
        st = date2ts(date)
        et = date2ts(get_before_date(-1, date))
        query = {"query": {"bool": {"must": [{"wildcard": {"geo": "中国*"}},{"range": {"timestamp": {"gte": st, "lt": et}}}], "must_not": [
        ], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    else:
        # 全部查询,选最新的5条
        query = {"query": {"bool": {"must": [{"wildcard": {"geo": "中国*"}}], "must_not": [], "should": [
        ]}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    hits = es.search(index='event_'+event_id,
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return []
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result

# @cache.memoize(300)
def get_geo(event_id,geo,s, e):
    # 时间段初始化,为空时查询近30天内的数据
    if not s or not e:
        e = today()
        s = get_before_date(30)
    st = date2ts(s)
    et = date2ts(e)
    query = {"query": {"bool": {"must": [{"wildcard": {"geo": "*{}*".format(geo)}}, {"range": {"timestamp": {"gte": st, "lte": et}}}], "must_not": [], "should": []}}, "from": 0, "size": 100000, "sort": [], "aggs": {}}
    hits = es.search(index='event_'+event_id,
                     doc_type='text', body=query,_source_include=['geo'])['hits']['hits']
    if not hits:
        return {}
    geo_dic = {}
    for hit in hits:
        item = hit['_source']
        geo_list = item['geo'].split('&')
        if len(geo_list) == 1:
            continue
        if len(geo_list) > 1 and geo == '中国':
            # 中国&山西
            city = geo_list[1]
            # 过滤掉类似中国&中山 中山是市
            if city not in MAP_CITIES_DICT.keys():
                continue
        elif len(geo_list) > 2 and geo != '中国':
            # 拿到省名 并过滤掉类似中国&中山 中山是市
            province = geo_list[1]
            if province not in MAP_CITIES_DICT.keys():
                continue
            # 中国&山西&太原
            city = geo_list[2]
            if not city:
                continue
            # 在对应省的城市列表中替换
            for i in MAP_CITIES_DICT[province]:
                if city in i:
                    city=i
                    break
        else:
            continue
        # 过滤名称为中国的
        if city == '中国':
            continue
        if city not in geo_dic:
            geo_dic.update({city: 1})
        else:
            geo_dic[city] += 1
    # 通过省条数排名

    result= {'city':geo_dic,'rank':[]}
    result['rank'] = [{i[0]:i[1]} for i in sorted(geo_dic.items(), key=lambda x: x[1], reverse=True)[:15]]

    return result


def get_emotion_geo(event_id,emotion,geo):
    query = {"query":{"bool":{"must":[{"term":{"emotion":emotion}},{"term":{"event_id":event_id}}],"must_not":[],"should":[]}},"from":0,"size":1000,"sort":[],"aggs":{}}
    hits = es.search(index='event_emotion_geo',doc_type='text',body=query)['hits']['hits']
    result= {'city':{},'rank':[]}
    for hit in hits:
        item = hit['_source']
        geo_dict = item['geo_dict']
        for geo_item in geo_dict:
            count = geo_item['count']
            geo_list = geo_item['geo'].split('&')
            if len(geo_list) == 1:
                continue
            if len(geo_list) > 1 and geo == '中国':
                # 中国&山西
                city = geo_list[1]
                # 过滤掉类似中国&中山 中山是市
                if city not in MAP_CITIES_DICT.keys():
                    continue
            elif len(geo_list) > 2 and geo != '中国':
                # 拿到省名 并过滤掉类似中国&中山 中山是市
                # 过滤掉与查询的省名不符的
                province = geo_list[1]
                if province not in MAP_CITIES_DICT.keys() or province !=geo:
                    continue
                # 中国&山西&太原
                city = geo_list[2]
                if not city:
                    continue
                # 在对应省的城市列表中替换
                for i in MAP_CITIES_DICT[province]:
                    if city in i:
                        city=i
                        break
            else:
                continue
            # 过滤名称为中国的
            if city == '中国':
                continue
            if city not in result['city']:
                result['city'].update({city: count})
            else:
                result['city'][city] += count
    result['rank'] = [{i[0]:i[1]} for i in sorted(result['city'].items(), key=lambda x: x[1], reverse=True)[:15]]
    return result

def get_browser_by_emotion(event_id,emotion):
    query = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {"term": {"sentiment": emotion}},
                        ]}
                }}
        },
        "size": 5,
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    hits = es.search(index='event_'+event_id,doc_type='text', body=query)['hits']['hits']
    if not hits:
        return []
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result
def get_browser_by_geo(event_id,geo, s, e):
    # 时间段初始化
    if not s or not e:
        e = today()
        s = get_before_date(30)
    st = date2ts(s)
    et = date2ts(e)
    # 通过省字段查询
    query = {"query": {"bool": {"must": [{"wildcard": {"geo": "*{}*".format(geo)}}, {"range": {"timestamp": {"gte": st, "lte": et}}}],"must_not": [], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    hits = es.search(index='event_'+event_id,
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return {}
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result

def get_browser_by_user(event_id,uid):
    query = {"query":{"bool":{"must":[],"must_not":[],"should":[]}},"from":0,"size":5,"sort":[{"timestamp": {"order": "desc"}}],"aggs":{}}
    if uid:
        query['query']['bool']['must'].append({"term":{"uid":uid}})
    hits = es.search(index='event_' + event_id,
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return []
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result

def get_user_name(item):
    try:
        r = es.get(index='user_information',doc_type='text',id=item['uid'],_source_include=['username'])
        item.update(r['_source'])
    except:
        pass
    return item
def get_in_group_renge(event_id):
    # 获取表内所有uid
    query = {
        "size": 0,
        "aggs": {
            "uids": {
                "terms": {
                    "field": "uid",
                    "size": 10000
                }
            }
        }
    }
    buckets = es.search(index='event_'+event_id,
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
    personality_index_list = ["machiavellianism_index", "narcissism_index", "psychopathy_index","extroversion_index", "nervousness_index", "openn_index", "agreeableness_index", "conscientiousness_index"]
    personality_label_list = ["machiavellianism_label", "narcissism_label", "psychopathy_label","extroversion_label", "nervousness_label", "openn_label", "agreeableness_label", "conscientiousness_label"]

    # 拼接聚合查询语句 平均值
    for i in personality_index_list:
        query["aggs"].update({i.split("_")[0]: {'avg': {'field': i}}})
    # 各index字段的平均值
    result = es.search(index="user_ranking", doc_type="text",
                       body=query)["aggregations"]

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
    # 拼接聚合语句 条数
    for i in personality_label_list:
        query["aggs"].update({i.split("_")[0]: {'terms': {'field': i}}})
    aggregations = es.search(index="user_ranking", doc_type="text", body=query)[
        "aggregations"]
    map_dic = {0: 'low', 2: 'high'}
    for k, v in aggregations.items():
        # 初始值为0
        result[k].update({'low':0,'high':0})
        for bucket in v['buckets']:
            # print(bucket)
            if bucket['key'] not in map_dic.keys():
                continue
            result[k][map_dic[bucket['key']]] = bucket['doc_count']
    return result


def get_in_group_ranking(event_id,mtype):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "event_id": 'event_'+event_id
                        }
                    }
                ],
                "must_not": [],
                "should": []
            }
        },
        "from": 0,
        "size": 1,
        "sort": [],
        "aggs": {}
    }
    # 通过标签限制字段 不然全查出来 查询微博时比较耗时
    r = es.search(index='event_personality',doc_type='text',body=query,_source_include=['{mtype}_high,{mtype}_low'.format(mtype=mtype)])['hits']['hits']
    if not r:
        return {}
    r = r[0]['_source']
    result = {}
    for k,v in r.items():
        # 跳过date,timestamp等字段
        if 'high' not in k and 'low' not in k:
            result[k] = v
            continue
        # 初始化result
        if k.split('_')[0] not in result.keys():
            result[k.split('_')[0]] = {'high':{},'low':{}}
        for i in v:
            # print(i)
            # 得到总的值
            sum_i = sum([i['doc_count'] for i in v if 'key' in i.keys()])
            # 情绪饼图
            result[k.split('_')[0]][k.split('_')[1]]['emotion'] = {EMOTION_MAP_NUM_CH[i['key']]:i['doc_count']/sum_i for i in v if 'key' in i.keys()}
            # 获取微博,暂时没有限制返回的字段
            if 'mid_list' in i.keys():
                mids = i['mid_list']
                query = {"query":{"bool":{"must":[{"terms":{"mid":mids}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}
                hits = es.search(index='event_'+event_id,doc_type='text',body=query)['hits']['hits']
                result[k.split('_')[0]][k.split('_')[1]]['mblogs'] = [hit['_source'] for hit in hits]
    return result[mtype]


def get_network(event_id):
    result = {'important_users_list': []}
    important_users_list = es.get(index='event_information', doc_type='text', id=event_id)['_source']['userlist_important']
    for uid in important_users_list[:5]:
        user_item = es.get(index='user_information', doc_type='text', id=uid)['_source']
        result['important_users_list'].append(user_item)

    message_type = 3
    key = 'target'

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
                                    'target': important_users_list
                                }
                            },
                            {
                                "terms": {
                                    'source': important_users_list
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
        if c not in link and c['source'] != c['target']:
            link.append(c)
            if a not in node:
                node.append(a)
            if b not in node:
                node.append(b)
    transmit_net = {'node': list(node), 'link': link}
    result['transmit_net'] = transmit_net
    return result


def get_emotion_trend(event_id):
    query = {"query": {"bool": {"must": [{"term": {"event_id": event_id}}]}}, "from": 0, "size": 1000, "sort": [{"date": {"order": "asc"}}]}
    emotion_result = es.search(index='event_emotion', doc_type='text', body=query)['hits']['hits']
    if emotion_result:
        result = {
            'nuetral': [],
            'positive': [],
            'angry': [],
            'sad': [],
            'hate': [],
            'negtive': [],
            'anxiety': [],
            'time': []
        }
        for i in emotion_result:
            for k, v in i['_source'].items():
                print(k, v)
                if k in result:
                    result[k].append(v)
                if k == 'date':
                    result['time'].append(v)
    else:
        result = {}
    return result


def get_semantic(event_id):
    result = {'keywords': {}}
    keywords_list = es.get(index='event_wordcloud', id=event_id, doc_type='text')['_source']['keywords']
    keywords_item = {}
    print(len(keywords_list))
    for keyword in keywords_list:
        keywords_item[keyword['keyword']] = keyword['count']
    keywords_item_sorted = sorted(keywords_item.items(), key=lambda x:x[1], reverse=True)[0:200]
    for i in keywords_item_sorted:
        result['keywords'][i[0]] = i[1]
    river_result = es.get(index='event_river', doc_type='text', id=event_id)['_source']
    cluster_count = json.loads(river_result['cluster_count'])
    cluster_word = json.loads(river_result['cluster_word'])
    river_dict = {
        'time': []
    }
    for k1, v1 in cluster_count.items():
        river_dict['time'].append(k1)
        # print(k1, v1)
    # print(cluster_count)
        for k2, v2 in v1.items():
            # print(k2, v2)
            title_str = ''
            title_list = cluster_word[str(k2)]
            for title in title_list[0:3]:
                title_str += (title + '&')
            # print(title_str, v2)
            river_dict.setdefault(title_str.rstrip('&'), [])
            river_dict[title_str.rstrip('&')].append(v2)
    #         river_list.append([k1, v2, title_str.rstrip('&')])
    # print(cluster_word)
    result['river_dict'] = river_dict
    return result
