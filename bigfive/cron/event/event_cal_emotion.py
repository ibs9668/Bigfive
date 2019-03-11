# -*- coding: UTF-8 -*-

import sys
sys.path.append('../../')
from config import *
from time_utils import *
from global_utils import * 

# 0中性 1积极 2生气 3焦虑 4悲伤 5厌恶 6消极其他 
#
def event_cal_sentiment_geo_everyday(event_id,keywords_string,date):
    keyword_query_list = []
    for keyword in keywords_string.split("&"):
        keyword_query_list.append({'wildcard':{'text':'*'+keyword+'*'}})
    
    print (keyword_query_list)
    sort_dict = {}
    sort_dict = {'_id':{'order':'asc'}}    
    query_body = {
        "_source":["sentiment","geo"],
        'query':{
            'bool':{
                'should':keyword_query_list,
                'minimum_should_match':2
                }
            }
    }
    weibo_index = 'flow_text_' + date
    print (weibo_index)
    es_search  = ESIterator(0,sort_dict,1000,weibo_index,"text",query_body,es_weibo)
    

    sentiment_dict = {}
    sentiment_geo_dict = {}
    while True:
        try:
            #一千条es数据
            es_result = next(es_search)
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
    body_dict = dict(sentiment_dict,**base_dict)
    print(body_dict)
    #es.index(index ="event_emotion",doc_type= "text",id = str(event_id)+"_"+ str(date2ts(date)),body = body_dict)
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

#get_datelist_v2(start_date, end_date) 输出时间列表的函数
#事件长期 event_id keywords_string date days
def event_cal_sentiment_long(event_id,keywords_string,date,days):
    for day in get_datelist_v2(ts2date(date2ts(date)-24*3600*days),date):
        try:
            event_cal_sentiment_geo_everyday(event_id,keywords_string,day)
        except:
            pass


if __name__ == '__main__':
 	event_cal_sentiment_long(111,"滴滴&打车","2016-11-13",0)
