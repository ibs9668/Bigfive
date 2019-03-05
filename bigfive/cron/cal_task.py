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
from cron_group import group_activity, group_attribute


def user_ranking(uid_list,username_list,date):
    query_id_list = [uid + '_' + str(date2ts(date)) for uid in uid_list]
    res = es.mget(index=USER_PERSONALITY, doc_type='text', body={'ids':query_id_list})['docs']
    personality_dic = {i['_source']['uid']:i['_source'] for i in res}
    res = es.mget(index=USER_INFLUENCE, doc_type='text', body={'ids':query_id_list})['docs']
    attribute_dic = {i['_source']['uid']:i['_source'] for i in res}

    for idx in range(len(uid_list)):
        uid = uid_list[idx]
        username = username_list[idx]

        #黑暗+大五人格计算值
        machiavellianism_index = personality_dic[uid]['machiavellianism_index']
        narcissism_index = personality_dic[uid]['narcissism_index']
        psychopathy_index = personality_dic[uid]['psychopathy_index']
        extroversion_index = personality_dic[uid]['extroversion_index']
        nervousness_index = personality_dic[uid]['nervousness_index']
        openn_index = personality_dic[uid]['openn_index']
        agreeableness_index = personality_dic[uid]['agreeableness_index']
        conscientiousness_index = personality_dic[uid]['conscientiousness_index']

        #画像计算
        liveness_index = get_attribute_normalization(attribute_dic[uid]['activity'],'activity')
        importance_index = get_attribute_normalization(attribute_dic[uid]['importance'],'importance')
        sensitive_index = get_attribute_normalization(attribute_dic[uid]['sensitivity'],'sensitivity')
        influence_index = get_attribute_normalization(attribute_dic[uid]['influence'],'influence')

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

            'liveness_star':get_attribute_star(liveness_index),
            'importance_star':get_attribute_star(importance_index),
            'sensitive_star':get_attribute_star(sensitive_index),
            'influence_star':get_attribute_star(influence_index),

            'machiavellianism_label':get_user_personality_label(machiavellianism_index,'machiavellianism_index'),
            'narcissism_label':get_user_personality_label(narcissism_index,'narcissism_index'),
            'psychopathy_label':get_user_personality_label(psychopathy_index,'psychopathy_index'),
            'extroversion_label':get_user_personality_label(extroversion_index,'extroversion_index'),
            'nervousness_label':get_user_personality_label(nervousness_index,'nervousness_index'),
            'openn_label':get_user_personality_label(openn_index,'openn_index'),
            'agreeableness_label':get_user_personality_label(agreeableness_index,'agreeableness_index'),
            'conscientiousness_label':get_user_personality_label(conscientiousness_index,'conscientiousness_index'),

            'uid':uid,
            'username':username
        }
        es.index(index=USER_RANKING,doc_type='text',body=dic,id=uid)

def cal_user_personality(uid_list, date, days):
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

def get_user_personality_label(personality_index, personality_name):
    threshold = PERSONALITY_DIC[personality_name]['threshold']
    if personality_index < threshold[0]:
        personality_label = 0
    elif personality_index > threshold[1]:
        personality_label = 2
    else:
        personality_label = 1

    return personality_label

def get_attribute_normalization(attribute_index, attribute_name):
    threshold = ATTRIBUTE_DIC[attribute_name]['threshold']
    if attribute_index < threshold[0]:
        attribute_normalization = 0
    elif attribute_index > threshold[1]:
        attribute_normalization = 100
    else:
        attribute_normalization = int(((attribute_index - threshold[0]) / (threshold[1] - threshold[0])) * 100)

    return attribute_normalization

def get_attribute_star(attribute_index):
    return int(attribute_index / 20) + 1

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
        if len(iter_user_list) == 0:
            break
        cal_user_personality(iter_user_list,'2016-11-27',14)
        time.sleep(1)
        user_ranking(iter_user_list,iter_username_list,'2016-11-27')




#群体的创建，扫描未计算的任务，获得任务的基本参数开始计算，主要为了圈定符合条件的用户群体，利用关键词检索和人格计算得分进行筛选
#输入：从group_task表中获得所需参数列表
#输出：存储获得的userlist至数据库
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


def group_ranking(group_dic):
    uid_list = group_dic['userlist']
    date = ts2date(group_dic['create_time'])
    group_id = group_dic['group_id']
    group_name = group_dic['group_name']

    query_id = group_id + '_' + str(date2ts(date))
    personality_dic = es.get(index=GROUP_PERSONALITY, doc_type='text', id=query_id)['_source']
    attribute_dic = es.get(index=GROUP_INFLUENCE, doc_type='text', id=query_id)['_source']

    machiavellianism_index = int(personality_dic['machiavellianism_index'])
    narcissism_index = int(personality_dic['narcissism_index'])
    psychopathy_index = int(personality_dic['psychopathy_index'])
    extroversion_index = int(personality_dic['extroversion_index'])
    nervousness_index = int(personality_dic['nervousness_index'])
    openn_index = int(personality_dic['openn_index'])
    agreeableness_index = int(personality_dic['agreeableness_index'])
    conscientiousness_index = int(personality_dic['conscientiousness_index'])

    activity = int(attribute_dic['activity'])
    influence = int(attribute_dic['influence'])
    importance = int(attribute_dic['importance'])
    sensitivity = int(attribute_dic['sensitivity'])
    density = int(attribute_dic['density'])
    activeness_star = attribute_dic['activeness_star']
    influence_star = attribute_dic['influence_star']
    importance_star = attribute_dic['importance_star']
    sensitivity_star = attribute_dic['sensitivity_star']
    density_star = attribute_dic['density_star']
    
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
        'compactness_index':density,
        'liveness_star':activeness_star,
        'importance_star':importance_star,
        'sensitive_star':sensitivity_star,
        'influence_star':influence_star,
        'compactness_star':density_star,

        'machiavellianism_label':get_user_personality_label(machiavellianism_index,'machiavellianism_index'),
        'narcissism_label':get_user_personality_label(narcissism_index,'narcissism_index'),
        'psychopathy_label':get_user_personality_label(psychopathy_index,'psychopathy_index'),
        'extroversion_label':get_user_personality_label(extroversion_index,'extroversion_index'),
        'nervousness_label':get_user_personality_label(nervousness_index,'nervousness_index'),
        'openn_label':get_user_personality_label(openn_index,'openn_index'),
        'agreeableness_label':get_user_personality_label(agreeableness_index,'agreeableness_index'),
        'conscientiousness_label':get_user_personality_label(conscientiousness_index,'conscientiousness_index'),

        'group_id':group_id,
        'group_name':group_name
    }
    es.index(index=GROUP_RANKING,doc_type='text',body=dic,id=group_id)


def cal_group_personality(group_id, uid_list, date):
    date_ts = date2ts(date)
    iter_count = 0
    group_all_user_count = len(uid_list)
    extroversion_index_list = []
    agreeableness_index_list = []
    conscientiousness_index_list = []
    nervousness_index_list = []
    openn_index_list = []
    machiavellianism_index_list = []
    narcissism_index_list = []
    psychopathy_index_list = []
    while iter_count < group_all_user_count:   #一下获取多个用户以减少查询次数
        print('iter_num: %d' % iter_count)
        iter_uid_list = uid_list[iter_count: iter_count + GROUP_ITER_COUNT]
        iter_uid_list = [uid + '_' + str(date_ts) for uid in iter_uid_list]
        try:
            iter_user_dict_list = es.mget(index=USER_PERSONALITY, doc_type='text', body={'ids':iter_uid_list})['docs']
        except:
            iter_user_dict_list = []

        for user_dict in iter_user_dict_list:
            uid = user_dict['_id']
            if user_dict['found'] == False:
                continue
            source = user_dict['_source']
            #外倾性
            extroversion_index = source['extroversion_index']
            extroversion_index_rank = get_index_rank(extroversion_index, 'extroversion_index', date_ts)
            extroversion_index_list.append(extroversion_index_rank) 
            #宜人性
            agreeableness_index = source['agreeableness_index']
            agreeableness_index_rank = get_index_rank(agreeableness_index, 'agreeableness_index', date_ts)
            agreeableness_index_list.append(agreeableness_index_rank)
            #尽责性
            conscientiousness_index = source['conscientiousness_index']
            conscientiousness_index_rank = get_index_rank(conscientiousness_index, 'conscientiousness_index', date_ts)
            conscientiousness_index_list.append(conscientiousness_index_rank)
            #神经质
            nervousness_index = source['nervousness_index']
            nervousness_index_rank = get_index_rank(nervousness_index, 'nervousness_index', date_ts)
            nervousness_index_list.append(nervousness_index_rank)
            #开放性
            openn_index = source['openn_index']
            openn_index_rank = get_index_rank(openn_index, 'openn_index', date_ts)
            openn_index_list.append(openn_index_rank)
            #马基雅维利主义
            machiavellianism_index = source['machiavellianism_index']
            machiavellianism_index_rank = get_index_rank(machiavellianism_index, 'machiavellianism_index', date_ts)
            machiavellianism_index_list.append(machiavellianism_index_rank)
            #自恋
            narcissism_index = source['narcissism_index']
            narcissism_index_rank = get_index_rank(narcissism_index, 'narcissism_index', date_ts)
            narcissism_index_list.append(narcissism_index_rank)
            #精神病态
            psychopathy_index = source['psychopathy_index']
            psychopathy_index_rank = get_index_rank(psychopathy_index, 'psychopathy_index', date_ts)
            psychopathy_index_list.append(psychopathy_index_rank)

        iter_count += GROUP_ITER_COUNT

    #计算属性排名的平均值
    try:
        all_user_count = es.count(index=USER_PERSONALITY, doc_type='text', body={'query':{'term':{'timestamp':date_ts}}})['count']
    except Exception as e:
        raise e

    ave_extroversion_index_rank = float(sum(extroversion_index_list)) / len(extroversion_index_list)
    extroversion_index = (all_user_count - ave_extroversion_index_rank) / all_user_count * 100

    ave_agreeableness_index_rank = float(sum(agreeableness_index_list) / len(agreeableness_index_list))
    agreeableness_index = (all_user_count - ave_agreeableness_index_rank) / all_user_count * 100

    ave_conscientiousness_index_rank = float(sum(conscientiousness_index_list) / len(conscientiousness_index_list))
    conscientiousness_index = (all_user_count - ave_conscientiousness_index_rank) / all_user_count * 100

    ave_nervousness_index_rank = float(sum(nervousness_index_list) / len(nervousness_index_list))
    nervousness_index = (all_user_count - ave_nervousness_index_rank) / all_user_count * 100

    ave_openn_index_rank = float(sum(openn_index_list) / len(openn_index_list))
    openn_index = (all_user_count - ave_openn_index_rank) / all_user_count * 100

    ave_machiavellianism_index_rank = float(sum(machiavellianism_index_list) / len(machiavellianism_index_list))
    machiavellianism_index = (all_user_count - ave_machiavellianism_index_rank) / all_user_count * 100

    ave_narcissism_index_rank = float(sum(narcissism_index_list) / len(narcissism_index_list))
    narcissism_index = (all_user_count - ave_narcissism_index_rank) / all_user_count * 100

    ave_psychopathy_index_rank = float(sum(psychopathy_index_list) / len(psychopathy_index_list))
    psychopathy_index = (all_user_count - ave_psychopathy_index_rank) / all_user_count * 100


    dic = {
        'extroversion_index':extroversion_index,
        'agreeableness_index':agreeableness_index,
        'conscientiousness_index':conscientiousness_index,
        'nervousness_index':nervousness_index,
        'openn_index':openn_index,
        'machiavellianism_index':machiavellianism_index,
        'narcissism_index':narcissism_index,
        'psychopathy_index':psychopathy_index,
        'group_id':group_id,
        'timestamp':date_ts,
        'date':date
    }
    # personality_dic[uid] = dic
    es.index(index=GROUP_PERSONALITY,doc_type='text',body=dic,id=group_id + '_' + str(date_ts))

###获得对应的数值在用户列表中的排名
def get_index_rank(personality_value, personality_name, timestamp):
    result = 0
    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'timestamp':timestamp}},
                    {'range':{
                        personality_name:{
                            'from':personality_value,
                            'to': MAX_VALUE
                            }
                        }
                    }
                ]
            }
        }
    }
    index_rank = es.count(index=USER_PERSONALITY, doc_type='text', body=query_body)
    if index_rank['_shards']['successful'] != 0:
       result = index_rank['count']
    else:
        print('es index rank error')
        result = 0
    return result

def get_group_personality_label(personality_index, personality_name):
    threshold = PERSONALITY_DIC[personality_name]['threshold']
    if personality_index < threshold[0]:
        personality_label = 0
    elif personality_index > threshold[1]:
        personality_label = 2
    else:
        personality_label = 1

    return personality_label

if __name__ == '__main__':
    # user_insert()
    es.delete(index='group_task',doc_type='text',id='aaa_1551347004')
    dic = {
        "remark": "第四次群体测试",
        "keyword": "",
        "create_condition": {
            'machiavellianism_index':1,
            'narcissism_index':5,
            'psychopathy_index':0,
            'extroversion_index':0,
            'nervousness_index':0,
            'openn_index':0,
            'agreeableness_index':0,
            'conscientiousness_index':0,
        },
        "group_name": "测试四",
        "group_pinyin": Pinyin().get_pinyin(group_name, ''),
        "create_time": int(time.time()),
        "create_date": ts2date(create_time),
        "progress": 0
    }
    es.index(index='group_task',doc_type='text',id=dic['group_pinyin'] + '_' + str(dic['create_time']),body=dic)