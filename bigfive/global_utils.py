from config import *
from time_utils import *

#用户遍历迭代器，输入索引（限于USER_RANKING与USER_INFORMATION），查询条件，每次迭代的次数，则可以迭代输出查询结果
def user_generator(user_index, query_body, iter_num_per):
    iter_num = 0
    iter_get_user = iter_num_per
    while (iter_get_user == iter_num_per):
        print("user_iter_num: %d" % (iter_num*iter_num_per))
        query_body['sort'] = {'uid':{'order':'asc'}}
        query_body['size'] = iter_num_per
        query_body['from'] = iter_num * iter_num_per
        es_result = es.search(index=user_index,doc_type='text',body=query_body)['hits']['hits']
        iter_get_user = len(es_result)
        if iter_get_user == 0:
            break
        iter_num += 1
        yield es_result

#微博遍历迭代器，输入索引（限于flow_text_yyyy-mm-dd系列），查询条件，每次迭代的次数，则可以迭代输出查询结果
def weibo_generator(weibo_index, query_body, iter_num_per):
    iter_num = 0
    iter_get_weibo = iter_num_per
    while (iter_get_weibo == iter_num_per):
        print("weibo_iter_num: %d" % (iter_num*iter_num_per))
        query_body['sort'] = {'_id':{'order':'asc'}}
        query_body['size'] = iter_num_per
        query_body['from'] = iter_num * iter_num_per
        es_result = es_weibo.search(index=weibo_index,doc_type='text',body=query_body)['hits']['hits']
        iter_get_weibo = len(es_result)
        if iter_get_weibo == 0:
            break
        iter_num += 1
        yield es_result

if __name__ == '__main__':
    # query_body = {
    #     'query':{
    #         'match_all':{}
    #     }
    # }
    # user_index = USER_RANKING
    # iter_num_per = 1000
    # user_generator = user_generator(user_index, query_body, iter_num_per)
    # for i in user_generator:
    #     print(len(i))
    
    query_body = {
        "_source":["uid"],
        "query":{
            'match_phrase':{
                'keywords_string':"语言"
            }
        }
    }
    weibo_index = 'flow_text_2016-11-13'
    iter_num_per = 1000
    weibo_generator = weibo_generator(weibo_index, query_body, iter_num_per)
    for i in weibo_generator:
        print(i[0])