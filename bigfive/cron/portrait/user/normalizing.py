# -*- coding: UTF-8 -*-

import os
import numpy as np
import math

import sys
sys.path.append('../../../')
from config import *
from time_utils import *



def get_uidlist():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
    uid_list = []
    for es_item in es_result:
        uid_list.append(es_item["_id"])
    #print (uid_list)
    return uid_list

def new_mapping(uid_list):
    for i in uid_list:
        query_body = {"query": {"bool": {"must":{"term": {"uid":i}}}},"size" : 20000}
        user_info = es.search(index = "user_influence",doc_type = "text",body = query_body)["hits"]["hits"]
        for user in user_info:
            id_es = user["_id"]
            new_dict = {"importance_normalization":0,"influence_normalization":0,"activity_normalization":0,"sensitivity_normalization":0}
            old_dict = user["_source"]
            insert_dict = dict(new_dict,**old_dict)
            es.index(index = "user_influence",doc_type = "text",id = id_es,body =insert_dict )
            print(insert_dict)
            print (id_es)
        break
        

def normalize_influence_index():
    target_max = 100
    target_min = 0
    index_list = ["importance","influence","activity","sensitivity"]
    aggs_max_dict = {}
    aggs_max_dict = {"aggs": {"groupby": {"terms":{"field":"timestamp","size":15},"aggs":{"max_index":{"max":{}},"min_index":{"min":{}}}}}}
    for i in index_list :#对于每一个属性值
        #aggs_max_dict = {"aggs": {"index": {"terms":{"field":"timestamp"}}}}
        aggs_max_dict["aggs"]["groupby"]["aggs"]["max_index"]["max"]["field"] = i
        aggs_max_dict["aggs"]["groupby"]["aggs"]["min_index"]["min"]["field"] = i
        #print  (aggs_max_dict)
        max_min_index = es.search(index="user_influence", doc_type="text", body = aggs_max_dict)["aggregations"]["groupby"]["buckets"]
        for j in max_min_index: #每一天 的每一个属性的最值
            query_body = {}
            timestamp = j["key"]
            max_index = j["max_index"]["value"]
            #print (max_index)
            min_index = j["min_index"]["value"]
            #print (min_index)
            query_body = {"query": {"bool": {"must":{"term": {"timestamp":timestamp}}}},"size" : 20000}
            user_info = es.search(index = "user_influence",doc_type = "text",body = query_body)["hits"]["hits"]
            for user in user_info:
                id_es = user["_id"]
                new_index_value = (target_max-target_min)*(user["_source"][i] - min_index) /(max_index -min_index)+target_min
                print(id_es,i,max_index,min_index,new_index_value)
                es.update(index = "user_influence",doc_type = "text",id = id_es,body ={"doc":{i+"_normalization" :new_index_value}} )
                 


        


                
            
        
         
if __name__ == '__main__':
    uid_list = get_uidlist()
    #new_mapping(uid_list)
    normalize_influence_index()
    
    
