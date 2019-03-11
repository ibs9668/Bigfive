import sys
sys.path.append('../../../')

from config import *
from time_utils import *

#根据群体内的用户计算用户的位置情况，指定时间范围计算该范围内用户的出发地、目的地和转移情况
#输入：群组id，日期，向前延伸天数
#输出，将群组该日期的位置情况存入数据库
def group_activity(group_id, uid_list, start_date, end_date):
    date_end_ts = date2ts(end_date)
    date_start_ts = date2ts(start_date)
    activity_direction = {}
    main_start_geo = {}
    main_end_geo = {}
    print(len(uid_list))
    for uid in uid_list:
        # print(uid)
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

        geo_dic = {}
        for hit in res:
            geo = hit['_source']['geo']
            timestamp = hit['_source']['timestamp']
            count = hit['_source']['count']
            if timestamp in geo_dic:
                if geo in geo_dic[timestamp]:
                    geo_dic[timestamp][geo] += count
                else:
                    geo_dic[timestamp][geo] = count
            else:
                geo_dic[timestamp] = {geo:count}

        geo_list = []
        for timestamp in sorted(list(geo_dic.keys())):
            main_geo = sorted(geo_dic[timestamp].items(),key = lambda x:x[1],reverse = False)[0][0]
            geo_list.append({'geo':main_geo,'timestamp':timestamp})
        #取出来的每一个用户的位置为每一天该用户的所在地{'geo':geo,'timestamp':timestamp}

        if len(geo_list) == 0:
            continue
        last_geo = geo_list[0]['geo'].replace('&',' ')
        for hit in geo_list[1:]:
            geo = hit['geo'].replace('&',' ')
            #对于前后两天位置不同的认为是发生了位置改变
            if last_geo != geo:
                geo2geo = last_geo + '&' + geo
                try:
                    activity_direction[geo2geo] += 1
                except:
                    activity_direction[geo2geo] = 1

                try:
                    main_start_geo[last_geo] += 1
                except:
                    main_start_geo[last_geo] = 1

                try:
                    main_end_geo[geo] += 1
                except:
                    main_end_geo[geo] = 1

            last_geo = geo

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
        'main_end_geo':main_end_geo_dic,
        'date':end_date
    }
    es.index(index=GROUP_ACTIVITY, doc_type='text', id=str(group_id)+'_'+str(date_end_ts), body=dic)