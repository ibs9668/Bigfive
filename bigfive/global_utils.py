from config import *
from time_utils import *

#用户遍历迭代器，输入索引（限于USER_RANKING与USER_INFORMATION），查询条件，每次迭代的次数，则可以迭代输出查询结果
def get_user_generator(user_index, query_body, iter_num_per):
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
def get_weibo_generator(weibo_index, query_body, iter_num_per):
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

'''
 es迭代器类 
 创建实例所需属性 step：迭代起始点，sort_dict：控制es数据查询排序字段及排序顺序，
 iter_count：迭代步长（控制每次查询数据量）,index_name :查询索引名字
 query_body:es查询语句 ，doc_type ：查询类型 ，es：建立的es连接
 
'''
class ESIterator(object):
    def __init__(self,step,sort_dict,iter_count,index_name,doc_type,query_body,es):
        self.step=step
        self.sort_dict = sort_dict
        self.iter_count =iter_count
        self.index_name = index_name
        self.doc_type = doc_type
        self.query_body = query_body
        self.es = es
    def __next__(self):
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

    
    #迭代器实例
    sort_dict = {}
    sort_dict = {'uid':{'order':'asc'}}
    query_body = {
        'query':{
             'match_all':{}
         }
     }
    my_test = ESIterator(0,sort_dict,1000,"user_information","text",query_body,es)

    while True:
        try:
            #获得下一批次查询的数据:
            x = next(my_test)
            print (len(x))
        except StopIteration:
            #遇到StopIteration就退出循环
            break

