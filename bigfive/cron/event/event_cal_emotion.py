# -*- coding: UTF-8 -*-

import sys
sys.path.append('../../')
from config import *
from time_utils import *
from global_utils import * 

# 0中性 1积极 2生气 3焦虑 4悲伤 5厌恶 6消极其他 
#
def get_event():
    query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
    es_result = es.search(index="event_information", doc_type="text",body=query_body)["hits"]["hits"]
    for es_item in es_result:
        try:
            get_event_sentiment(es_item["_source"]["start_date"],es_item["_source"]["end_date"],es_item["_id"])
        except:
            print("no index")



def get_event_sentiment(start_date,end_date,event_id):
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
            }
        }

        
        ESIterator1 = ESIterator(0,sort_dict,1000,"event_"+ str(event_id),"text",query_body,es)


        sentiment_dict = {}
        sentiment_geo_dict = {}
        ##
        while True:
            try:
                #一千条es数据
                es_result = next(ESIterator1)

                print (es_result)
                for item in es_result:
                    if item["_source"]["sentiment"] not in sentiment_dict:
                        sentiment_dict[item["_source"]["sentiment"]] = 1
                    else:
                        sentiment_dict[item["_source"]["sentiment"]] += 1

                    if item["_source"]["sentiment"] not in sentiment_geo_dict:
                        sentiment_geo_dict[item["_source"]["sentiment"]] = {}
                    if not item["_source"]["geo"].startswith('中国'):
                        pass
                    elif item["_source"]["geo"] not in sentiment_geo_dict[item["_source"]["sentiment"]]:
                        sentiment_geo_dict[item["_source"]["sentiment"]][item["_source"]["geo"]] = 1
                    else:
                        sentiment_geo_dict[item["_source"]["sentiment"]][item["_source"]["geo"]] += 1

            except StopIteration:
                #遇到StopIteration就退出循环
                break
        

        print (sentiment_dict)#一天的数据的统计信息
        print (sentiment_geo_dict)
        for i in range(0,7):
            if str(i) not in sentiment_dict:
                sentiment_dict[str(i)] = 0
            if str(i) not in sentiment_geo_dict:
                sentiment_geo_dict[str(i)] = {}
        base_dict = {"timestamp":date2ts(date),"date":date,"event_id":event_id}
        print(sentiment_dict)
        new_sentiment_dict = {}
        new_sentiment_dict["nuetral"] = sentiment_dict["0"]
        new_sentiment_dict["positive"] = sentiment_dict["1"]
        new_sentiment_dict["angry"] = sentiment_dict["2"]
        new_sentiment_dict["anxiety"] = sentiment_dict["3"]
        new_sentiment_dict["sad"] = sentiment_dict["4"]
        new_sentiment_dict["hate"] = sentiment_dict["5"]
        new_sentiment_dict["negtive"] = sentiment_dict["6"]
        print(new_sentiment_dict)
        body_dict = dict(new_sentiment_dict,**base_dict)
        print(body_dict)
        es.index(index ="event_emotion",doc_type= "text",id = str(event_id)+"_"+ str(date2ts(date)),body = body_dict)
        for sentiment in sentiment_geo_dict.keys():
            s_dict={}
            s_list= []
            for item_g in sentiment_geo_dict[sentiment].keys():
                i_dict = {}
                i_dict["geo"] = item_g
                i_dict["count"] = sentiment_geo_dict[sentiment][item_g]
                s_list.append(i_dict)
            s_dict["geo_dict"] = s_list
            s_dict["emotion"] = sentiment
            body_dict = dict(s_dict,**base_dict)
            print (body_dict)
            es.index(index = "event_emotion_geo",doc_type= "text",id =str(event_id)+"_"+ str(date2ts(date))+"_"+str(sentiment),body = body_dict )



if __name__ == '__main__':
 	get_event()
