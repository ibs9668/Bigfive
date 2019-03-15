import sys
sys.path.append('../../../')
from config import *
from time_utils import *
from global_utils import *

from user_ip import get_user_activity
from user_topic import get_user_topic
from user_domain import get_user_domain
from user_political import get_user_political
from user_text_analyze import get_word_analysis

#weibo_data_dict{"day1":[微博数据列表],"day2":[微博数据列表]}
def get_weibo_data_dict(uid, start_date,end_date):
    weibo_data_dict = {}
    #对每一天进行微博数据获取
    for day in get_datelist_v2(start_date, end_date):
        print(day)
        weibo_data_dict[day] = []
        index_name = "flow_text_" + str(day)
        query_body ={"query": {"bool": {"must":[{"term": {"uid": uid}}]}}}
        sort_dict = {'_id':{'order':'asc'}}
        ESIterator1 = ESIterator(0,sort_dict,1000,index_name,"text",query_body,es_weibo)
        while True:
            try:
                #一千条es数据
                es_result = next(ESIterator1)
                if len(weibo_data_dict[day]):
                    weibo_data_dict[day].extend(es_result)
                else:
                    weibo_data_dict[day] = es_result
                   
            except StopIteration:
                #遇到StopIteration就退出循环
                break
    return weibo_data_dict

def user_portrait(uid, start_date,end_date):
    
    weibo_data_dict = get_weibo_data_dict(uid, start_date,end_date)
    
    print('Calculating user position...')
    get_user_activity(uid,start_date,end_date)

    print('Calculating user topic...')
    get_user_topic(uid,start_date,end_date)

    print('Calculating user domain...')
    get_user_domain(uid,start_date,end_date)


    print('Calculating user political...')
    get_user_political(uid, start_date,end_date)

    print('Calculating word analysis...')
    get_word_analysis(uid,start_date,end_date)

    print('Calculating word analysis...')
    #cal_user_emotion(uid,weibo_data_dict)

    print('Calculating word analysis...')


    print('Calculating word analysis...')
    
if __name__ == '__main__':
    user_portrait(2061250093,"2016-11-13","2016-11-27")
