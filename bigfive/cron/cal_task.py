import sys
sys.path.append('../')
from config import *
from time_utils import *

from model.personality_cal import cal_person
from portrait.user.cron_user import user_attribute

from elasticsearch import Elasticsearch,helpers
from elasticsearch.helpers import bulk

def user_ranking(uid,username=None):
    if username == None:
        try:
            username = es.get(index=USER_INFORMATION,doc_type='text',id=uid)['_source']['username']
        except:
            raise ValueError('No such uid in es!')
    machiavellianism_index,narcissism_index,psychopathy_index,extroversion_index,nervousness_index,openn_index,agreeableness_index,conscientiousness_index = cal_person(uid)
    veness_index,importance_index,sensitive_index,influence_index,liveness_star,importance_star,sensitive_star,influence_star = user_attribute(uid)
    dic = {
        'machiavellianism_index':machiavellianism_index,
        'narcissism_index':narcissism_index,
        'psychopathy_index':psychopathy_index,
        'extroversion_index':extroversion_index,
        'nervousness_index':nervousness_index,
        'openn_index':openn_index,
        'agreeableness_index':agreeableness_index,
        'conscientiousness_index':conscientiousness_index,
        'veness_index':veness_index,
        'importance_index':importance_index,
        'sensitive_index':sensitive_index,
        'influence_index':influence_index,
        'liveness_star':liveness_star,
        'importance_star':importance_star,
        'sensitive_star':sensitive_star,
        'influence_star':influence_star,
        'uid':uid,
        'username':username
    }
    es.index(index=USER_RANKING,doc_type='text',body=dic,id=uid)

def user_insert():
    query_body = {
        'query':{
            'match_all':{}
        },
        "size":1000
    }
    es_result = helpers.scan(
        client=es,
        query=query_body,
        scroll='1m',
        index=USER_INFORMATION,
        doc_type='text',
        timeout='1m'
    )

    num = 0
    for hit in es_result:
        print(num)
        uid = hit['_source']['uid']
        username = hit['_source']['username']
        user_ranking(uid,username)
        num += 1

def group_create(args_dict):
    uid_list_keyword = []
    if 'keyword' in args_dict:
        for weibo_index in WEIBO_INDEX:
            query_body = {
                "query":{
                    'match_phrase':{
                        'keywords_string':args_dict['keyword']
                    }
                },
                "size":1000
            }

            es_result = helpers.scan(
                client=es,
                query=query_body,
                scroll='1m',
                index=weibo_index,
                doc_type='text',
                timeout='1m'
            )

            for hit in es_result:
                uid_list_keyword.append(hit['_source']['uid'])

    uid_list_keyword = set(uid_list_keyword)

    query_body = {
        'query':{
            "filtered":{
                "filter":{
                    "bool":{
                        "must":[]
                    }
                }
            }
        }
    }
    num = 0
    for arg in args_dict:   #args_dict = {'keyword':word,'liveness_index':liveness_index,...}
        if arg == 'keyword':
            continue
        index_low = (args_dict[arg] - 1) * 20
        index_high = args_dict[arg] * 20
        if index_low == 0:
            query_body['query']['filtered']['filter']['bool']['must'].append({'range':{arg:{'gte':index_low,'lte':index_high}}})
        else:
            query_body['query']['filtered']['filter']['bool']['must'].append({'range':{arg:{'gt':index_low,'lte':index_high}}})
        num += 1

    uid_list_index = []
    if num:
        es_result = helpers.scan(
            client=es,
            query=query_body,
            scroll='1m',
            index=USER_RANKING,
            doc_type='text',
            timeout='1m'
        )
        for hit in es_result:
            uid_list_index.append(hit['_source']['uid'])

    uid_list_index = set(uid_list_index)
    uid_list = list(uid_list_index & uid_list_keyword)
    print(uid_list)
    
if __name__ == '__main__':
    args_dict = {
        'keyword':'语言',
        'machiavellianism_index':3
    }
    group_create(args_dict)