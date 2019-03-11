#-*-coding=utf-8-*-
import os
import re
import sys
import json

import geoip2.database

import sys
sys.path.append('../../../')
from config import *
from time_utils import *

list_index = [ 'flow_text_2016-11-14', 'flow_text_2016-11-15', 'flow_text_2016-11-16',\
 'flow_text_2016-11-17', 'flow_text_2016-11-18', 'flow_text_2016-11-19', 'flow_text_2016-11-20', \
 'flow_text_2016-11-21', 'flow_text_2016-11-22', 'flow_text_2016-11-23', 'flow_text_2016-11-24',\
  'flow_text_2016-11-25', 'flow_text_2016-11-26', 'flow_text_2016-11-27'] #'flow_text_2016-11-13',


#IP映射到 国家-省份-城市
def from_ip_get_info(sip):
    reader = geoip2.database.Reader('GeoLite2-City/GeoLite2-City.mmdb')
    try:
        response = reader.city(sip)
        try:
            city = response.city.names.get(u'zh-CN', response.city.name)
            country = response.registered_country.names.get(u'zh-CN')
            subdivisions = response.subdivisions.most_specific.names.get(u'zh-CN', "")

            if not city:
                city = u'其他'
                # city = response.country.names.get(u'zh-CN')
            if not subdivisions:
                subdivisions = u'其他'
        except Exception as e:
            logging.debug("read Geolite2-City.mmdb error:%s" % e)
            city = ''

        # subdivisions = response.subdivisions.most_specific.names.get(u'zh-CN', "")
    except Exception as ex:
        return u'其他'
    return country+"&"+subdivisions+"&"+city

#汇总用户IP频次
def get_recent_ip(uid,index_list,date): #n_days,

    ip_dict = dict()

    query_body = {"query": {
        "bool": {
            "must": [
                    {"term": {
                        "uid": uid
                        }  
                        }
              
            ]
        }
    },
        "from": 0,
        "size": 0,
        "aggs": {"ip_aggs":{"terms":{"field":"ip","size":300,"order":{"_count":"desc"}}} }
    }

    ip_list = []
    search_result = es_weibo.search(index=index_list,body=query_body)["aggregations"]["ip_aggs"]["buckets"] #doc_type=event_name,
    for i in search_result:
        i["uid"] = uid
        i["timestamp"] = date2ts(date)
        ip_list.append(i)

    return ip_list

#汇总IP
def ip_rank(ip_list):

    for i in ip_list:
        result_dict = dict()
        location = from_ip_get_info(i["key"])
        result_dict["ip"] = i["key"]
        result_dict["location"] = location
        result_dict["count"] = i["doc_count"]
        result_dict["uid"] = i["uid"]
        result_dict["date"] = i["timestamp"]

        es.index(index="user_activity",doc_type="text",
        body={
        "timestamp": i["timestamp"],
        "uid":i["uid"],
        "ip":i["key"],
        "geo":location
        ,
        "count":int(i["doc_count"])
                },timeout=50)


##########################################

def get_weibo_index(RUN_TYPE,start_date,last_time):

    weibo_index_pre = "flow_text_"
    if RUN_TYPE == 1:       
        now_date = ts2datetime(time.time())
        now_date_ts = date2ts(now_date)+DAY#今天零点时间戳
    elif RUN_TYPE == 2:
        start_date_ts = date2ts(start_date) #开始时间戳

        weibo_index_list = []
        for i in range(last_time):
            start_date_ts = int(start_date_ts+ DAY)
            start_date = ts2datetime(start_date_ts)
            if es_weibo.indices.exists(index=str(weibo_index_pre)+str(start_date)) :
                weibo_index_list.append(str(weibo_index_pre)+str(start_date))

    return weibo_index_list  #计算得到微博es

def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    return uid_list


def user_ip_run(flow_text_list):

    uid_list = get_uidlist()
    for i in range(len(flow_text_list)):
        count = 0
        try: 
            for uid in uid_list:
                ip_list = get_recent_ip(uid,flow_text_list[i],flow_text_list[i].split("_")[-1])

                if ip_list == []:
                    es.index(index="user_activity",doc_type="text",
                            body={
                            "timestamp": date2ts(flow_text_list[i].split("_")[-1]),
                            "uid":uid,
                            "ip":"",
                            "geo":"",
                            "count":0},timeout=50)
                else:
                    ip_rank(ip_list)
                count += 1
                print(count)
        except:
            pass
  
def get_user_activity(uid, date):
    get_recent_ip(uid,'flow_text_%s' % date,date)


if __name__ == '__main__':
    
    user_ip_run(ES_INDEX_LIST)

  #   uid_list = get_uidlist()
  #   #索引名称
  #   for i in range(len(list_index)):
  #       date_list= ["2016-11-14","2016-11-15","2016-11-16","2016-11-17","2016-11-18",\
  #       "2016-11-19","2016-11-20","2016-11-21","2016-11-22","2016-11-23","2016-11-24","2016-11-25",\
  #       "2016-11-26","2016-11-27"]  #"2016-11-13",
  #       # print (list_index[i])
  #       count = 0
  #       try: 
  #           for uid in uid_list:
  #               ip_list = get_recent_ip(uid,list_index[i],date_list[i])

  #               if ip_list == []:
  #                   pass
  #               else:

  #                   ip_rank(ip_list)
  #               count += 1
  #               print(count)
  #       except:
  #           print("error____"+list_index[i]+"____"+str(count))
  # 