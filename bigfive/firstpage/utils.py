# -*- coding: utf-8 -*-
import json

from bigfive.config import es



def search_group(keyword, page, size, order_name, order_type):
    page = page if page else '1'
    size = size if size else '10'
    if order_name == 'name':
        order_name = 'group_name'
    order_name = order_name if order_name else 'group_name'
    order_type = order_type if order_type else 'asc'
    query = {"query": {"bool": {"must": []}}}
    query['from'] = str((int(page) - 1) * int(size))
    query['size'] = str(size)
    query['sort'] = [{order_name: {"order": order_type}}]
    if keyword:
        group_user_query = '{"wildcard":{"group_name": "*%s*"}}' % keyword
        query['query']['bool']['must'].append(json.loads(group_user_query))
    hits = es.search(index='group_ranking', doc_type='text', body=query)['hits']
    result = {'rows': [], 'total': hits['total']}
    for item in hits['hits']:
        item['_source']['name'] = item['_source']['group_name']
        item['_source']['id'] = item['_id']
        result['rows'].append(item['_source'])
    return result


def search_person_and_group(keyword, page, size, person_order_name, group_order_name, person_order_type, group_order_type):
    page = page if page else '1'
    size = size if size else '10'
    person_order_name = person_order_name if person_order_name else 'username'
    group_order_name = group_order_name if group_order_name else 'group_name'
    person_order_type = person_order_type if person_order_type else 'asc'
    group_order_type = group_order_type if group_order_type else 'asc'

    person_query = {"query": {"bool": {"must": []}}}
    group_query = {"query": {"bool": {"must": []}}}
    person_query['from'] = str((int(page) - 1) * int(size))
    person_query['size'] = str(size)
    person_query['sort'] = [{person_order_name: {"order": person_order_type}}]

    group_query['from'] = str((int(page) - 1) * int(size))
    group_query['size'] = str(size)
    group_query['sort'] = [{group_order_name: {"order": group_order_type}}]

    if keyword:
        person_user_query = '{"wildcard":{"username": "*%s*"}}' % keyword
        group_user_query = '{"wildcard":{"group_name": "*%s*"}}' % keyword
        person_query['query']['bool']['must'].append(json.loads(person_user_query))
        group_query['query']['bool']['must'].append(json.loads(group_user_query))

    print(person_query)
    person_result = es.search(index='user_ranking', doc_type='text', body=person_query)['hits']
    group_result = es.search(index='group_ranking', doc_type='text', body=group_query)['hits']

    result = {'person_rows': [], 'person_total': person_result['total'],
              'group_rows': [], 'group_total': group_result['total']}
    for item in person_result['hits']:
        item['_source']['name'] = item['_source']['username']
        result['person_rows'].append(item['_source'])
    for item in group_result['hits']:
        item['_source']['name'] = item['_source']['group_name']
        result['group_rows'].append(item['_source'])

    return result


def get_statistics_user_info(timestamp):
    user_total_count = es.count(index = "user_information",doc_type = "text")["count"]
    print (user_total_count)
    query_body = {"query": {"bool": {"must":[{"term": {"insert_time": timestamp}}]}},"size" : 10000}
    today_insert_user_num = len(es.search(index = "user_information",doc_type = "text",body = query_body)["hits"]["hits"])
    print (today_insert_user_num)
    personality_index_list = ["machiavellianism_index","narcissism_index","psychopathy_index","extroversion_index","nervousness_index","openn_index","agreeableness_index","conscientiousness_index"]
    personality_label_list = ["machiavellianism_label","narcissism_label","psychopathy_label","extroversion_label","nervousness_label","openn_label","agreeableness_label","conscientiousness_label"]
    aggs_avg_dict = {}
    aggs_avg_dict = {"aggs": {"aggs_index": {"avg":{}}}}




    result =  {}
    result["user_total_count"] = user_total_count
    result["today_insert_user_num"] = today_insert_user_num

    for i in personality_index_list:
        aggs_avg_dict["aggs"]["aggs_index"]["avg"]["field"] = i
        result[i.split("_")[0]] = {}
        result[i.split("_")[0]]["value"] = es.search(index="user_ranking", doc_type="text", body = aggs_avg_dict)["aggregations"]["aggs_index"]["value"]

    query_body = {"query": {"bool": {"must":{"term": {}}}},"size" : 10000}
    index_list = [0,2]#0低2高

    for j in personality_label_list:
        for n in index_list:
            query_body["query"]["bool"]["must"]["term"][j] = n
            #print (query_body)
            if int(n) ==0:
                result[j.split("_")[0]]["low"] = len(es.search(index = "user_ranking",doc_type = "text",body = query_body)["hits"]["hits"])
            else:
                result[j.split("_")[0]]["high"] = len(es.search(index = "user_ranking",doc_type = "text",body = query_body)["hits"]["hits"])
            query_body = {"query": {"bool": {"must":{"term": {}}}},"size" : 10000}
    print (result)


    return result


    



