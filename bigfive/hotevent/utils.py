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


def get_time_hot(s, e):
    if not s or not e:
        e = today()
        s = get_before_date(30)
    query = {"query": {"bool": {"must": [{"range": {"date": {"gte": s, "lte": e}}}], "must_not": [
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


def get_browser_by_date(date):
    # 按日期查询微博浏览区的微博
    if date:
        # 按具体日期查询,选最新的5条
        st = date2ts(date)
        et = date2ts(get_before_date(-1, date))
        query = {"query": {"bool": {"must": [{"range": {"timestamp": {"gte": st, "lt": et}}}], "must_not": [
        ], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    else:
        # 全部查询,选最新的5条
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

# @cache.memoize(300)
def get_geo(s, e,geo):
    # 时间段初始化,为空时查询近30天内的数据
    if not s or not e:
        e = today()
        s = get_before_date(30)
    st = date2ts(s)
    et = date2ts(e)
    query = {"query": {"bool": {"must": [{"wildcard": {"geo": "*{}*".format(geo)}}, {"range": {"timestamp": {"gte": st, "lte": et}}}], "must_not": [], "should": []}}, "from": 0, "size": 100000, "sort": [], "aggs": {}}
    hits = es.search(index='event_ceshishijiansan_1551942139',
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
            city = geo_list[1]
        elif len(geo_list) > 2 and geo != '中国':
            city = geo_list[2]
            if city in ["延边朝鲜族","恩施土家族苗族","湘西土家族苗族","阿坝藏族羌族","甘孜藏族","凉山彝族","黔东南苗族侗族","楚雄彝族","红河哈尼族彝族","文山壮族苗族","西双版纳傣族","大理白族","大理白族","德宏傣族景颇族","怒江傈僳族","迪庆藏族","临夏回族","甘南藏族","海北藏族","黄南藏族","海南藏族","果洛藏族","玉树藏族","海西蒙古族藏族","昌吉回族","博尔塔拉蒙古","巴音郭楞蒙古","伊犁哈萨克",]:
                city += '自治州'
            elif city in ["大兴安岭","铜仁","毕节","昌都","山南","日喀则","那曲","林芝","海东","吐鲁番","哈密","阿克苏","喀什","和田","塔城","阿勒泰"]:
                city += '地区'
            else:
                city += '市'
        else:
            continue
        if city in ['中国','中山']:
            continue
        if city not in geo_dic:
            geo_dic.update({city: 1})
        else:
            geo_dic[city] += 1
    # 通过省条数排名

    result= {'city':geo_dic,'rank':[]}
    for i in sorted(geo_dic.items(), key=lambda x: x[1], reverse=True)[:15]:
        result['rank'].append({i[0]:i[1]})

    return result


def get_browser_by_geo(geo, s, e):
    # 时间段初始化
    if not s or not e:
        e = today()
        s = get_before_date(30)
    st = date2ts(s)
    et = date2ts(e)
    if not geo:
        # 全查询
        query = {
            "query": {"bool": {"must": [{"wildcard": {"geo": "中国*"}}, {"range": {"timestamp": {"gte": st, "lte": et}}}],"must_not": [], "should": []}}, "from": 0, "size": 5,
            "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    else:
        # 通过省字段查询
        query = {"query": {"bool": {
            "must": [{"wildcard": {"geo": "*{}*".format(geo)}}, {"range": {"timestamp": {"gte": st, "lte": et}}}],"must_not": [], "should": []}}, "from": 0, "size": 5, "sort": [{"timestamp": {"order": "desc"}}], "aggs": {}}
    hits = es.search(index='event_ceshishijiansan_1551942139',
                     doc_type='text', body=query)['hits']['hits']
    if not hits:
        return {}
    result = []
    for hit in hits:
        item = hit['_source']
        result.append(item)
    return result


def get_in_group_renge():
    # 获取表内所有uid
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
                            "event_id": event_id
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
    r = es.search(index='event_personality',doc_type='text',body=query,_source_include=['{mtype}_high,{mtype}_low'.format(mtype=mtype)])['hits']['hits'][0]['_source']
    # 情绪映射
    emotion_map = {
    '0':'中性', '1':'积极', '2':'生气', '3':'焦虑', '4':'悲伤', '5':'厌恶', '6':'消极其他'
    }
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
            result[k.split('_')[0]][k.split('_')[1]]['emotion'] = {emotion_map[i['key']]:i['doc_count']/sum_i for i in v if 'key' in i.keys()}
            # 获取微博,暂时没有限制字段
            if 'mid_list' in i.keys():
                mids = i['mid_list']
                query = {"query":{"bool":{"must":[{"terms":{"mid":mids}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}
                hits = es.search(index='event_ceshishijiansan_1551942139',doc_type='text',body=query)['hits']['hits']
                result[k.split('_')[0]][k.split('_')[1]]['mblogs'] = [hit['_source'] for hit in hits]
    return result[mtype]


def get_semantic(event_id):
    result = {'keywords': {}}
    keywords_list = es.get(index='event_wordcloud', id=event_id, doc_type='text')['_source']['keywords']
    keywords_item = {}
    for keyword in keywords_list:
        keywords_item[keyword['keyword']] = keyword['count']
    keywords_item_sorted = sorted(keywords_item.items(), key=lambda x:x[1], reverse=True)[0:50]
    for i in keywords_item_sorted:
        result['keywords'][i[0]] = i[1]
    river_result = es.get(index='event_river', doc_type='text', id=event_id)['_source']
    cluster_count = json.loads(river_result['cluster_count'])
    cluster_word = json.loads(river_result['cluster_word'])
    river_list = []
    print(cluster_word)
    return result
