import sys
sys.path.append('../')
sys.path.append('portrait/user')
from config import *
from time_utils import *

from model.personality_cal import cal_person
from cron_user import user_attribute

from elasticsearch import Elasticsearch,helpers
from elasticsearch.helpers import bulk
from xpinyin import Pinyin

def user_ranking(uid,username=None):
    if username == None:
        try:
            username = es.get(index=USER_INFORMATION,doc_type='text',id=uid)['_source']['username']
        except:
            raise ValueError('No such uid in es!')
    machiavellianism_index,narcissism_index,psychopathy_index,extroversion_index,nervousness_index,openn_index,agreeableness_index,conscientiousness_index = cal_person(uid)
    liveness_index,importance_index,sensitive_index,influence_index,liveness_star,importance_star,sensitive_star,influence_star = user_attribute(uid)
    dic = {
        'machiavellianism_index':machiavellianism_index,
        'narcissism_index':narcissism_index,
        'psychopathy_index':psychopathy_index,
        'extroversion_index':extroversion_index,
        'nervousness_index':nervousness_index,
        'openn_index':openn_index,
        'agreeableness_index':agreeableness_index,
        'conscientiousness_index':conscientiousness_index,
        'liveness_index':liveness_index,
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

def group_create(args_dict,keyword,remark,group_name,create_time):
    uid_list_keyword = []
    # USER_WEIBO_ITER_COUNT = 1000
    if keyword != '':
        for weibo_index in ES_INDEX_LIST:
            print(weibo_index)
            weibo_iter_num = 0
            iter_get_weibo = USER_WEIBO_ITER_COUNT
            es_result = []
            while (iter_get_weibo == USER_WEIBO_ITER_COUNT):
                print(weibo_iter_num*USER_WEIBO_ITER_COUNT)
                weibo_query_body = {
                    "query":{
                        'match_phrase':{
                            'keywords_string':keyword
                        }
                    },
                    'sort':{
                        '_id':{
                            'order':'asc'
                        }
                    },
                    "size":USER_WEIBO_ITER_COUNT,
                    "from":weibo_iter_num * USER_WEIBO_ITER_COUNT
                }
                res = es_weibo.search(index=weibo_index,doc_type='text',body=weibo_query_body)['hits']['hits']
                es_result.extend(res)
                iter_get_weibo = len(res)
                weibo_iter_num += 1
            print(len(es_result))

            uid_list_keyword.extend([hit['_source']['uid'] for hit in es_result])
    uid_list_keyword = set(uid_list_keyword)


    user_query_body = {
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
        if args_dict[arg] == 0:
            continue
        index_low = (args_dict[arg] - 1) * 20
        index_high = args_dict[arg] * 20
        if index_low == 0:
            user_query_body['query']['filtered']['filter']['bool']['must'].append({'range':{arg:{'gte':index_low,'lte':index_high}}})
        else:
            user_query_body['query']['filtered']['filter']['bool']['must'].append({'range':{arg:{'gt':index_low,'lte':index_high}}})
        num += 1

    uid_list_index = []
    # user_query_body['size'] = 5000
    # es_result = es.search(index=USER_RANKING,doc_type='text',body=user_query_body)['hits']['hits']
    # uid_list_index = [hit['_source']['uid'] for hit in es_result]
    if num:
        iter_num = 0
        iter_get_user = USER_ITER_COUNT
        while (iter_get_user == USER_ITER_COUNT):
            print(iter_num*USER_ITER_COUNT)
            user_query_body['size'] = USER_ITER_COUNT
            user_query_body['from'] = iter_num * USER_ITER_COUNT
            user_query_body['sort'] = {'uid':{'order':'asc'}}
            # print(user_query_body)
            es_result = es.search(index=USER_RANKING,doc_type='text',body=user_query_body)['hits']['hits']
            iter_get_user = len(es_result)
            iter_num += 1

            for hit in es_result:
                uid_list_index.append(hit['_source']['uid'])

    uid_list_index = set(uid_list_index)

    if keyword != '' and num != 0:
        uid_list = list(uid_list_index & uid_list_keyword)
    if num == 0:
        uid_list_keyword = list(uid_list_keyword)
        iter_num = 0
        uid_list = []
        while (iter_num*USER_WEIBO_ITER_COUNT <= len(uid_list_keyword)):
            iter_uid_list_keyword = uid_list_keyword[iter_num*USER_WEIBO_ITER_COUNT : (iter_num + 1)*USER_WEIBO_ITER_COUNT]
            iter_user_dict_list = es.mget(index=USER_INFORMATION, doc_type='text', body={'ids':iter_uid_list_keyword})['docs']
            uid_list.extend([i['_id'] for i in iter_user_dict_list if i['found']])
            iter_num += 1
    if keyword == '':
        uid_list = list(uid_list_index)

    print(len(uid_list))
    group_pinyin = Pinyin().get_pinyin(group_name, '')
    dic = {
        'remark':remark,
        'create_condition':args_dict,
        'group_name':group_name,
        'create_time':create_time,
        'keyword':create_time,
        'group_pinyin':group_pinyin,
        'group_id':group_pinyin + '_' + str(create_time),
        'userlist':uid_list
    }

    es.index(index=GROUP_INFORMATION,doc_type='text',body=dic,id=dic['group_id'])

    return dic

    
if __name__ == '__main__':
    args_dict = {
        'machiavellianism_index':0,
        'narcissism_index':0,
        'psychopathy_index':0,
        'extroversion_index':0,
        'nervousness_index':0,
        'openn_index':0,
        'agreeableness_index':0,
        'conscientiousness_index':0,
    }
    # keyword = '强大'
    keyword = '强大'
    remark = '明哥的确是厉害'
    group_name = '明哥厉害'
    create_time = int(time.time())
    group_create(args_dict,keyword,remark,group_name,create_time)
    # print(es.mget(index=USER_INFORMATION, doc_type='text', body={'ids':['1608546201','111111111']}))