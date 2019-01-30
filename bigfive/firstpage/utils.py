# -*- coding: utf-8 -*-
import json

from elasticsearch import Elasticsearch

from bigfive.config import ES_HOST, ES_PORT
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=600)


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
