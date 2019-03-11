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


def get_event():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="event_information", doc_type="text",body=query_body)["hits"]["hits"]
    for es_item in es_result:
        #try:
        print es_item["_source"]
        get_event_userlist_important(es_item["_source"]["userlist"],es_item["_id"],1)
            #get_event_userlist_important(es_item["_source"]["userlist"],es_item["_id"],2)
        #except:
            #print("no index")


def get_event_userlist_important(userlist,event_id,map_type):
    #user_list = es.get(index='group_information', doc_type='text', id=group_id)[
        #'_source']['userlist']
    if map_type in ['1', '2']:
        message_type = 3
    else:
        message_type = 2
    if map_type in ['1', '3']:
        key = 'target'
    else:
        key = 'source'
    query_body = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "message_type": message_type
                                }
                            },
                            {
                                "terms": {
                                    key: userlist
                                }
                            }
                        ]}
                }}
        },
        "size": 3000,
    }
    r = es.search(index="user_social_contact", doc_type="text",
                  body=query_body)["hits"]["hits"]
    node = []
    link = []
    for one in r:
        item = one['_source']
        a = {'id': item['target'], 'name': item['target_name']}
        b = {'id': item['source'], 'name': item['source_name']}
        c = {'source': item['source'], 'target': item['target']}
        if a not in node:
            node.append(a)
        if b not in node:
            node.append(b)
        if c not in link and c['source'] != c['target']:
            link.append(c)
    social_contact = {'node': node, 'link': link}
    if node:
        print (social_contact)
        edges = []
        for item in social_contact["link"]:
            #收集edgs
            item_list = []
            item_list.append(item["source"])
            item_list.append(item["target"])
            edges.append(tuple(item_list))       
        print(len(edges))
        #print (len(uid_list))
        graph = buildDiGraph(edges)
        pr_value = nx.pagerank(graph, alpha=0.85,max_iter= 100000)
        print("naive pagerank值是：", pr_value)
        print (len(pr_value.keys()))
        if len(pr_value)>= 100:
            uid_rank_list= sorted(pr_value.items(),key=lambda x:x[1],reverse=True)[0:100]#取前100个用户
        else :
            uid_rank_list= sorted(pr_value.items(),key=lambda x:x[1],reverse=True)
        print (uid_rank_list)# 排好序的全部用户 
    
        uid_list = []
        for i in uid_rank_list:
            uid_list.append(i[0])
    
    
        print(uid_list)
        print(event_id)
        es.update(index = "event_information",doc_type = "text",id = event_id,body = {"doc":{"userlist_important":uid_list}})


if __name__ == '__main__':
    get_event()
