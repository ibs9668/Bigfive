# -*- coding: UTF-8 -*-

import os
import time
import numpy as np
import math
import re


import sys
sys.path.append('../../../')
from config import *
from time_utils import *


def get_queue_index(timestamp):
    time_struc = time.gmtime(float(timestamp))
    hour = time_struc.tm_hour
    minute = time_struc.tm_min
    index = hour*4+math.ceil(minute/15.0) #every 15 minutes
    return int(index)


def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    #print (uid_list)
    return uid_list


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



def get_infludece_index(uid_list,ES_INDEX_LIST):
    for j in ES_INDEX_LIST:
        for n,user in enumerate(uid_list):#一个索引为一天
            query_body = {
                "query": {
                    "bool": {
                    "must":[{
                        "term": {
                            "uid": user
                        }}]
                    }},
                "size":10000
            }
            result_weibo = es_weibo.search(index=j, doc_type="text", body=query_body)["hits"]["hits"]
            if len(result_weibo) != 0:
                #统计用户每条微博的转发关系 为了影响力
                for i ,weiboinfo in enumerate(result_weibo):
                    cal_user_weibo_relation_info(weiboinfo["_source"])#统计用户每条微博的转发关系
            print (user)
        for i,_ in enumerate(uid_list):#一个索引为一天
            es_timestamp = date2ts(j.split("_")[-1])
            influence = cal_influence_index(_)
            print (_,influence)
            id_es = str(_) +"_" + str(es_timestamp)
            es.update(index = "user_influence",doc_type = "text",id = id_es, body = {"doc":{"influence":influence}})




if __name__ == '__main__':

    #uid_list = [u'2061250093', u'1732637974', u'1496985147', u'1163566787', u'2215605707', u'2484854632', u'1919316512', u'2004328542', u'1670815317', u'1697587822', u'1792560981', u'1711692405', u'2277992341', u'2690122393', u'1708919080', u'1600058913', u'1464631973', u'2606892862', u'2143949340', u'2373295690', u'1780288902', u'1768405100', u'1192216061', u'2706112830', u'2693155673', u'2458761340', u'2395216530', u'1766382225', u'2261214681', u'1765367445', u'1841499435', u'1937686044', u'1750048972', u'1873564283', u'1368363504', u'2499731447', u'1882630570', u'1044547635', u'1233705802', u'1261543734', u'1321417737', u'1960846257', u'1854846587', u'1581916632', u'1819843822', u'2419769870', u'2119892055', u'2278565651', u'2294455022', u'1621205852', u'1960035641', u'2120183513', u'1277948651', u'1595970927', u'1977614194', u'1305458780', u'1817520981', u'1826114715', u'2492803622', u'2876992347', u'2738547280', u'1407653637', u'2280810463', u'2683817863', u'2885306274', u'2837502200', u'2623758953', u'2218796512', u'2203116712', u'1833285262', u'2574958892', u'2391483812', u'2550053697', u'2839595794', u'2182756300', u'2430959095', u'2815141844', u'2618420511', u'2459749574', u'1931046815', u'2095204551', u'1250924423', u'1650247615', u'3025361751', u'2281980783', u'2598989305', u'2838508040', u'2689186111', u'1570777113', u'2687353254', u'2216012354', u'2885975524', u'3211778843', u'2430801272', u'1878326131', u'2032212537', u'2197408652', u'2858646005', u'1915690151', u'2901244615', u'1678122810', u'1924764862', u'1191617047', u'1848802707', u'1761978824', u'1862654581', u'2500319980', u'1744990763', u'1373007890', u'1748616307', u'1678312093', u'2684929823', u'1310456570', u'1761710404', u'2519487853', u'1807654580', u'1838009963', u'1970407665', u'2500351800', u'1812570123', u'1069716200', u'2198366090', u'1946043297', u'2886299324', u'2713141523', u'1705330725', u'1903250833', u'2002274681', u'2218745312', u'3189647102', u'2490788685', u'2696481104', u'2288119482', u'3162600794', u'1937197023', u'1694249707', u'2727350665', u'1718922271', u'2351454621', u'3210088165', u'1914697577', u'2354820605', u'2709872580', u'1339796057', u'1676416790', u'2061785230', u'1048661441', u'3202584435', u'1680212422', u'1683591440', u'1912573740', u'2311613450', u'2694985291', u'1773414995', u'2506871382', u'2806726610', u'1792448581', u'1658752217', u'2171306135', u'1937592587', u'1283702697', u'2355776262', u'1767005912', u'1811473435', u'2809724464', u'2291828917', u'2281910103', u'3190238250', u'2596087954', u'1569970122', u'3189359872', u'3192566164', u'3188000542', u'2336844811', u'3168364473', u'3176017093', u'2154425591', u'2473543467', u'2391563912', u'2794575021', u'1377377471', u'2473922027', u'3037195462', u'2152686560', u'2201891555', u'1731710474', u'1398481831', u'1824979017', u'1927959443', u'2824109237', u'1822581781', u'1765507015', u'2679165143', u'1727977942', u'1868653803', u'2016894413', u'3192006204', u'2950837580', u'1081103485', u'1298743060', u'2386107652', u'1215708964', u'1756892997', u'2885184404', u'2542891701', u'1642423695', u'2885210944', u'1780433665', u'1952544431', u'1793575861', u'2990769151', u'1839853771', u'2720573953', u'1222755274', u'2090937623', u'3203050172', u'1758838865', u'1907313744', u'1766550132', u'1796709875', u'1374306401', u'2808320487', u'2817297204', u'1749840877', u'1783787910', u'2630330503', u'1077899370', u'3130804401', u'2671972067', u'1757461781', u'1886617701', u'2683118780', u'2433138150', u'2809889004', u'2796972862', u'2610038031', u'2664345931', u'2641003894', u'2642802532', u'2808858274', u'2692302033', u'2693301423', u'1141180955', u'2609988223', u'1922024974', u'2096166922', u'1801548064', u'2891651531', u'1655568350', u'2689012234', u'2060416163', u'2647677180', u'2135599165', u'2786530174', u'1735609302', u'1770579454', u'1282260443', u'1731371081', u'2694173841', u'2649443551', u'1607391665', u'2693204273', u'2693916911', u'1890565997', u'2612128105', u'1750996695', u'1649262787', u'2850885000', u'2386684732', u'2814761560', u'1581121011', u'2181231640', u'2134951535', u'1405885274', u'1822231191', u'1625452457', u'1824262277', u'2714874593', u'2809646714', u'2693890521', u'1974976653', u'1644513522', u'2476928055', u'1842291705', u'2706792310', u'2686819421', u'2317091885', u'1053589610', u'3062184497', u'1788158701', u'2283030274', u'2693324033', u'2693084163', u'3036523662', u'2693136293', u'2252337644', u'1841443932', u'3050911055', u'2820583063', u'1289178810', u'2053404880', u'1891674357', u'2823344727', u'2607581295', u'2440443320', u'2671564631', u'2786399804', u'2401736033', u'2654263940', u'2413689811', u'1787246017', u'2161206197', u'2641401524', u'2080263075', u'2861968794', u'2193810117', u'2499405244', u'1732649854', u'2653249043', u'2598818662', u'1878229657', u'2278852414', u'2429774301', u'2419784070', u'2255908122', u'1706200670', u'2552079792', u'2084348103', u'1771471017', u'2885173844', u'2802787432', u'2885204194', u'2630296293', u'2885137004', u'1594114140', u'2529379527', u'1947386307', u'1627720327', u'2367603147', u'2417525902', u'2588351037', u'2049561621', u'2414567625', u'2959256850', u'2803045732', u'3049173657', u'1827149272', u'2634655141', u'2814001810', u'1828657872', u'2375049194', u'2481448734', u'1450252421', u'2693958641', u'2713551683', u'2817337574', u'2065467572', u'2712530752', u'2792938504', u'2891550101', u'2709423953', u'2606002492', u'2645581775', u'2341439593', u'1792571147', u'2693178613', u'2520514175', u'1891703137', u'3064635297', u'2327289553', u'1650722155', u'2467486894', u'3051602983', u'1910792283', u'2279614662', u'1750184632', u'2701251924', u'3190780720', u'3188240802', u'1834762085', u'3194199312', u'2593614123', u'3208376674', u'3185979337', u'3223693447', u'3200710175', u'1838992310', u'1949806182', u'2684021720', u'1271980112', u'1634867914', u'2797870235', u'1260589201', u'1793563424', u'1649485327', u'1527933561', u'3188894332', u'3209924964', u'1863190965', u'1705991685', u'2815028934', u'2575807432', u'2874723143', u'2915291661', u'1613073235', u'2850851020', u'1414982995', u'2456443413', u'2076347913', u'2634527561', u'3189476392', u'2291059334', u'1880204903', u'2310157830', u'2115990470', u'2676713353', u'3189422112', u'1886350301', u'2885167734', u'2392409042', u'1216877104', u'2860247094', u'1615092293', u'1534925721', u'2413810411', u'1440838580', u'2790320940', u'3194222512', u'2012396262', u'2506619592', u'1706217473', u'2627531171', u'1791444510', u'3180304332', u'1880439740', u'2945083414', u'2692473240', u'2236146673', u'1840089485', u'1764722644', u'2034211525', u'1403535330', u'1800288474', u'1871883515', u'2681690432', u'1080028685', u'2422410855', u'1773724762', u'1841674385', u'1776397143', u'2715102733', u'1772129642', u'1251842443', u'1771541997', u'2386301172', u'1824764487', u'1627741981', u'1826664582', u'1627623444', u'1791473393', u'1259864220', u'1716604270', u'1999458037', u'1684314040', u'1582590235', u'3215027891', u'1430817252', u'1818241007', u'1854744964', u'1718784241', u'2344251667', u'1864397062', u'2044989233', u'1870823825', u'1756647981', u'1748493104', u'1877031977', u'1175058733', u'1705604005', u'1767044465', u'2115446980', u'1552832452', u'2018111394', u'1808642794', u'2514811655', u'1063227324', u'1964577042', u'1690903500', u'1764065424', u'1752487513', u'3226893262', u'1642127292', u'1731225391', u'1747828494', u'1719625807', u'2261148931', u'1808734844', u'1776677383', u'2543702947', u'1548232220']
    #print len(uid_list)
    #uid_list = get_uidlist()
    uid_list = ["2146717162"]
    ES_INDEX_LIST = ["flow_text_2016-11-13"]
    get_infludece_index(uid_list,ES_INDEX_LIST)
