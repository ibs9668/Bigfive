# -*- coding: UTF-8 -*-

import sys
sys.path.append('../../')
from config import *
from time_utils import *
from global_utils import * 
import networkx as nx
import matplotlib.pyplot as plt


def buildDiGraph(edges):
    """
    初始化图
    :param edges: 存储有向边的列表
    :return: 使用有向边构造完毕的有向图
    """
    print (111)
    G = nx.DiGraph()   # DiGraph()表示有向图
    for edge in edges:
        G.add_edge(edge[0], edge[1])   # 加入边
    return G


#计算群体热度事件的转发关系
def event_cal_network_everyday(event_id,keywords_string,date):
    keyword_query_list = []
    for keyword in keywords_string.split("&"):
        keyword_query_list.append({'wildcard':{'text':'*'+keyword+'*'}})
    
    print (keyword_query_list)
    sort_dict = {}
    sort_dict = {'_id':{'order':'asc'}}    
    query_body = {
        "_source":["uid","root_uid","timestamp","message_type"],
        'query':{
            'bool':{
                'should':keyword_query_list,
                'minimum_should_match':2,
                'must':{
                    "term":{
                        "message_type":3
                        }
                    }

                }
            }
    }
    print (query_body)
    weibo_index = 'flow_text_' + date
    print (weibo_index)
    es_search  = ESIterator(0,sort_dict,1000,weibo_index,"text",query_body,es_weibo)

    #转发关系再问一下
    edges = []
    uid_list = []
    while True:
        try:
            #一千条es数据
            es_result = next(es_search)
            for item in es_result:
                '''
                #收集edgs
                item_list = []
                item_list.append(item["_source"]["root_uid"])
                item_list.append(item["_source"]["uid"])
                edges.append(tuple(item_list))
                '''
                #建表
                source = item["_source"]["root_uid"]
                try:
                    #source_inf = es.get(index="weibo_user", doc_type="type1",id = source)
                    #if source_inf["found"] == True:
                    source_name = source
                    message_type = item["_source"]["message_type"]
                    timestamp = item["_source"]["timestamp"]
                    target = item["_source"]["uid"]
                    #target_inf = es.get(index="user_information", doc_type="text",id = _)
                    #if target_inf["found"] == True:
                    #target_name = target_inf["_source"]["username"].encode("utf-8")
                    #else:
                    target_name = target
                    #print (time_change(timestamp),target,target_name,source,source_name,message_type)
                    #print ("---")
                    id_es = str(target)+"_"+ str(source) +"_"+str(date2ts(ts2date(timestamp)))+"_"+str(message_type) + "_" + str(event_id)
                    #print (id_es)
                    es.index(index = "event_social_contact",doc_type = "text",id = id_es, body = {"timestamp":date2ts(ts2date(timestamp)),"source": source, "target": target, "source_name": source_name, "target_name":target_name,"message_type":message_type,"date":date,"event_id":event_id})
                except:
                    print ("no")
        except StopIteration:
            #遇到StopIteration就退出循环
            break
    '''
    print(len(edges))
    print (len(uid_list))
    graph = buildDiGraph(edges)
    pr_value = nx.pagerank(graph, alpha=0.85,max_iter= 10000)
    print("naive pagerank值是：", pr_value)
    print (len(pr_value.keys()))
    list1= sorted(pr_value.items(),key=lambda x:x[1],reverse=True)
    print (list1)# 排好序的全部用户 

    user_rank_list = []
    for i in list1:
        if i[0] in uid_list:
            user_rank_list.append(i)

    final_edges = []
    print (user_rank_list) #排好序的用户列表
    for j in list1[0:10]:#取前多少用户：（问对哪些用户进行操作）
        for edge in edges :
            if j[0] in edge:
                if edge not in final_edges:
                    final_edges.append(edge)
                else:
                    pass

    print (final_edges)
    print (len(final_edges))
    '''
#根据event_id找到群体热度事件的相关社交网络数据 进行networkx的pagerank
def event_cal_network_pagerank(event_id,start_time,end_time):
    sort_dict = {}
    sort_dict = {'_id':{'order':'asc'}}
    
    query_body = {
        "_source":["source","target"],
        "query": {
            "bool": {
                "must": [
                {
                    "range": {
                        "timestamp": {
                            "gte": start_time,
                            "lte": end_time
                        }
                    }
                },
                {
                    "term": {
                        "event_id": event_id
                    }
                }
                ]
            }
       }}

    index = "event_social_contact"
    es_search  = ESIterator(0,sort_dict,1000,index,"text",query_body,es)

    edges = []
    uid_list = []
    while True:
        try:
            #一千条es数据
            es_result = next(es_search)
            for item in es_result:
                #收集edgs
                item_list = []
                item_list.append(item["_source"]["source"])
                item_list.append(item["_source"]["target"])
                edges.append(tuple(item_list))
        except StopIteration:
            #遇到StopIteration就退出循环
            break        
    print(len(edges))
    #print (len(uid_list))
    graph = buildDiGraph(edges)
    pr_value = nx.pagerank(graph, alpha=0.85,max_iter= 100000)
    print("naive pagerank值是：", pr_value)
    print (len(pr_value.keys()))
    uid_rank_list= sorted(pr_value.items(),key=lambda x:x[1],reverse=True)[0:10]#取前100个用户
    print (uid_rank_list)# 排好序的全部用户 
    
    uid_list = []
    for i in uid_rank_list:
        uid_list.append(i[0])
    
    
    print(uid_list)
    id_es = str(event_id) +"_" + str(start_time) +"_" +str(end_time)
    es.index(index = "event_social_contact_pagerank",doc_type = "text",id = id_es,body = {"uidlist":"&".join(uid_list),"strat_timestamp":start_time,"end_timestamp":end_time,"start_date":ts2date(int(start_time)),"end_date":ts2date(int(end_time))})



             

#get_datelist_v2(start_date, end_date) 输出时间列表的函数
#事件长期 event_id keywords_string date days
def event_cal_network_long(event_id,keywords_string,date,days):
    for day in get_datelist_v2(ts2date(date2ts(date)-24*3600*days),date):
        try:
            event_cal_network_everyday(event_id,keywords_string,day)
        except:
        	pass

if __name__ == '__main__':
    #event_cal_network_long(111,"滴滴&打车","2016-11-13",0)
    event_cal_network_pagerank('111','1478966400','1478966400')
