# -*- coding: UTF-8 -*-

import os
import time
import numpy as np
import math
import json
import sys

sys.path.append('../../../')
from config import *
from time_utils import *
from global_utils import *


Fifteenminutes = 15


def get_max_fansnum():
    query_body = {"aggs": {"max_fansnum": {"max": {"field": "fans_num"}}}}
    #uid_list = ["2396658275"]
    max_fansnum  = es.search(index="user_information", doc_type="text", body = query_body)["aggregations"]["max_fansnum"]["value"]
    
    return max_fansnum

'''
domain:最终身份领域 topic
'''
def cal_importance(domain, topic_list, user_fansnum, fansnum_max):
    result = 0
    domain_result = 0
    domain_result = DOMAIN_WEIGHT_DICT[domain]
    print (domain_result)
    topic_result = 0
    try :
        for topic in topic_list:
            topic_result += TOPIC_WEIGHT_DICT[topic]
    except :
        topic_result = 0
    result = (IMPORTANCE_WEIGHT_DICT['fansnum']*math.log(float(user_fansnum)/ fansnum_max*9+1, 10) + \
            IMPORTANCE_WEIGHT_DICT['domain']*domain_result + IMPORTANCE_WEIGHT_DICT['topic']*(topic_result / 3))*100


    return result


#input: user_activeness_geo {geo1:count, geo2:count,...} for the latest dat  ,user_activeness_time {'statusnum':value, 'activity_time':value}
def get_day_activeness(user_day_activeness_geo, user_day_activeness_time,uid):
    result = 0
    # get day geo dict by ip-timestamp result
    max_freq = user_day_activeness_time[uid]['activity_time']

    statusnum = user_day_activeness_time[uid]['statusnum']
    activity_geo_count = len(user_day_activeness_geo.keys())
    result = activeness_weight_dict['activity_time'] * math.log(max_freq  + 1) + \
             activeness_weight_dict['activity_geo'] * math.log(activity_geo_count + 1) +\
             activeness_weight_dict['statusnum'] * math.log(statusnum + 1)
    return result




def get_day_activity_time(user_day_activity_time):
    results = {}
    activity_list_dict = {} # {uid:[activity_list]}
    uid = user_day_activity_time["uid"]
    activity_list_dict[uid] = []
                
    for i in range(0, 96):
        try:
            count = user_day_activity_time["time_segment"][i]
        except:
            count = 0
        activity_list_dict[uid].append(count)
    #print (activity_list_dict)
    activity_list = activity_list_dict[uid]
    statusnum = sum(activity_list)

    signal = np.array(activity_list)

    fftResult = np.abs(np.fft.fft(signal))**2
    n = signal.size
    freq = np.fft.fftfreq(n, d=1)
    i = 0
    max_val = 0
    max_freq = 0
    for val in fftResult:
        if val>max_val and freq[i]>0:
            max_val = val
            max_freq = freq[i]
        i += 1

    results[uid] = {'statusnum': statusnum, 'activity_time': math.log(max_freq + 1)}
    
    return results
    #{uid: {'activity_time':x, 'statusnum':y}}


def get_queue_index(timestamp):
    time_struc = time.gmtime(float(timestamp))
    hour = time_struc.tm_hour
    minute = time_struc.tm_min
    index = hour*4+math.ceil(minute/15.0) #every 15 minutes
    return int(index)


def judge_user_weibo_rel_exist(uid):#判断此条微博用户 微博关系信息是否存在
    try:#判断此条微博用户 微博关系信息是否存在 
        weibo_rel_exist = es.get(index="user_weibo_relation_info", doc_type="text",id = uid)#ruocunzai
        return True
    except:
        es.index(index = "user_weibo_relation_info",doc_type="text",id = uid,body = {"uid":uid,"fans_num":0,"friends_num":0,\
  "origin_weibo":[],"origin_weibo_be_comment":[],"origin_weibo_be_retweet":[],"comment_weibo":[],\
  "retweeted_weibo":[],"retweeted_weibo_be_retweet":[],"retweeted_weibo_be_comment":[]})
        return True

def cal_user_weibo_relation_info(item):
    uid = int(item['uid'])#用户uid
    if judge_user_weibo_rel_exist(uid):#此条微博用户已经具有表 拿出此条数据
        uid_es_result =es.get(index="user_weibo_relation_info", doc_type="text",id = uid)["_source"]
        fans_num = item['user_fansnum']
        #friends_count = item.get("user_friendsnum", 0)关注数没有
        es.update(index="user_weibo_relation_info", doc_type="text",id =uid,body= {"doc":{"fans_num":fans_num}})
        retweeted_uid = item['root_uid']
        retweeted_mid = item['root_mid']

        message_type = int(item['message_type'])
        mid = item['mid']
        timestamp = item['timestamp']
        text = item['text']

        if message_type == 1:
            origin_weibo_dict = {}
            origin_weibo_dict["mid"] = mid
            origin_weibo_dict["retweet_num"] = 0
            origin_weibo_dict["comment_num"] = 0
            origin_weibo_dict["timestamp"] = timestamp
            uid_es_result["origin_weibo"].append(origin_weibo_dict)
            es.update(index="user_weibo_relation_info", doc_type="text",id =uid,body= {"doc":{"origin_weibo":uid_es_result["origin_weibo"]}})
 
            
        elif message_type == 2: # comment weibo 评论微博
            
            #if cluster_redis.sismember(user + '_comment_weibo', retweeted_mid):
                #return 
            if retweeted_mid in uid_es_result["comment_weibo"]:#此条微博已经被记录过 pass
                return
            if retweeted_uid =="":
                return 
            uid_es_result["comment_weibo"].append(retweeted_mid)
            es.update(index="user_weibo_relation_info", doc_type="text",id =uid,body= {"doc":{"comment_weibo":uid_es_result["comment_weibo"]}})
            #cluster_redis.sadd(user + '_comment_weibo', retweeted_mid)
            RE = re.compile(u'//@([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+):', re.UNICODE)
            nicknames = RE.findall(text)
            queue_index = get_queue_index(timestamp)
            #cluster_redis.hincrby(user, 'comment_weibo', 1) len(uid_es_result["comment_weibo"])

            #if 1:
            if len(nicknames) == 0:#评论的为他人原创 需更新root_uid的信息 
                if judge_user_weibo_rel_exist(retweeted_uid):#判断此人是否有信息表 给其建立表
                    retweeted_uid_es_result = es.get(index="user_weibo_relation_info", doc_type="text",id = retweeted_uid)["_source"]
                    mid_list = []
                    for origin_item in retweeted_uid_es_result["origin_weibo"]:#dict
                        mid_list.append(origin_item["mid"])#获取当前全部mid
                    if retweeted_mid not in mid_list: #当前帖子没被记录过
                        origin_weibo_dict = {}
                        origin_weibo_dict["mid"] = retweeted_mid
                        origin_weibo_dict["retweet_num"] = 0
                        origin_weibo_dict["comment_num"] = 1
                        origin_weibo_dict["timestamp"] = timestamp
                        retweeted_uid_es_result["origin_weibo"].append(origin_weibo_dict)

                        origin_weibo_be_comment_dict = {}
                        origin_weibo_be_comment_dict["queue_index"] = queue_index
                        origin_weibo_be_comment_dict["value"] = 1
                        origin_weibo_be_comment_dict["timestamp"] = timestamp
                        retweeted_uid_es_result["origin_weibo_be_comment"].append(origin_weibo_be_comment_dict)
                        es.update(index="user_weibo_relation_info", doc_type="text",id =retweeted_uid,body= {"doc":{"origin_weibo":retweeted_uid_es_result["origin_weibo"],"origin_weibo_be_comment":retweeted_uid_es_result["origin_weibo_be_comment"]}})
                    else :#当前帖子被记录过
                        update_list_1 = []
                        update_list_2 = []
                        for j,_ in enumerate(retweeted_uid_es_result["origin_weibo"]):
                            if _["mid"] != retweeted_mid:
                                update_list_1.append(_)
                            else:
                                new_comment_num = _["comment_num"] + 1
                                _.update(comment_num=new_comment_num,timestamp=timestamp)
                                update_list_1.append(_)
                        es.update(index="user_weibo_relation_info", doc_type="text",id =retweeted_uid ,body = {"doc":{"origin_weibo":update_list_1}})
                        for i,_ in enumerate(retweeted_uid_es_result["origin_weibo_be_comment"]):
                            if _["queue_index"]!= queue_index:
                                update_list_2.append(_)
                            else:
                                new_queue_index = _["queue_index"] + 1
                                _.update(queue_index=new_queue_index)
                                update_list_2.append(_)
                        es.update(index="user_weibo_relation_info", doc_type="text",id =retweeted_uid ,body = {"doc":{"origin_weibo_be_comment":update_list_2}})
                       
                
            else: #中间被人转发过
                nick_id = nicknames[0]#转发人名称
                query_body = {"query": {"bool": {"must": [{"term": {"name": nick_id}}]}},"size": 10}
                result = es.search(index="weibo_user", doc_type="type1", body=query_body)["hits"]["hits"]
                if len(result)!= 0:#查到此用户
                    middle_uid = result[0]["_id"]
                    #cluster_redis.hincrby(str(_id), retweeted_mid + '_retweeted_weibo_comment', 1) 
                    #cluster_redis.hincrby(str(_id), 'retweeted_weibo_comment_timestamp_%s' % queue_index, 1)
                    #cluster_redis.hset(str(_id), retweeted_mid + '_retweeted_weibo_comment_timestamp', timestamp)
                    if judge_user_weibo_rel_exist(middle_uid):#判断此人是否有信息表 给其建立表
                        middle_uid_es_result = es.get(index="user_weibo_relation_info", doc_type="text",id = middle_uid)["_source"]
                        mid_list = []
                        for retweet_item in middle_uid_es_result["retweeted_weibo"]:#dict
                            mid_list.append(retweet_item["mid"])#获取当前全部mid
                        if retweeted_mid not in mid_list: #当前帖子没被记录过
                            retweeted_weibo_dict = {}
                            retweeted_weibo_dict["mid"] = retweeted_mid
                            retweeted_weibo_dict["retweet_num"] = 0
                            retweeted_weibo_dict["comment_num"] = 1
                            retweeted_weibo_dict["timestamp"] = timestamp
                            middle_uid_es_result["retweeted_weibo"].append(retweeted_weibo_dict)
                            retweeted_weibo_be_comment_dict = {}
                            retweeted_weibo_be_comment_dict["queue_index"] = queue_index
                            retweeted_weibo_be_comment_dict["value"] = 1
                            retweeted_weibo_be_comment_dict["timestamp"] = timestamp
                            middle_uid_es_result["retweeted_weibo_be_comment"].append(retweeted_weibo_be_comment_dict)
                            es.update(index="user_weibo_relation_info", doc_type="text",id =middle_uid,body= {"doc":{"retweeted_weibo":middle_uid_es_result["retweeted_weibo"],"retweeted_weibo_be_comment":middle_uid_es_result["retweeted_weibo_be_comment"]}})
                        else :#当前帖子被记录过
                            update_list_1 = []
                            update_list_2 = []
                            for j,_ in enumerate(middle_uid_es_result["retweeted_weibo"]):
                                if _["mid"] != retweeted_mid:
                                    update_list_1.append(_)
                                else:
                                    new_comment_num = _["comment_num"] + 1
                                    _.update(comment_num=new_comment_num,timestamp=timestamp)
                                    update_list_1.append(_)
                            es.update(index="user_weibo_relation_info", doc_type="text",id =middle_uid ,body = {"doc":{"retweeted_weibo":update_list_1}})
                            for i,_ in enumerate(middle_uid_es_result["retweeted_weibo_be_comment"]):
                                if _["queue_index"]!= queue_index:
                                    update_list_2.append(_)
                                else:
                                    new_queue_index = _["queue_index"] + 1
                                    _.update(queue_index=new_queue_index)
                                    update_list_2.append(_)
                            es.update(index="user_weibo_relation_info", doc_type="text",id =middle_uid ,body = {"doc":{"retweeted_weibo_be_comment":update_list_2}})


        elif message_type == 3:
            #cluster_redis.sadd('user_set', user)
            #if cluster_redis.sismember(user + '_retweeted_weibo', retweeted_mid):
                #return
            
            mid_list = []
            for retweet_item in uid_es_result["retweeted_weibo"]:#dict
                mid_list.append(retweet_item["mid"])#获取当前全部mid
            if retweeted_mid in mid_list:#此条微博已经被记录过 pass
                return
            if retweeted_uid =="":
                return

            #cluster_redis.sadd(user + '_retweeted_weibo', retweeted_mid)
            #cluster_redis.hset(user, retweeted_mid + '_retweeted_weibo_timestamp', timestamp) 
            #cluster_redis.hset(user, retweeted_mid + '_retweeted_weibo_retweeted', 0)
            #cluster_redis.hset(user, retweeted_mid + '_retweeted_weibo_comment', 0)

            retweeted_weibo_dict = {}
            retweeted_weibo_dict["mid"] = retweeted_mid
            retweeted_weibo_dict["retweet_num"] = 0
            retweeted_weibo_dict["comment_num"] = 0
            retweeted_weibo_dict["timestamp"] = timestamp
            uid_es_result["retweeted_weibo"].append(retweeted_weibo_dict)
            es.update(index="user_weibo_relation_info", doc_type="text",id =uid,body= {"doc":{"retweeted_weibo":uid_es_result["retweeted_weibo"]}})
            

            queue_index = get_queue_index(timestamp)

            #cluster_redis.hincrby(retweeted_uid, 'origin_weibo_retweeted_timestamp_%s' % queue_index, 1)
            #cluster_redis.hincrby(retweeted_uid, retweeted_mid + '_origin_weibo_retweeted', 1) 
            
            if judge_user_weibo_rel_exist(retweeted_uid):#判断此人是否有信息表 给其建立表
                retweeted_uid_es_result = es.get(index="user_weibo_relation_info", doc_type="text",id = retweeted_uid)["_source"]
                mid_list = []
                for origin_item in retweeted_uid_es_result["origin_weibo"]:#dict
                    mid_list.append(origin_item["mid"])#获取当前全部mid
                if retweeted_mid not in mid_list: #当前帖子没被记录过
                    origin_weibo_dict = {}
                    origin_weibo_dict["mid"] = retweeted_mid
                    origin_weibo_dict["retweet_num"] = 1
                    origin_weibo_dict["comment_num"] = 0
                    origin_weibo_dict["timestamp"] = timestamp
                    retweeted_uid_es_result["origin_weibo"].append(origin_weibo_dict)

                    origin_weibo_be_retweet_dict = {}
                    origin_weibo_be_retweet_dict["queue_index"] = queue_index
                    origin_weibo_be_retweet_dict["value"] = 1
                    origin_weibo_be_retweet_dict["timestamp"] = timestamp
                    retweeted_uid_es_result["origin_weibo_be_retweet"].append(origin_weibo_be_retweet_dict)
                    es.update(index="user_weibo_relation_info", doc_type="text",id =retweeted_uid,body= {"doc":{"origin_weibo":retweeted_uid_es_result["origin_weibo"],"origin_weibo_be_retweet":retweeted_uid_es_result["origin_weibo_be_retweet"]}})
                else :#当前帖子被记录过
                    update_list_1 = []
                    update_list_2 = []
                    for j,_ in enumerate(retweeted_uid_es_result["origin_weibo"]):
                        if _["mid"] != retweeted_mid:
                            update_list_1.append(_)
                        else:
                            new_retweet_num = _["retweet_num"] + 1
                            _.update(retweet_num=new_retweet_num,timestamp=timestamp)
                            update_list_1.append(_)
                    es.update(index="user_weibo_relation_info", doc_type="text",id =retweeted_uid ,body = {"doc":{"origin_weibo":update_list_1}})
                    for i,_ in enumerate(retweeted_uid_es_result["origin_weibo_be_retweet"]):
                        if _["queue_index"]!= queue_index:
                            update_list_2.append(_)
                        else:
                            new_queue_index = _["queue_index"] + 1
                            _.update(queue_index=new_queue_index)
                            update_list_2.append(_)
                    es.update(index="user_weibo_relation_info", doc_type="text",id =retweeted_uid ,body = {"doc":{"origin_weibo_be_retweet":update_list_2}})
                       
            RE = re.compile(u'//@([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+):', re.UNICODE)
            nicknames = RE.findall(text)
            if len(nicknames) != 0:
                for nick_id in nicknames:
                    query_body = {"query": {"bool": {"must": [{"term": {"name": nick_id}}]}},"size": 10}
                    result = es.search(index="weibo_user", doc_type="type1", body=query_body)["hits"]["hits"]
                    if len(result)!= 0:#查到此用户
                        middle_uid = result[0]["_id"]
                    
                        #cluster_redis.hincrby(str(_id), retweeted_mid+'_retweeted_weibo_retweeted', 1) 
                        #cluster_redis.hset(str(_id), retweeted_mid+'_retweeted_weibo_retweeted_timestamp', timestamp)
                        #cluster_redis.hincrby(str(_id), 'retweeted_weibo_retweeted_timestamp_%s' % queue_index, 1)
                        if judge_user_weibo_rel_exist(middle_uid):#判断此人是否有信息表 给其建立表
                            middle_uid_es_result = es.get(index="user_weibo_relation_info", doc_type="text",id = middle_uid)["_source"]
                            mid_list = []
                            for retweet_item in middle_uid_es_result["retweeted_weibo"]:#dict
                                mid_list.append(retweet_item["mid"])#获取当前全部mid
                            if retweeted_mid not in mid_list: #当前帖子没被记录过
                                retweeted_weibo_dict = {}
                                retweeted_weibo_dict["mid"] = retweeted_mid
                                retweeted_weibo_dict["retweet_num"] = 1
                                retweeted_weibo_dict["comment_num"] = 0
                                retweeted_weibo_dict["timestamp"] = timestamp
                                middle_uid_es_result["retweeted_weibo"].append(retweeted_weibo_dict)
                                retweeted_weibo_be_retweet_dict = {}
                                retweeted_weibo_be_retweet_dict["queue_index"] = queue_index
                                retweeted_weibo_be_retweet_dict["value"] = 1
                                retweeted_weibo_be_retweet_dict["timestamp"] = timestamp
                                middle_uid_es_result["retweeted_weibo_be_retweet"].append(retweeted_weibo_be_retweet_dict)
                                es.update(index="user_weibo_relation_info", doc_type="text",id =middle_uid,body= {"doc":{"retweeted_weibo":middle_uid_es_result["retweeted_weibo"],"retweeted_weibo_be_retweet":middle_uid_es_result["retweeted_weibo_be_retweet"]}})
                            else :#当前帖子被记录过
                                update_list_1 = []
                                update_list_2 = []
                                for j,_ in enumerate(middle_uid_es_result["retweeted_weibo"]):
                                    if _["mid"] != retweeted_mid:
                                        update_list_1.append(_)
                                    else:
                                        new_retweet_num = _["retweet_num"] + 1
                                        _.update(retweet_num=new_retweet_num,timestamp=timestamp)
                                        update_list_1.append(_)
                                es.update(index="user_weibo_relation_info", doc_type="text",id =middle_uid ,body = {"doc":{"retweeted_weibo":update_list_1}})
                                for i,_ in enumerate(middle_uid_es_result["retweeted_weibo_be_retweet"]):
                                    if _["queue_index"]!= queue_index:
                                        update_list_2.append(_)
                                    else:
                                        new_queue_index = _["queue_index"] + 1
                                        _.update(queue_index=new_queue_index)
                                        update_list_2.append(_)
                                es.update(index="user_weibo_relation_info", doc_type="text",id =middle_uid ,body = {"doc":{"retweeted_weibo_be_retweet":update_list_2}})

def influence_weibo_cal(total_number, average_number, top_number,brust):
    influence_weibo = 0.5*math.log(int(total_number)+1) + 0.2*math.log(int(average_number)+1) +0.1*math.log(int(top_number)+1) + 0.1*math.log(10*brust[0]+1) +0.1*math.log(10*brust[1]+1)
    return influence_weibo

def influence_cal(origin_weibo_total_number, retweeted_weibo_total_number, user_fansnum, influence_origin_weibo_retweeted, influence_origin_weibo_comment, influence_retweeted_weibo_retweeted, influence_retweeted_weibo_comment):
    influence = 300*(0.15*(0.6*math.log(int(origin_weibo_total_number)+1)+0.3*math.log(int(retweeted_weibo_total_number)+1)+0.1*math.log(int(user_fansnum)+1))+0.85*(0.3*influence_origin_weibo_retweeted+0.3*influence_origin_weibo_comment+0.2*influence_retweeted_weibo_retweeted+0.2*influence_retweeted_weibo_comment))
    return influence

def deliver_weibo_brust(time_list, division=900, percent=0.5):

    time_list = [int(value) for value in time_list]
    max_value = max(time_list)
    if max_value <= 5:
        return 0, 0
    else:
        list_brust = [value for value in time_list if value >= percent*max_value]
        brust_time = len(list_brust)
        brust_velosity = sum(list_brust)/float(brust_time)
    return brust_time, brust_velosity


def activity_weibo(xx_weibo_be_xxx):

    user_weibo_timestamp = [0]*96
    if len(xx_weibo_be_xxx) != 0:
        for i ,_ in enumerate(xx_weibo_be_xxx):#dict
            user_weibo_timestamp[int(_["queue_index"])-1] = _["value"]

    weibo_brust = deliver_weibo_brust(user_weibo_timestamp)
    return weibo_brust


def cal_influence_index(uid):
    try:
        uid_es_result =es.get(index="user_weibo_relation_info", doc_type="text",id = uid)["_source"]
        
        origin_weibo_retweeted_detail={}
        origin_weibo_comment_detail = {}
        origin_weibo_retweeted_total_number = 0
        origin_weibo_comment_total_number = 0
        origin_weibo_retweeted_average_number = 0
        origin_weibo_comment_average_number = 0
        origin_weibo_retweeted_top = [("0", 0)]
        origin_weibo_comment_top = [("0", 0)]

        for i,origin_weibo_item in enumerate(uid_es_result["origin_weibo"]):#dict
            if origin_weibo_item["retweet_num"] != 0:
                origin_weibo_retweeted_total_number += origin_weibo_item["retweet_num"]
                origin_weibo_retweeted_detail[origin_weibo_item["mid"]] = origin_weibo_item["retweet_num"]
            if origin_weibo_item["comment_num"] != 0:
                origin_weibo_comment_total_number += origin_weibo_item["comment_num"]
                origin_weibo_comment_detail[origin_weibo_item["mid"]] = origin_weibo_item["comment_num"]

        origin_weibo_retweeted_average_number = origin_weibo_retweeted_total_number * 1.0/ len(uid_es_result["origin_weibo"])
        origin_weibo_comment_average_number = origin_weibo_comment_total_number * 1.0/ len(uid_es_result["origin_weibo"])
        if origin_weibo_retweeted_detail:
            order = sorted(origin_weibo_retweeted_detail.iteritems(), key=lambda x:x[1], reverse=True)
            origin_weibo_retweeted_top = order[0:3] # list of top 3 weibo
        if origin_weibo_comment_detail:
            order = sorted(origin_weibo_comment_detail.iteritems(), key=lambda x:x[1], reverse=True)
            origin_weibo_comment_top = order[0:3] # list of top 3 weibo

        retweeted_weibo_retweeted_detail={}
        retweeted_weibo_comment_detail = {}
        retweeted_weibo_retweeted_total_number = 0
        retweeted_weibo_comment_total_number = 0
        retweeted_weibo_retweeted_average_number = 0
        retweeted_weibo_comment_average_number = 0
        retweeted_weibo_retweeted_top = [("0", 0)]
        retweeted_weibo_comment_top = [("0", 0)]

        for i,retweeted_weibo_item in enumerate(uid_es_result["retweeted_weibo"]):#dict
            if retweeted_weibo_item["retweet_num"] != 0:
                retweeted_weibo_retweeted_total_number += retweeted_weibo_item["retweet_num"]
                retweeted_weibo_retweeted_detail[retweeted_weibo_item["mid"]] = retweeted_weibo_item["retweet_num"]
            if retweeted_weibo_item["comment_num"] != 0:
                retweeted_weibo_comment_total_number += retweeted_weibo_item["comment_num"]
                retweeted_weibo_comment_detail[retweeted_weibo_item["mid"]] = retweeted_weibo_item["comment_num"]

        retweeted_weibo_retweeted_average_number = retweeted_weibo_retweeted_total_number * 1.0/ len(uid_es_result["retweeted_weibo"])
        retweeted_weibo_comment_average_number = retweeted_weibo_comment_total_number * 1.0/ len(uid_es_result["retweeted_weibo"])
        if retweeted_weibo_retweeted_detail:
            order = sorted(retweeted_weibo_retweeted_detail.iteritems(), key=lambda x:x[1], reverse=True)
            retweeted_weibo_retweeted_top = order[0:3] # list of top 3 weibo
        if retweeted_weibo_comment_detail:
            order = sorted(retweeted_weibo_comment_detail.iteritems(), key=lambda x:x[1], reverse=True)
            retweeted_weibo_comment_top = order[0:3] # list of top 3 weibo

        origin_weibo_retweeted_brust= activity_weibo(uid_es_result["origin_weibo_be_retweet"])
        origin_weibo_comment_brust= activity_weibo(uid_es_result["origin_weibo_be_comment"])
        retweeted_weibo_retweeted_brust= activity_weibo(uid_es_result["retweeted_weibo_be_retweet"])
        retweeted_weibo_comment_brust= activity_weibo(uid_es_result["retweeted_weibo_be_comment"])

        influence_origin_weibo_retweeted = influence_weibo_cal(origin_weibo_retweeted_total_number, origin_weibo_retweeted_average_number, origin_weibo_retweeted_top[0][1],origin_weibo_retweeted_brust)

        influence_origin_weibo_comment = influence_weibo_cal(origin_weibo_comment_total_number, origin_weibo_comment_average_number, origin_weibo_comment_top[0][1], origin_weibo_comment_brust)

        influence_retweeted_weibo_retweeted = influence_weibo_cal(retweeted_weibo_retweeted_total_number, retweeted_weibo_retweeted_average_number, retweeted_weibo_retweeted_top[0][1], retweeted_weibo_retweeted_brust)

        influence_retweeted_weibo_comment = influence_weibo_cal(retweeted_weibo_comment_total_number, retweeted_weibo_comment_average_number, retweeted_weibo_comment_top[0][1], retweeted_weibo_retweeted_brust)
        
        origin_weibo_total_number = len(uid_es_result["origin_weibo"])
        retweeted_weibo_total_number = len(uid_es_result["retweeted_weibo"])
        user_fansnum = uid_es_result["fans_num"]

        influence = influence_cal(origin_weibo_total_number, retweeted_weibo_total_number, user_fansnum, influence_origin_weibo_retweeted, influence_origin_weibo_comment, influence_retweeted_weibo_retweeted, influence_retweeted_weibo_comment)
    
        return influence
    except:
        influence = 0
        return influence


# sensitive_words
def createWordTree():
    wordTree = [None for x in range(65536)]

    wordTree.append(0)
    nodeTree = [wordTree, 0]

    awords = []

    for b in open('sensitive_words.txt', 'r'):
        awords.append(b.strip().split('\t')[0])
        #所有敏感词列表
    #print(awords)

    for word in awords:
        temp = wordTree
        for a in range(0,len(word)):
            index = ord(word[a])
            print(index)
            if a < (len(word) - 1):
                if temp[index] == None:
                    node = [[None for x in range(65536)],0]

                    temp[index] = node
                elif temp[index] == 1:
                    node = [[None for x in range(65536)],1]

                    temp[index] = node
                
                temp = temp[index][0]
            else:
                temp[index] = 1
        
    return nodeTree 


def searchWord(text, nodeTree):#分词
    temp = nodeTree
    words = []
    word = []
    a = 0
    print(text)
    print(len(text))
    
    while a < len(text):
        index = ord(text[a])
        if index >= 63356:
            a = a + 1
            continue
        #print(index)
        
        temp = temp[0][index]
        if temp == None:
            temp = nodeTree
            a = a - len(word)
            word = []
        elif temp == 1 or temp[1] == 1:
            word.append(index)
            words.append(word)
            a = a - len(word) + 1 
            word = []
            temp = nodeTree
        else:
            word.append(index)
        a = a + 1
    
    map_words = {}
    print(words)

    for w in words:
        for x in w:
            print(chr(x))
        iter_word = "".join([chr(x) for x in w])
        print(iter_word)
        if not map_words.__contains__(iter_word):
            map_words[iter_word] = 1
        else:
            map_words[iter_word] = map_words[iter_word] + 1

    
    return map_words


def cal_sensitive(today_sensitive_words_dict):

    #print (aaa)
    #node = createWordTree()

    #sensitive_words_dict = searchWord(text.encode('utf-8', 'ignore'), node)

    sensitive_score_dict = { "1": 1,"2": 5,"3": 10}
    sensitive_words_weight = dict()
    for b in open('sensitive_words.txt', 'r'):
        word = b.strip().split('\t')[0]
        weight =  b.strip().split('\t')[1]
        sensitive_words_weight[word] =  weight
    #print(sensitive_words_weight)
    score = 0
    if today_sensitive_words_dict:
        for k,v in today_sensitive_words_dict.items():
            #print(type(k))
            tmp_stage = sensitive_words_weight.get(k, 0)

            if tmp_stage:
                score += v*sensitive_score_dict[str(tmp_stage)]

    return score

def cal_user_influence(uid,weibo_data_dict):
    for day,weibo_list in weibo_data_dict.items():#value 为列表  key为日期
        es_timestamp = date2ts(day)
        sum_r = len(weibo_list)
        id_es = str(uid) +"_" + str(es_timestamp)
        importance = 0
        sensitive = 0.0
        activeness = 0
        influence = 0

        ####重要度计算 要在user_domain_topic后计算重要度
        max_fansnum = get_max_fansnum()
        try:
            domain_topic_result = es.get(index="user_domain_topic", doc_type="text", id = id_es)["_source"]
            topic_list = []
            for key in domain_topic_result.keys():
                if "topic_" in key:
                    value = float(domain_topic_result[key])
                    if value > 0:
                        topic_list.append(key)
            domain = domain_topic_result["main_domain"]
            user_info = es.get(index="user_information", doc_type="text", id = uid)["_source"]
            user_fansnum = user_info["fans_num"]
            importance = cal_importance(domain, topic_list, user_fansnum, max_fansnum)
            
        except:
            importance = 0
        #####重要度计算结束

        ####影响力计算 
        influence = cal_influence_index(uid)
        ####影响力计算结束

        if sum_r :#此天有微博数据
            ###活跃度计算准备条件
            user_day_activity_time = {}
            user_day_activity_time["uid"] = uid 
            user_day_activity_time["timestamp"] = es_timestamp
            time_segment_dict = {}
            user_day_activeness_geo = {}
            ####活跃度

            ###敏感度计算准备条件
            node = createWordTree()
            today_sensitive_words_dict = {}
            ####敏感度

            for weibo_item in weibo_list:#每一条微博
                ####活跃度过程计算
                timestamp = weibo_item["_source"]['timestamp']
                ts_1  = date2ts(ts2date(timestamp)) 
                time_segment = (timestamp - ts_1) / Fifteenminutes
                if time_segment not in time_segment_dict:
                    time_segment_dict[time_segment] = 1
                else:
                    time_segment_dict[time_segment] += 1
                geo = weibo_item["_source"]['geo']
                if geo not in user_day_activeness_geo:
                    user_day_activeness_geo[geo] = 1
                else:
                    user_day_activeness_geo[geo] += 1
                ###
                ###敏感度过程计算
                text = weibo_item["_source"]['text']
                sensitive_words_dict = searchWord(text, node)
                for word in sensitive_words_dict :
                    if word not in today_sensitive_words_dict:
                        today_sensitive_words_dict[word] = 1
                ###

            #####遍历完一天全部微博后的操作
            #user_day_activeness_geo :{u'\u4e2d\u56fd&\u5c71\u897f&\u4e34\u6c7e': 4}
            user_day_activity_time["time_segment"] = time_segment_dict
            #user_day_activity_time : {'timestamp': 1478448000, 'uid': '2396658275', 'time_segment': {93: 2, 94: 2}})
            user_day_activeness_time = get_day_activity_time(user_day_activity_time)
            #user_day_activeness_time:{'2396658275': {'activity_time': 0.010362787035546658, 'statusnum': 4}}
            
            ## 活跃度最终结果
            activeness = get_day_activeness(user_day_activeness_geo,user_day_activeness_time,uid)
            ## 敏感度最终结果
            sensitive = cal_sensitive(today_sensitive_words_dict)
            
        else:
            ###当天没有发微博数据的情况
            activeness = 0
            sensitive = 0.0

        #print(uid,es_timestamp,activeness,sensitive,importance,influence)
        es.index(index = "user_influence",doc_type = "text",id = id_es, body ={"uid": uid,"timestamp": es_timestamp,"date": day,"importance_normalization": 0,"influence_normalization": 0,"activity_normalization": 0,"sensitivity_normalization": 0,"activity": activeness,"sensitivity":sensitive,"importance":importance,"influence":influence})


if __name__ == '__main__':
    pass 
