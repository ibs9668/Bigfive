import sys
sys.path.append('../../../')
from config import *
from time_utils import *

#根据群体内的用户计算用户的位置情况，指定时间范围计算该范围内用户的出发地、目的地和转移情况
#输入：群组id，日期，向前延伸天数
#输出，将群组该日期的位置情况存入数据库
def group_activity(group_id, date, days):
    date_end_ts = date2ts(date)
    date_start_ts = date_end_ts - 24*3600*days
    activity_direction = {}
    main_start_geo = {}
    main_end_geo = {}
    userlist = es.get(index=GROUP_INFORMATION, doc_type='text', id=group_id)['_source']['user_lst']
    print(len(userlist))
    for uid in userlist:
        print(uid)
        query_body = {
            "query":{
                "filtered":{
                    "filter":{
                        "bool":{
                            "must":[
                                {"term":{"uid":uid}},
                                {"range":{
                                    "timestamp":{
                                        "gt":date_start_ts,
                                        "lte":date_end_ts
                                    }
                                }}
                            ]
                        }
                    }
                }
            },
            "size":500,
            "sort":{
                "timestamp":{
                    "order":"asc"
                }
            }
        }
        res = es.search(index=USER_ACTIVITY, doc_type='text', body=query_body)['hits']['hits']
        #取出来的每一个用户的位置为每一天该用户的所在地{'location':location,'timestamp':timestamp}

        if len(res) == 0:
            continue
        last_location = res[0]['_source']['location'].replace('&',' ')
        for hit in res[1:]:
            location = hit['_source']['location'].replace('&',' ')
            #对于前后两天位置不同的认为是发生了位置改变
            if last_location != location:
                geo2geo = last_location + '&' + location
                try:
                    activity_direction[geo2geo] += 1
                except:
                    activity_direction[geo2geo] = 1

                try:
                    main_start_geo[last_location] += 1
                except:
                    main_start_geo[last_location] = 1

                try:
                    main_end_geo[location] += 1
                except:
                    main_end_geo[location] = 1

            last_location = location

    sorted_activity_direction = sorted(activity_direction.items(),key = lambda x:x[1],reverse = True)
    sorted_main_start_geo = sorted(main_start_geo.items(),key = lambda x:x[1],reverse = True)
    sorted_main_end_geo = sorted(main_end_geo.items(),key = lambda x:x[1],reverse = True)

    activity_direction_dic = [{'geo2geo':i[0],'count':i[1]} for i in sorted_activity_direction]
    main_start_geo_dic = [{'main_start_geo':i[0],'count':i[1]} for i in sorted_main_start_geo]
    main_end_geo_dic = [{'main_end_geo':i[0],'count':i[1]} for i in sorted_main_end_geo]

    dic = {
        'timestamp':date_end_ts,
        'group_id':group_id,
        'activity_direction':activity_direction_dic,
        'main_start_geo':main_start_geo_dic,
        'main_end_geo':main_end_geo_dic
    }
    es.index(index=GROUP_ACTIVITY, doc_type='text', id=str(group_id)+'_'+str(date_end_ts), body=dic)

#计算群组的紧密性、重要度、活跃度与影响力，紧密性根据转发评论关系计算，其他为群组内用户对应指标均值
#输入：群组id
#输出：将该群组的四项属性以星级的形式存入数据库
def group_social_attribute(group_id):
    uid_list = es.get(index=GROUP_INFORMATION, doc_type='text', id=group_id)['_source']['user_lst']
    iter_count = 0
    all_user_count = len(uid_list)
    importance_list = []
    influence_list = []
    activeness_list = []
    result = {}
    while iter_count < all_user_count:   #一下获取多个用户以减少查询次数
        iter_uid_list = uid_list[iter_count: iter_count + GROUP_ITER_COUNT]
        try:
            iter_user_dict_list = es.mget(index=USER_RANKING, doc_type='text', body={'ids':iter_uid_list})['docs']
        except:
            iter_user_dict_list = []

        #利用用户对应属性在全体用户中的排名计算群体的这些属性
        for user_dict in iter_user_dict_list:
            uid = user_dict['_id']
            if user_dict['found'] == False:
                continue
            source = user_dict['_source']
            #影响力
            influence = source['influence_index']
            influence_rank = get_index_rank(influence, 'influence_index')
            influence_list.append(influence_rank) 
            #重要度
            importance = source['importance_index']
            importance_rank = get_index_rank(importance, 'importance_index')
            importance_list.append(importance_rank)
            #活跃度
            activeness = source['liveness_index']
            activeness_rank = get_index_rank(activeness, 'liveness_index')
            activeness_list.append(activeness_rank)
            print(uid,importance,influence,activeness)
            print(uid,importance_rank,influence_rank,activeness_rank)

        iter_count += GROUP_ITER_COUNT

    print(importance_list,influence_list,activeness_list)
    #计算属性排名的平均值
    try:
        all_user_count = es.count(index=USER_RANKING, doc_type='text', body={'query':{'match_all':{}}})['count']
    except Exception as e:
        raise e
    #活跃度
    ave_activeness_rank = float(sum(activeness_list)) / len(activeness_list)
    if ave_activeness_rank <= GROUP_AVE_ACTIVENESS_RANK_THRESHOLD[0] * all_user_count:
        result['activeness_star'] = 5
    elif ave_activeness_rank > GROUP_AVE_ACTIVENESS_RANK_THRESHOLD[1] * all_user_count:
        result['activeness_star'] = 1
    else:
        result['activeness_star'] = 3
    #影响力
    ave_influence_rank = float(sum(influence_list) / len(influence_list))
    if ave_influence_rank <= GROUP_AVE_INFLUENCE_RANK_THRESHOLD[0] * all_user_count:
        result['influence_star'] = 5
    elif ave_influence_rank > GROUP_AVE_INFLUENCE_RANK_THRESHOLD[1] * all_user_count:
        result['influence_star'] = 1
    else:
        result['influence_star'] = 3
    #重要度
    ave_importance_rank = float(sum(importance_list) / len(importance_list))
    if ave_importance_rank <= GROUP_AVE_IMPORTANCE_RANK_THRESHOLD[0] * all_user_count:
        result['importance_star'] = 5
    elif ave_importance_rank > GROUP_AVE_IMPORTANCE_RANK_THRESHOLD[1] * all_user_count:
        result['importance_star'] = 1
    else:
        result['importance_star'] = 3
    return result


###获得对应的数值在用户列表中的排名
def get_index_rank(attr_value, attr_name):
    result = 0
    query_body = {
            'query':{
                'range':{
                    attr_name:{
                        'from':attr_value,
                        'to': MAX_VALUE
                        }
                    }
                }
            }
    index_rank = es.count(index=USER_RANKING, doc_type='text', body=query_body)
    if index_rank['_shards']['successful'] != 0:
       result = index_rank['count']
    else:
        print('es index rank error')
        result = 0
    return result


if __name__=='__main__':
    # group_activity('2','2019-01-23',7)
    print(group_social_attribute('2'))