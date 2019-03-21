# -*- coding: UTF-8 -*-

import sys
sys.path.append("../")
sys.path.append("../../")


from config import *
from time_utils import *
from global_utils import *



def get_user_ranking():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}}}
    sort_dict = {"_id":{"order":"asc"}}
    ESIterator2 = ESIterator(0,sort_dict,1000,USER_RANKING,"text",query_body,es)
    uidlist = []
    while True:
        try:
            es_result = next(ESIterator2)
            for i in es_result:
                uidlist.append(i["_id"])
        except StopIteration:
            break
    
    return uidlist
    


def get_politics_user(politics_id,politic_mapping_name):
    uidlist = get_user_ranking()
    sort_dict = {"_id":{"order":"asc"}}
    query_body = {
        "query":{
            "bool":{
                "must":[
                    {"match_all": { }
                    }
                ]
            }
        }
    }

    ESIterator1 = ESIterator(0,sort_dict,1000,politic_mapping_name,"text",query_body,es)


    mid_user = {}
    uid_user = {}
    mid_user = {"positive":{"bigv_user":[],"ordinary_user":[]},"negative":{"bigv_user":[],"ordinary_user":[]}}
    uid_user = {"p_bigv_user":[],"p_ordinary_user":[],"n_bigv_user":[],"n_ordinary_user":[]}
    personality_label_list = ["machiavellianism_label","narcissism_label","psychopathy_label","extroversion_label","nervousness_label","openn_label","agreeableness_label","conscientiousness_label"]

    while True:
        try:
            es_result = next(ESIterator1)
            #print(len(es_result))
            #print(es_result[0])
            for item in es_result:
                if item["_source"]["sentiment"] != 0:
                    if item["_source"]["sentiment"] == 1: #积极用户
                        if item["_source"]["user_fansnum"] >= 1000:
                            mid_user["positive"]["bigv_user"].append(item["_id"])
                            if item["_source"]["uid"] in uidlist and item["_source"]["uid"] not in uid_user["p_bigv_user"]:
                                uid_user["p_bigv_user"].append(item["_source"]["uid"])
                        else:
                            mid_user["positive"]["ordinary_user"].append(item["_id"])
                            if item["_source"]["uid"] in uidlist and item["_source"]["uid"] not in uid_user["p_ordinary_user"]:
                                uid_user["p_ordinary_user"].append(item["_source"]["uid"])
                    else:#消极用户
                        if item["_source"]["user_fansnum"] >= 1000:
                            mid_user["negative"]["bigv_user"].append(item["_id"])
                            if item["_source"]["uid"] in uidlist and item["_source"]["uid"] not in uid_user["n_bigv_user"]:
                                uid_user["n_bigv_user"].append(item["_source"]["uid"])
                        else:
                            mid_user["negative"]["ordinary_user"].append(item["_id"])
                            if item["_source"]["uid"] in uidlist and item["_source"]["uid"] not in uid_user["n_ordinary_user"]:
                                uid_user["n_ordinary_user"].append(item["_source"]["uid"])
                else:
                    pass
        except StopIteration:
            #遇到StopIteration就退出循环
            break
    #print(mid_user)
    
    
    
    for user,uid_list in uid_user.items():#一个遍历一个类型
        #print(type(uid_list))
        #print(user,uid_list)
        personality_dict = {}
        if len(uid_list):
            personality_result = es.mget(index=USER_RANKING,doc_type="text",body = {"ids":uid_list} )['docs']
            for user_item in personality_result:
                for personality_label in personality_label_list:
                    if personality_label not in personality_dict:
                        personality_dict[personality_label] = {"low":0,"high":0}#字典初始化
                    else:
                        pass
                    #map_dic = {0:'low',2:'high',1:"middle"}
                    if user_item["_source"][personality_label] == 0:
                        personality_dict[personality_label]["low"] += 1
                    elif user_item["_source"][personality_label] == 2:
                        personality_dict[personality_label]["high"] += 1
        else:
            for personality_label in personality_label_list:
                personality_dict[personality_label] = {"low":0,"high":0}

            #print(personality_result)
        #print(user,len(uid_list),personality_dict)
        sentiment = user.split("_")[0]
        user_type = user.split("_")[1]
        es_dict = {}
        es_dict["politics_id"] = politics_id 
        if sentiment == "n" :#消极
            es_dict["sentiment"] = "negative"
        else:
            es_dict["sentiment"] = "positive"
        if user_type == "bigv":
            es_dict["user_type"] = "BigV"
        else:
            es_dict["user_type"] = "ordinary"
        es_dict = dict(es_dict,**personality_dict)
        id_es = politics_id + "_"+sentiment +"_"+ user_type
        print(es_dict)
        es.index(index ="politics_personality",doc_type = "text",id = id_es,body = es_dict)
    return mid_user
            

        
    
if __name__ == "__main__":
    '''
    s_t = time.time()
    get_politics_user("ceshizhengceyi_1552983497","politics_ceshizhengceyi_1552983497")
    e_t = time.time()
    print ("time",e_t - s_t)
    s_t1 = time.time()
    get_politics_user("ceshizhengceer_1553060528","politics_ceshizhengceer_1553060528")
    e_t1 = time.time()
    print ("time",e_t1 - s_t1)
    '''
    pass


        

                


                    
                    
                    

