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
    group_id = '{}_{}'.format(data['group_pinyin'],data['create_time'])
    for k,v in data['create_condition'].items():
        data['create_condition'][k] = int(v)
    # 计算进度 0未完成 1计算中 2完成
    data['progress'] = 0
    # 建立计算任务group_task
    es.index(index='group_task',doc_type='text',id=group_id,body=data)
    return data


def search_group_information(group_name,remark,create_time,page,size,order_name,order,index):
    """通过group名称,备注,创建时间查询"""
    """因为字段基本一样,使用index 用于区分task 和info 表,不再复写该函数"""
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
        query['query']['bool']['must'].append({"wildcard":{"group_name":"*{}*".format(group_name.lower())}})
    # 添加备注查询
    if remark:
        query['query']['bool']['must'].append({"wildcard":{"remark":"*{}*".format(remark.lower())}})
    # 添加时间查询
    if create_time:
        st = date2ts(create_time)
        et = st+86400
        query['query']['bool']['must'].append({"range":{"create_time":{"gt":st,"lt":et}}})
    if index =='task':
        index = 'group_task'
    elif index=='info':
        index = 'group_information'
    r = es.search(index=index,doc_type='text',body=query,_source_include=['group_name,create_time,remark,progress,create_condition'])['hits']['hits']
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
    return {'rows':result,'total':len(result)}

def delete_by_id(index,doc_type,id):
    """通过es的_id删除一条记录"""
    if index =='task':
        index = 'group_task'
    elif index=='info':
        index = 'group_information'
    r = es.delete(index=index,doc_type=doc_type,id=id)
    return r


def search_group_ranking():
    query ={"query":{"bool":{"must":[{"match_all":{}}],"must_not":[],"should":[]}},"from":0,"size":6,"sort":[],"aggs":{}}
    r = es.search(index='group_ranking',doc_type='text',body=query)
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
    return {'rows':result,'total':total}

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

    es_result= es.search(index="group_social_contact", doc_type="text", body=query_body)["hits"]["hits"]#默认取第0条一个用户的最新一条
    social_contact = {}
    if es_result:
        group_inf = es_result[0]
        social_contact["node"] = group_inf["_source"]["node"]
        social_contact["link"] = group_inf["_source"]["link"]
    else:
        social_contact["node"] = []
        social_contact["link"] = []
    return social_contact



if __name__ == '__main__':
    data = {"remark": "某市政府多人涉嫌贪污，目前正接受调查", "create_condition": {"openn_index": 1, "sensitive_index": 3, "extroversion_index": 3, "liveness_index": 2, "conscientiousness_index": 3, "compactness_index": 4,"importance_index": 3, "event": "gangdu", "psychopathy_index":3, "narcissism_index": 4, "machiavellianism_index": 3, "agreeableness_index": 5, "nervousness_index": 1}, "group_name": "政府"}
    r = create_group(data)
    print(r)