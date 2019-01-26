# -*- coding: utf-8 -*-

from flask import Blueprint, request
import json
from .utils import *

mod = Blueprint('person', __name__, url_prefix='/person')


@mod.route('/test/')
def test():
    result = 'This is person!'
    return json.dumps(result, ensure_ascii=False)


# 进入页面时默认展示的表
@mod.route('/portrait/')
def default():
    page = request.args.get('page', default='1')  # 当前页页码
    size = request.args.get('size', default='10')  # 每页展示的条数
    query = '{"query": {"bool": {"must": [{"match_all": {}}]}}, "from": %s, "size": %s}' % (
        str((int(page) - 1) * int(size)), str(size))
    result = es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']
    print(result)
    return json.dumps([item['_source'] for item in result], ensure_ascii=False)


# 基本搜索
@mod.route('/portrait/basic_search/')
def basic_search():
    keyword = request.args.get("keyword")
    page = request.args.get('page', default='1')  # 当前页页码
    size = request.args.get('size', default='10')  # 每页展示的条数
    query = '{"query": {"bool": {"must": [{"wildcard": {"%s": "%s"}}]}}, "from": %s, "size": %s}'

    # 判断关键词是昵称还是uid(通过judge_uid_or_nickname函数判断，若为uid返回True，若为昵称返回False)
    # 若为昵称使用"wildcard" : {"username": "*keyword*"}查询
    # 若为uid使用"wildcard" : {"uid": "keyword*"}查询
    query = query % ("uid", keyword + '*', str((int(page) - 1) * int(size)), str(size)) if judge_uid_or_nickname(
        keyword) else query % ("username", '*' + keyword + '*', str((int(page) - 1) * int(size)), str(size))
    print(query)

    result = es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']
    print(result)
    return json.dumps([item['_source'] for item in result], ensure_ascii=False)


@mod.route('/portrait/advanced_search/')
def advanced_search():
    keyword = request.args.get("keyword", default='')
    page = request.args.get('page', default='1')
    size = request.args.get('size', default='10')

    sensitive_index = request.args.get('sensitive_index', default=True)
    machiavellianism_index = request.args.get('machiavellianism_index', default=-1)
    narcissism_index = request.args.get('narcissism_index', default=-1)
    psychopathy_index = request.args.get('psychopathy_index', default=-1)
    extroversion_index = request.args.get('extroversion_index', default=-1)
    nervousness_index = request.args.get('nervousness_index', default=-1)
    openn_index = request.args.get('openn_index', default=-1)
    agreeableness_index = request.args.get('agreeableness_index', default=-1)
    conscientiousness_index = request.args.get('conscientiousness_index', default=-1)

    machiavellianism_rank = index_to_score_rank(machiavellianism_index)
    narcissism_rank = index_to_score_rank(narcissism_index)
    psychopathy_rank = index_to_score_rank(psychopathy_index)
    extroversion_rank = index_to_score_rank(extroversion_index)
    nervousness_rank = index_to_score_rank(nervousness_index)
    openn_rank = index_to_score_rank(openn_index)
    agreeableness_rank = index_to_score_rank(agreeableness_index)
    conscientiousness_rank = index_to_score_rank(conscientiousness_index)

    sensitive_query = '"gte":60' if sensitive_index else '"lt": 2153321'
    user_query = '"uid": "%s*"' % keyword if judge_uid_or_nickname(keyword) else '"username": "*%s*"' % keyword

    query = r'{"query":{"bool":{"must":[{"range":{"machiavellianism_index":{"gte":"%s","lt":"%s"}}},{"range":{"narcissism_index":{"gte":"%s","lt":"%s"}}},{"range":{"psychopathy_index":{"gte":"%s","lt":"%s"}}},{"range":{"extroversion_index":{"gte":"%s","lt":"%s"}}},{"range":{"nervousness_index":{"gte":"%s","lt":"%s"}}},{"range":{"openn_index":{"gte":"%s","lt":"%s"}}},{"range":{"agreeableness_index":{"gte":"%s","lt":"%s"}}},{"range":{"conscientiousness_index":{"gte":"%s","lt":"%s"}}},{"range":{"sensitive_index":{%s}}},{"wildcard":{%s}}]}},"from":%s,"size":%s}'
    query = query % (
        machiavellianism_rank[0],
        machiavellianism_rank[1],

        narcissism_rank[0],
        narcissism_rank[1],

        psychopathy_rank[0],
        psychopathy_rank[1],

        extroversion_rank[0],
        extroversion_rank[1],

        nervousness_rank[0],
        nervousness_rank[1],

        openn_rank[0],
        openn_rank[1],

        agreeableness_rank[0],
        agreeableness_rank[1],

        conscientiousness_rank[0],
        conscientiousness_rank[1],

        sensitive_query,
        user_query,

        str((int(page) - 1) * int(size)),
        str(size)
    )
    print(query)

    result = es.search(index='user_ranking', doc_type='text', body=query)['hits']['hits']
    print(result)
    return json.dumps([item['_source'] for item in result], ensure_ascii=False)
