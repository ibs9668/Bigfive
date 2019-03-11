import sys
import json
sys.path.append('../../')

from config import *
from time_utils import *
from global_utils import *

#批量计算一段时间内的一条微博的一跳转发量和评论量
def weibo_retweet_comment(midlist, start_date, end_date):
    index_list = []
    for day in get_datelist_v2(start_date, end_date):
        index_list.append('flow_text_%s' % day)
    count_dic = {}

    query_body = {
        '_source':['root_mid','message_type'],
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'terms':{'root_mid':midlist}},
                            {'terms':{'message_type':[2,3]}}
                        ]
                    }
                }
            }
        }
    }
    weibo_generator = get_weibo_generator(index_list, query_body, USER_WEIBO_ITER_COUNT)
    for res in weibo_generator:
        for hit in res:
            root_mid = hit['_source']['root_mid']
            message_type = hit['_source']['message_type']
            if root_mid in count_dic:
                if message_type == 2:
                    count_dic[root_mid]['comment'] += 1
                elif message_type == 3:
                    count_dic[root_mid]['retweeted'] += 1
            else:
                if message_type == 2:
                    count_dic[root_mid] = {'comment':1,'retweeted':0}
                elif message_type == 3:
                    count_dic[root_mid] = {'comment':0,'retweeted':1}

    return count_dic

#批量计算一段时间内的一个用户的一跳转发量和评论量
def user_retweet_comment(uidlist, start_date, end_date):
    index_list = []
    for day in get_datelist_v2(start_date, end_date):
        index_list.append('flow_text_%s' % day)
    count_dic = {}

    query_body = {
        '_source':['root_uid','message_type'],
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'terms':{'root_uid':uidlist}},
                            {'terms':{'message_type':[2,3]}}
                        ]
                    }
                }
            }
        }
    }
    weibo_generator = get_weibo_generator(index_list, query_body, USER_WEIBO_ITER_COUNT)
    for res in weibo_generator:
        for hit in res:
            root_uid = hit['_source']['root_uid']
            message_type = hit['_source']['message_type']
            if root_uid in count_dic:
                if message_type == 2:
                    count_dic[root_uid]['comment'] += 1
                elif message_type == 3:
                    count_dic[root_uid]['retweeted'] += 1
            else:
                if message_type == 2:
                    count_dic[root_uid] = {'comment':1,'retweeted':0}
                elif message_type == 3:
                    count_dic[root_uid] = {'comment':0,'retweeted':1}

    return count_dic

if __name__ == '__main__':
    query_body = {
        'query':{
            'match_all':{}
        }
    }
    # midlist = [hit['_source']['mid'] for hit in es.search(index='event_ceshishijiansan_1551942139',doc_type='text',body=query_body)['hits']['hits']]
    # uidlist = [hit['_source']['uid'] for hit in es.search(index='user_information',doc_type='text',body=query_body)['hits']['hits']]
    # print(len(midlist))
    # print(len(uidlist))
    start_date = '2016-11-13'
    end_date = '2016-11-27'
    # weibo_retweet_comment(midlist, start_date, end_date)
    # user_retweet_comment(uidlist, start_date, end_date)

    weibo_generator = get_event_weibo_generator('event_ceshishijiansan_1551942139', query_body, USER_WEIBO_ITER_COUNT)
    for res in weibo_generator:
    	midlist = [hit['_source']['mid'] for hit in res]
    	retweet_dic = weibo_retweet_comment(midlist, start_date, end_date)
    	print(len(retweet_dic))
    	for mid in midlist:
    		try:
    			dic = retweet_dic[mid]
    		except:
    			dic = {'comment':0,'retweeted':0}
    		es.update(index='event_ceshishijiansan_1551942139',doc_type='text',id=mid,body={'doc':dic})