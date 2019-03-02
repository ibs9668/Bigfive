import sys
sys.path.append('../')
sys.path.append('portrait/user')
sys.path.append('portrait/group')
import random
from elasticsearch import Elasticsearch,helpers
from elasticsearch.helpers import bulk
from xpinyin import Pinyin

from config import *
from time_utils import *
from model.personality_predict import predict_personality
from cron_group import group_personality, group_activity, group_attribute, group_density_attribute


def user_ranking(uid_list,username_list,date):
    query_id_list = [uid + '_' + str(date2ts(date)) for uid in uid_list]
    res = es.mget(index=USER_PERSONALITY, doc_type='text', body={'ids':query_id_list})['docs']
    personality_dic = {i['_source']['uid']:i['_source'] for i in res}
    res = es.mget(index=USER_INFLUENCE, doc_type='text', body={'ids':query_id_list})['docs']
    attribute_dic = {i['_source']['uid']:i['_source'] for i in res}

    for uid in uid_list:
        dic = {
            'machiavellianism_index':personality_dic[uid]['machiavellianism_index'],
            'narcissism_index':personality_dic[uid]['narcissism_index'],
            'psychopathy_index':personality_dic[uid]['psychopathy_index'],
            'extroversion_index':personality_dic[uid]['extroversion_index'],
            'nervousness_index':personality_dic[uid]['nervousness_index'],
            'openn_index':personality_dic[uid]['openn_index'],
            'agreeableness_index':personality_dic[uid]['agreeableness_index'],
            'conscientiousness_index':personality_dic[uid]['conscientiousness_index'],
            'liveness_index':attribute_dic[uid]['activity'],
            'importance_index':attribute_dic[uid]['importance'],
            'sensitive_index':attribute_dic[uid]['sensitivity'],
            'influence_index':attribute_dic[uid]['influence'],
            'liveness_star':get_attribute_star(attribute_dic[uid]['activity']),
            'importance_star':get_attribute_star(attribute_dic[uid]['importance']),
            'sensitive_star':get_attribute_star(attribute_dic[uid]['sensitivity']),
            'influence_star':get_attribute_star(attribute_dic[uid]['influence']),
            'machiavellianism_label':get_personality_label(machiavellianism_index,'machiavellianism_index'),
            'narcissism_label':get_personality_label(narcissism_index,'narcissism_index'),
            'psychopathy_label':get_personality_label(psychopathy_index,'psychopathy_index'),
            'extroversion_label':get_personality_label(extroversion_index,'extroversion_index'),
            'nervousness_label':get_personality_label(nervousness_index,'nervousness_index'),
            'openn_label':get_personality_label(openn_index,'openn_index'),
            'agreeableness_label':get_personality_label(agreeableness_index,'agreeableness_index'),
            'conscientiousness_label':get_personality_label(conscientiousness_index,'conscientiousness_index'),
            'uid':uid,
            'username':username
        }
        es.index(index=USER_RANKING,doc_type='text',body=dic,id=uid)

def cal_personality(uid_list, date, days):
    # personality_dic = {}
    end_date = date
    start_date = ts2date(date2ts(date) - days*24*3600)
    per_predict = predict_personality(uid_list,start_date,end_date)
    timestamp = date2ts(date)
    for idx in range(len(uid_list)):
        uid = per_predict[0][idx]
        extroversion_index = per_predict[1][idx]
        agreeableness_index = per_predict[2][idx]
        conscientiousness_index = per_predict[3][idx]
        nervousness_index = per_predict[4][idx]
        openn_index = per_predict[5][idx]
        machiavellianism_index = per_predict[6][idx]
        narcissism_index = per_predict[7][idx]
        psychopathy_index = per_predict[8][idx]

        dic = {
            'extroversion_index':extroversion_index,
            'agreeableness_index':agreeableness_index,
            'conscientiousness_index':conscientiousness_index,
            'nervousness_index':nervousness_index,
            'openn_index':openn_index,
            'machiavellianism_index':machiavellianism_index,
            'narcissism_index':narcissism_index,
            'psychopathy_index':psychopathy_index,
            'uid':uid,
            'timestamp':timestamp,
            'date':date
        }
        # personality_dic[uid] = dic
        es.index(index=USER_PERSONALITY,doc_type='text',body=dic,id=uid + '_' + str(timestamp))

    # return personality_dic

def get_personality_label(personality_index, personality_name):
    threshold = PERSONALITY_DIC[personality_name]['threshold']
    if personality_index < threshold[0]:
        personality_label = 0
    elif personality_index > threshold[1]:
        personality_label = 2
    else:
        personality_label = 1

    return personality_label

def get_attribute_star(attribute_index):
    return int(liveness_index / 20) + 1

def user_insert():
    iter_num = 0
    iter_get_user = USER_ITER_COUNT
    while (iter_get_user == USER_ITER_COUNT):
        print('\nUsers that have been calculated: %d\n' % (iter_num*USER_ITER_COUNT))
        user_query_body = {
            'query':{
                'match_all':{}
            },
            'sort':{
                'uid':{
                    'order':'asc'
                }
            },
            "size":USER_ITER_COUNT,
            "from":iter_num * USER_ITER_COUNT
        }
        es_result = es.search(index=USER_INFORMATION,doc_type='text',body=user_query_body)['hits']['hits']
        iter_get_user = len(es_result)
        iter_num += 1
        iter_user_list = [hit['_source']['uid'] for hit in es_result]
        iter_username_list = [hit['_source']['username'] for hit in es_result]
        cal_personality(iter_user_list,'2016-11-27',14)
        user_ranking(iter_user_list,iter_username_list,'2016-11-27')

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
        'create_date':ts2date(create_time),
        'keyword':keyword,
        'group_pinyin':group_pinyin,
        'group_id':group_pinyin + '_' + str(create_time),
        'userlist':uid_list
    }

    es.index(index=GROUP_INFORMATION,doc_type='text',body=dic,id=dic['group_id'])

    return dic

# def group_attribute(uid_list, date):
#     activity = int(random.random() * 100)
#     influence = int(random.random() * 100)
#     importance = int(random.random() * 100)
#     sensitivity = int(random.random() * 100)
#     activeness_star = int(activity / 20) + 1
#     influence_star = int(influence / 20) + 1
#     importance_star = int(importance / 20) + 1
#     sensitivity_star = int(sensitivity / 20 + 1)
#     return activity, influence, importance, sensitivity, activeness_star, influence_star, importance_star, sensitivity_star

# def group_density_attribute(uid_list, date, num):
#     in_density = int(random.random() * 100)
#     density_star = int(in_density / 20) + 1
#     return in_density, density_star

def group_ranking(group_dic):
    uid_list = group_dic['userlist']
    date = ts2date(group_dic['create_time'])
    group_id = group_dic['group_id']
    group_name = group_dic['group_name']
    machiavellianism_index,narcissism_index,psychopathy_index,extroversion_index,nervousness_index,openn_index,agreeableness_index,conscientiousness_index = group_personality(uid_list)
    activity, influence, importance, sensitivity, activeness_star, influence_star, importance_star, sensitivity_star = group_attribute(uid_list, date)
    in_density, density_star = group_density_attribute(uid_list, date, 15)
    dic = {
        'machiavellianism_index':machiavellianism_index,
        'narcissism_index':narcissism_index,
        'psychopathy_index':psychopathy_index,
        'extroversion_index':extroversion_index,
        'nervousness_index':nervousness_index,
        'openn_index':openn_index,
        'agreeableness_index':agreeableness_index,
        'conscientiousness_index':conscientiousness_index,
        'liveness_index':activity,
        'importance_index':importance,
        'sensitive_index':sensitivity,
        'influence_index':influence,
        'compactness_index':in_density,
        'liveness_star':activeness_star,
        'importance_star':importance_star,
        'sensitive_star':sensitivity_star,
        'influence_star':influence_star,
        'compactness_star':density_star,
        'group_id':group_id,
        'group_name':group_name
    }
    es.index(index=GROUP_RANKING,doc_type='text',body=dic,id=group_id)
    
if __name__ == '__main__':
    user_insert()
    # args_dict = {
    #     'machiavellianism_index':0,
    #     'narcissism_index':0,
    #     'psychopathy_index':0,
    #     'extroversion_index':0,
    #     'nervousness_index':0,
    #     'openn_index':0,
    #     'agreeableness_index':0,
    #     'conscientiousness_index':0,
    # }
    # keyword = '强大'
    # remark = '明哥的确是厉害'
    # group_name = '明哥厉害'
    # create_time = int(time.time())
    # group_create(args_dict,keyword,remark,group_name,create_time)
    # print(es.mget(index=USER_INFORMATION, doc_type='text', body={'ids':['1608546201','111111111']}))