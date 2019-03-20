# -*- coding: UTF-8 -*-

import sys
sys.path.append('../../')
from config import *
from time_utils import *
from global_utils import * 
import networkx as nx


def buildDiGraph(edges):
    """
    初始化图
    :param edges: 存储有向边的列表
    :return: 使用有向边构造完毕的有向图
    """
    G = nx.DiGraph()   # DiGraph()表示有向图
    for edge in edges:
        G.add_edge(edge[0], edge[1])   # 加入边
    return G


def get_event():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="event_information", doc_type="text",body=query_body)["hits"]["hits"]
    for es_item in es_result:
        #try:
        print(es_item["_source"])
        get_event_userlist_important(es_item["_source"]["userlist"],es_item["_id"],1)
            #get_event_userlist_important(es_item["_source"]["userlist"],es_item["_id"],2)
        #except:
            #print("no index")


def get_event_userlist_important(event_id, userlist, map_type='retweeted'):
    #user_list = es.get(index='group_information', doc_type='text', id=group_id)[
        #'_source']['userlist']
    if map_type == 'retweeted':
        message_type = 3
    elif map_type == 'comment':
        message_type = 2
    else:
        raise Exception
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
                                    'target': userlist
                                }
                            },
                            {
                                "terms": {
                                    'source': userlist
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
    print(len(link))
    social_contact = {'node': node, 'link': link}
    if node:
        # print (social_contact)
        edges = []
        for item in social_contact["link"]:
            #收集edgs
            item_list = []
            item_list.append(item["source"])
            item_list.append(item["target"])
            edges.append(tuple(item_list))       
        # print(len(edges))
        #print (len(uid_list))
        graph = buildDiGraph(edges)
        pr_value = nx.pagerank(graph, alpha=0.85,max_iter= 100000)
        # print("naive pagerank值是：", pr_value)
        # print (len(pr_value.keys()))
        if len(pr_value)>= 100:
            uid_rank_list= sorted(pr_value.items(),key=lambda x:x[1],reverse=True)[0:100]#取前100个用户
        else :
            uid_rank_list= sorted(pr_value.items(),key=lambda x:x[1],reverse=True)
        # print (uid_rank_list)# 排好序的全部用户 
    
        uid_list = []
        for i in uid_rank_list:
            uid_list.append(i[0])
    
    
        # print(uid_list)
        # print(event_id)
        es.update(index = "event_information",doc_type = "text",id = event_id,body = {"doc":{"userlist_important":uid_list}})
        return uid_list
    else:
        es.update(index = "event_information",doc_type = "text",id = event_id,body = {"doc":{"userlist_important":[]}})
        return []



if __name__ == '__main__':
    userlist = es.get(index='group_information',doc_type='text',id='ceshiliu_1480176000')['_source']['userlist']
    print(get_event_userlist_important(userlist)) #, 'comment'
