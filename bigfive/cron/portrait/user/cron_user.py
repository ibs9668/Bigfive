import sys
sys.path.append('../../../')
from config import *
from time_utils import *
import random
from keyword_topic import text_rank, micro_words, cal_sensitive

from elasticsearch import Elasticsearch,helpers
from elasticsearch.helpers import bulk

def user_attribute(uid):
    liveness_index = int(random.random() * 100)
    importance_index = int(random.random() * 100)
    sensitive_index = int(random.random() * 100)
    influence_index = int(random.random() * 100)
    liveness_star = int(liveness_index / 20) + 1
    importance_star = int(importance_index / 20) + 1
    sensitive_star = int(sensitive_index / 20) + 1
    influence_star = int(influence_index / 20 + 1)
    return liveness_index,importance_index,sensitive_index,influence_index,liveness_star,importance_star,sensitive_star,influence_star

#计算对于库中的用户每天所发布微博的关键词、微话题和敏感词列表，便于统计
#不保证一个用户一天一条，如果未发布微博则没有记录
def word_analysis_daily(date):
    keywords_dict = {}
    hastag_dict = {}
    sensitive_dict = {}
    weibo_index = 'flow_text_' + date
    timestamp = date2ts(date)

    #遍历库中所有的用户
    iter_num = 0
    iter_get_user = USER_ITER_COUNT
    while (iter_get_user == USER_ITER_COUNT):
        print(iter_num*100,date)
        user_query_body = {
            'query':{
                'match_all':{}
            },
            'sort':{
                'uid':{
                    'order':'asc'
                }
            },
            "size":USER_ITER_COUNT,
            "from":iter_num * USER_ITER_COUNT
        }
        es_result = es.search(index=USER_INFORMATION,doc_type='text',body=user_query_body)['hits']['hits']
        iter_get_user = len(es_result)
        iter_num += 1
        iter_user_list = [hit['_source']['uid'] for hit in es_result]

        #每次迭代计算指定的用户数量
        #遍历这些用户当天所发布的微博
        weibo_iter_num = 0
        iter_get_weibo = USER_WEIBO_ITER_COUNT
        es_result = []
        while (iter_get_weibo == USER_WEIBO_ITER_COUNT):
            weibo_query_body = {
                "query":{
                    'terms':{
                        'uid':iter_user_list
                    }
                },
                'sort':{
                    '_id':{
                        'order':'asc'
                    }
                },
                "size":USER_WEIBO_ITER_COUNT,
                "from":weibo_iter_num * USER_WEIBO_ITER_COUNT
            }
            res = es_weibo.search(index=weibo_index,doc_type='text',body=weibo_query_body)['hits']['hits']
            es_result.extend(res)
            iter_get_weibo = len(res)
            weibo_iter_num += 1
        print(len(es_result))

        for hit in es_result:
            uid = hit['_source']['uid']
            text = hit['_source']['text']
            keywords = text_rank(text,5)
            hastags = micro_words(text)
            score, sensitive_words = cal_sensitive(text)
            sensitive_words_dict = sensitive_words['sensitive_words_dict']
            #关键词
            if uid in keywords_dict:
                for keyword in keywords:
                    try:
                        keywords_dict[uid][keyword] += 1
                    except:
                        keywords_dict[uid][keyword] = 1
            else:
                keywords_dict[uid] = {keyword:1 for keyword in keywords}
            #微话题
            if uid in hastag_dict:
                for hastag in hastags:
                    try:
                        hastag_dict[uid][hastag] += 1
                    except:
                        hastag_dict[uid][hastag] = 1
            else:
                hastag_dict[uid] = {hastag:1 for hastag in hastags}
            #敏感词
            if uid in sensitive_dict:
                for sensitive_word in sensitive_words_dict:
                    try:
                        sensitive_dict[uid][sensitive_word] += sensitive_words_dict[sensitive_word]
                    except:
                        sensitive_dict[uid][sensitive_word] = sensitive_words_dict[sensitive_word]

            else:
                sensitive_dict[uid] = {sensitive_word:1 for sensitive_word in sensitive_words_dict}
        #遍历存入数据库
        for uid in keywords_dict:
            # print(keywords_dict[uid],hastag_dict[uid],sensitive_dict[uid])
            keywords = [{'keyword':k,'count':keywords_dict[uid][k]} for k in keywords_dict[uid]]
            hastags = [{'hastag':k,'count':hastag_dict[uid][k]} for k in hastag_dict[uid]]
            sensitive_words = [{'sensitive_word':k,'count':sensitive_dict[uid][k]} for k in sensitive_dict[uid]]

            dic = {
                'keywords':keywords,
                'hastags':hastags,
                'sensitive_words':sensitive_words,
                'uid':uid,
                'timestamp':timestamp,
                'date':date
            }

            es.index(index=USER_TEXT_ANALYSIS,doc_type='text',body=dic,id=uid+'_'+str(timestamp))

        iter_user_list = []
        keywords_dict = {}
        hastag_dict = {}
        sensitive_dict = {}

#对于单个uid进行每天的过去指定时间窗口的关键词、微话题和敏感词全量统计
#保证一个用户一天一条
def word_analysis(uid, date, days):
    date_end_ts = date2ts(date)
    date_start_ts = date_end_ts - 24*3600*days
    keywords_dict = {}
    hastag_dict = {}
    sensitive_dict = {}
    query_body = {
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term':{'uid':uid}},
                            {'range':{'timestamp':{'gt':date_start_ts,'lte':date_end_ts}}}
                        ]
                    }
                }
            }
        },
        'size':500
    }
    res = es.search(index=USER_TEXT_ANALYSIS,doc_type='text',body=query_body)['hits']['hits']
    for hit in res:
        keywords = hit['_source']['keywords']
        hastags = hit['_source']['hastags']
        sensitive_words = hit['_source']['sensitive_words']

        for item in keywords:
            keyword = item['keyword']
            count = item['count']
            try:
                keywords_dict[keyword] += count
            except:
                keywords_dict[keyword] = count

        for item in hastags:
            hastag = item['hastag']
            count = item['count']
            try:
                hastag_dict[hastag] += count
            except:
                hastag_dict[hastag] = count

        for item in sensitive_words:
            sensitive_word = item['sensitive_word']
            count = item['count']
            try:
                sensitive_dict[sensitive_word] += count
            except:
                sensitive_dict[sensitive_word] = count

    keywords = [{'keyword':k,'count':keywords_dict[k]} for k in keywords_dict]
    hastags = [{'hastag':k,'count':hastag_dict[k]} for k in hastag_dict]
    sensitive_words = [{'sensitive_word':k,'count':sensitive_dict[k]} for k in sensitive_dict]

    dic = {
        'keywords':keywords,
        'hastags':hastags,
        'sensitive_words':sensitive_words,
        'uid':uid,
        'timestamp':date_end_ts,
        'date':date
    }

    es.index(index=USER_TEXT_ANALYSIS_STA,doc_type='text',body=dic,id=uid+'_'+str(date_end_ts))

#遍历用户进行全量计算
def word_analysis_main(date):
    iter_num = 0
    iter_get_user = USER_ITER_COUNT
    while (iter_get_user == USER_ITER_COUNT):
        print(iter_num*USER_ITER_COUNT,date)
        user_query_body = {
            'query':{
                'match_all':{}
            },
            'sort':{
                'uid':{
                    'order':'asc'
                }
            },
            "size":USER_ITER_COUNT,
            "from":iter_num * USER_ITER_COUNT
        }
        es_result = es.search(index=USER_INFORMATION,doc_type='text',body=user_query_body)['hits']['hits']
        iter_get_user = len(es_result)
        iter_num += 1
        iter_user_list = [hit['_source']['uid'] for hit in es_result]

        for uid in iter_user_list:
            word_analysis(uid,date,30)

if __name__=='__main__':
    # user_attribute('1965808527')
    # word_analysis_daily('2016-11-13')
    for date in get_datelist(2016,11,23,2016,11,27):
        word_analysis_main(date)
    # word_analysis_main('2016-11-13')