import sys
import json
sys.path.append('../')
sys.path.append('../../')

from elasticsearch.helpers import bulk

from word_cloud import word_cloud
from retreet_comment import weibo_retweet_comment
from event_geo_message import get_event_static, get_event_geo
from event_cal_network import get_event_userlist_important
from event_cal_emotion import get_event_sentiment
from event_personality import get_event_personality

from get_keywords import text_rank_keywords
from event_river.river_main import river_main

from config import *
from time_utils import *
from global_utils import *

#事件的创建，扫描未计算的任务，获得任务的基本参数开始计算，主要为了圈定符合条件的用户群体，利用关键词检索
#输入：从event_information表中获得所需参数列表
#输出：发布满足条件微博的用户的列表
def event_create(event_mapping_name, keywords, start_date, end_date):
    uid_list_keyword = []
    keyword_list = keywords.split('&')
    keyword_query_list = [{"wildcard":{"text":"*%s*" % keyword}} for keyword in keyword_list]
    weibo_query_body = {
        "query":{
            'bool':{
            	'should':keyword_query_list,
                'minimum_should_match':2
            }
        }
    }

    date_list = get_datelist_v2(start_date, end_date)
    ###迭代日期进行模糊搜索并将微博存到一个新的事件索引中去
    for date in date_list:
        print(date)
        weibo_index = 'flow_text_%s' % date
        weibo_generator = get_weibo_generator(weibo_index, weibo_query_body, USER_WEIBO_ITER_COUNT)
        package = []
        midlist = []
        uid_list = []
        weibo_num = 0
        for res in weibo_generator:
            for hit in res:
                source = hit['_source']
                ###计算需要在取出事件相关微博数据的时候计算的指标
                keywords_string = '&'.join(text_rank_keywords(source['text']))
                sentiment = source['sentiment']
                geo = source['geo']

                dic = {
                    'root_uid':source['root_uid'],
                    'sentiment':sentiment,
                    'ip':source['ip'],
                    'user_fansnum':source['user_fansnum'],
                    'mid':source['mid'],
                    'message_type':source['message_type'],
                    'geo':geo,
                    'uid':source['uid'],
                    'root_mid':source['root_mid'],
                    'keywords_string':keywords_string,
                    'text':source['text'],
                    'timestamp':source['timestamp'],
                }
                package.append({
                    '_index': event_mapping_name,  
                    '_type': "text",  
                    '_id':dic['mid'],
                    '_source': dic
                })
                midlist.append(source['mid'])
                uid_list.append(source['uid'])

                if weibo_num % 1000 == 0:
                    #获取用户昵称
                    username_results = es.mget(index='weibo_user', doc_type='type1', body={'ids':uid_list})['docs']
                    username_dic = {}
                    for item in username_results:
                        if item['found']:
                            username_dic[item['_id']] = item['_source']['name']
                        else:
                            username_dic[item['_id']] = item['_id']
                    #会根据这段时间内的微博计算一跳转发和评论数
                    retweet_dic = weibo_retweet_comment(midlist, start_date, end_date)
                    #增添新数据
                    for p in package:
                        p['_source'].update({'username':username_dic[p['_source']['uid']]})
                        try:
                            p['_source'].update(retweet_dic[p['_source']['mid']])
                        except KeyError:
                            p['_source'].update({'comment':0,'retweeted':0})
                    bulk(es, package)  #存入数据库
                    package = []
                    midlist = []
                    uid_list = []
                    
                weibo_num += 1
                uid_list_keyword.append(source['uid'])

        #存入剩下的数据
        username_results = es.mget(index='weibo_user', doc_type='type1', body={'ids':uid_list})['docs']
        username_dic = {}
        for item in username_results:
            if item['found']:
                username_dic[item['_id']] = item['_source']['name']
            else:
                username_dic[item['_id']] = item['_id']
        retweet_dic = weibo_retweet_comment(midlist, start_date, end_date)
        for p in package:
            p['_source'].update({'username':username_dic[p['_source']['uid']]})
            try:
                p['_source'].update(retweet_dic[p['_source']['mid']])
            except KeyError:
                p['_source'].update({'comment':0,'retweeted':0})
        bulk(es, package)

    uid_list_keyword = list(set(uid_list_keyword))
    iter_num = 0
    uid_list = []
    while (iter_num*USER_WEIBO_ITER_COUNT <= len(uid_list_keyword)):
        iter_uid_list_keyword = uid_list_keyword[iter_num*USER_WEIBO_ITER_COUNT : (iter_num + 1)*USER_WEIBO_ITER_COUNT]
        iter_user_dict_list = es.mget(index='weibo_user', doc_type='type1', body={'ids':iter_uid_list_keyword})['docs']
        uid_list.extend([i['_id'] for i in iter_user_dict_list if i['found']])
        iter_num += 1

    print('Uid_list_keyword num:%d' % len(uid_list))
    return uid_list


#计算对应事件的词云及事件河
#输入：事件的名称及其微博索引，以从事件微博索引中获取微博进行计算
#输出：将计算好的词云及事件河存到数据库中
def get_text_analyze(event_id, event_mapping_name):
    query_body = {
        'query':{
            'match_all':{}
        }
    }
    weibo_generator = get_event_weibo_generator(event_mapping_name, query_body, USER_WEIBO_ITER_COUNT)  #得到所有微博的迭代器

    keywords_dic = {}

    for res in weibo_generator:
        keywords_list = [hit['_source']['keywords_string'] for hit in res]
        dic = word_cloud(keywords_list)   #词云
        for keyword in dic:
            try:
                keywords_dic[keyword] += dic[keyword]
            except:
                keywords_dic[keyword] = dic[keyword]

    keywords_list = [{"keyword":k,"count":keywords_dic[k]} for k in keywords_dic]
    cloud_dic = {
        'event_id':event_id,
        'keywords':keywords_list
    }
    es.index(index=EVENT_WORDCLOUD,doc_type='text',body=cloud_dic,id=event_id)

    cluster_count,cluster_word = river_main(event_mapping_name)   #事件河
    cluster_dic = {
        'event_id':event_id,
        'cluster_count':json.dumps(cluster_count),
        'cluster_word':json.dumps(cluster_word)
    }
    es.index(index=EVENT_RIVER,doc_type='text',body=cluster_dic,id=event_id)

#调用时间、地域、网络、情绪、人格等五个简单维度的函数进行计算并存到数据库
def event_portrait(event_id, event_mapping_name, user_list, start_date, end_date):
    print('Start event static...')  #时间、地域
    get_event_static(event_id, event_mapping_name, start_date, end_date)

    print('Start geo update...')  #事件地点更新
    get_event_geo(event_id)

    print('Start event userlist important...')  #网络
    get_event_userlist_important(event_id, user_list)

    print('Start event sentiment...')  #情绪
    get_event_sentiment(event_id, event_mapping_name, start_date, end_date)

    print('Start event personality...')  #人格
    get_event_personality(event_id, event_mapping_name, user_list, start_date, end_date)

if __name__ == "__main__":
	event_create()