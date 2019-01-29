# coding=utf-8
from bigfive.config import ES_HOST, ES_PORT
from bigfive.time_utils import nowts,ts2date,date2ts
from elasticsearch import Elasticsearch
from xpinyin import Pinyin
es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
# es = Elasticsearch([{'host': '219.224.134.220', 'port': 9200}], timeout=1000)


def create_group(data):
    """创建组"""
    p = Pinyin()
    data['group_pinyin'] = p.get_pinyin(data['group_name'], '')
    data['create_time'] = nowts()
    data['group_id'] = '{}_{}'.format(data['group_pinyin'],data['create_time'])
    # 获取计算状态,需要完善
    data['state'] = get_state()
    for k,v in data['create_condition'].items():
        if k=='event':
            continue
        data['create_condition'][k] = int(v)

    # 添加符合组条件的用户id到user_lst,注意使用copy
    create_condition = data['create_condition'].copy()
    del create_condition['event']     # 去除下面不用的字段
    query = {"query": {"bool": {"must": []}},"size": 1000,}
    # 1 0-20 2 20-40 3 40-60 4 60-80 5 80-100
    for k,v in create_condition.items():
        one = {"range": {k: {"gte": (v-1)*20,"lt": v*20}}}
        query['query']['bool']['must'].append(one)
    r = es.search(index='user_ranking',doc_type='text',body=query,_source_include=['uid'])['hits']['hits']
    data['user_lst'] = []
    for item in r:
        data['user_lst'].append(item['_source']['uid'])
    # 数据插入
    es.index(index='group_information',doc_type='text',body=data)
    return data

def delete_group(gid):
    """通过es的_id删除一条group,不是group_id"""
    r = es.delete(index='group_information',doc_type='text',id=gid)
    return r

def search_group(group_name,remark,create_time,page,size,order_name,order):
    """通过group名称,备注,创建时间查询"""

    # 判断page的合法性
    if page.isdigit():
        page = int(page)
        if page<=0:
            return {}
    else:
        return {}
    # 基础查询语句
    query = {"query":{"bool":{"must":[],"must_not":[],"should":[]}},"from":(int(page)-1)*int(size),"size":size,"sort":[]}
    if order and order_name:
        query['sort'].append({order_name: {"order": order}})
    # 添加组名查询
    if group_name:
        query['query']['bool']['must'].append({"wildcard":{"group_name":"*{}*".format(group_name)}})
    # 添加备注查询
    if remark:
        query['query']['bool']['must'].append({"wildcard":{"remark":"*{}*".format(remark)}})
    # 添加时间查询
    if create_time:
        t = date2ts(create_time)
        st = date2ts(ts2date(t-86400))
        et = date2ts(ts2date(t+86400))
        query['query']['bool']['must'].append({"range":{"create_time":{"gte":st,"lt":et}}})
    r = es.search(index='group_information',doc_type='text',body=query,_source_include=['group_name,create_time,remark,state,create_condition'])
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
        item['create_time'] = ts2date(item['create_time'])
        result.append(item)
    return {'rows':result,'total':total}

def get_state():
    # 获取插入组之后计算的状态
    return '计算中'

def group_preference(group_id):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "group_id" : group_id

                                }
                            }
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result = es.search(index="group_preference", doc_type="text", body=query_body)["hits"]["hits"][0]#默认取第0条一个用户的最新一条

    return es_result


def group_influence(group_id):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "group_id" : group_id

                                }
                            }
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result = es.search(index="group_influence", doc_type="text", body=query_body)["hits"]["hits"]#默认取第0条一个用户的最新一条

    return es_result


def group_emotion(group_id):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "group_id" : group_id

                                }
                            }
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result = es.search(index="group_emotion", doc_type="text", body=query_body)["hits"]["hits"]#默认取第0条一个用户的最新一条

    return es_result


def group_social_contact(group_id,map_type):
    query_body = {
        "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": [{
                                "term":{
                                    "group_id" : group_id
                                }
                            },
                                {
                                "term":{
                                    "map_type" : map_type
                                }
                            },
                            ]
                        }
                    }
                }
            },
            "size":1000
    }

    es_result= es.search(index="group_social_contact", doc_type="text", body=query_body)["hits"]["hits"][0]#默认取第0条一个用户的最新一条

    return es_result



if __name__ == '__main__':
    data = {"remark": "某市政府多人涉嫌贪污，目前正接受调查", "create_condition": {"openn_index": 1, "sensitive_index": 3, "extroversion_index": 3, "liveness_index": 2, "conscientiousness_index": 3, "compactness_index": 4,"importance_index": 3, "event": "gangdu", "psychopathy_index":3, "narcissism_index": 4, "machiavellianism_index": 3, "agreeableness_index": 5, "nervousness_index": 1}, "group_name": "政府"}
    r = create_group(data)
    print(r)