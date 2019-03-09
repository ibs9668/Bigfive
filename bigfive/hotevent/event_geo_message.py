#-*-coding=utf-8-*-
# -*- coding: UTF-8 -*-

import sys
sys.path.append('../')
from config import *
from time_utils import *
from global_utils import * 

class ESIterator(object):
    def __init__(self,step,sort_dict,iter_count,index_name,doc_type,query_body,es):
        self.step=step
        self.sort_dict = sort_dict
        self.iter_count =iter_count
        self.index_name = index_name
        self.doc_type = doc_type
        self.query_body = query_body
        self.es = es
    def __next__(self):#python3
        self.query_body["sort"] = self.sort_dict
        self.query_body["size"] = self.iter_count
        self.query_body["from"] = self.step * self.iter_count
        es_result = self.es.search(index=self.index_name,doc_type=self.doc_type,body=self.query_body)['hits']['hits']
        iter_get_num = len(es_result)
        if iter_get_num == 0:
            raise StopIteration
        self.step +=1
        return es_result
    
    def __iter__(self):
        return self



def get_group_static(start_date,end_date,event_id):
    start_ts = date2ts(start_date)
    end_ts = date2ts(end_date)+DAY

    date_list = [ts2date(start_ts+DAY*i) for i in range(int((end_ts-start_ts)/DAY))]

    for date in date_list:
        geo_dict = {}
        message_type_dict = {}

        sort_dict = {'_id':{'order':'asc'}}    
        query_body = {
            'query':{
                'bool':{
                    "must": [
								{
								"range": {
								"timestamp": {
								"gte":int(date2ts(date)),
								"lt": int(date2ts(date)+DAY)
								}
							}
						}
					]
                }
            },"size":15000
        }

        count = 0
        ESIterator1 = ESIterator(0,sort_dict,1000,event_id,"text",query_body,es)

        ###地理位置和微博类型统计
        while True:
            try:
                #一千条es数据
                es_result = next(ESIterator1)

                for item in es_result:
                    if not item["_source"]["geo"].startswith('中国') or  len(item["_source"]["geo"].split("&"))<=2:
                        pass
                    elif item["_source"]["geo"] not in geo_dict:
                        geo_dict[item["_source"]["geo"]] = 1
                    else:
                        geo_dict[item["_source"]["geo"]] += 1

                    if item["_source"]["message_type"] not in message_type_dict:
                        message_type_dict[item["_source"]["message_type"]] = 1
                    else:
                        message_type_dict[item["_source"]["message_type"]] += 1

            except StopIteration:
                #遇到StopIteration就退出循环
                break
        timestamp = date2ts(date)
        try:
            for geo in geo_dict:
                es.index(index= "event_geo",doc_type= "text",body= {
                    "event_id":event_id,
                    "geo":geo,
                    "geo_count":geo_dict[geo],
                    "timestamp":timestamp,
                    "date":date
                    })
        except:
            pass

        try:
            for message in message_type_dict:
                es.index(index= "event_message_type",doc_type= "text",body= {
                    "event_id":event_id,
                    "message_type":message,
                    "message_count":message_type_dict[message],
                    "timestamp":timestamp,
                    "date":date
                    })
        except:
            pass



if __name__ == '__main__':

    get_group_static("2016-11-13","2016-11-27","event_ceshishijiansan_1551942139")
    