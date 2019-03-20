import time
import sys
import json
sys.path.append('../')
sys.path.append('portrait/user')
sys.path.append('portrait/group')
sys.path.append('event')
sys.path.append('politics')
sys.path.append('event/event_river')
from xpinyin import Pinyin
#注意：分词工具只需要初始化一次即可，多次初始化会出现线程问题！

from config import *
from time_utils import *
from global_utils import *
from portrait.cron_portrait import user_ranking, cal_user_personality, group_create, group_ranking, cal_group_personality
from portrait.user.cron_user import user_portrait
from portrait.group.cron_group import group_portrait
from cron_event import event_create, get_text_analyze, event_portrait
from event_mapping import create_event_mapping
from portrait.user.user_text_analyze import cal_user_text_analyze
from cron_politics import politics_create, politics_portrait
from politics_mapping import create_politics_mapping

#对用户进行批量计算，流数据接入时会自动入库批量计算
def user_main(uid_list,username_list, start_date, end_date):
    print('Start calculating user personality...')
    cal_user_personality(uid_list, start_date, end_date)

    print('Start calculating user text...')
    cal_user_text_analyze(uid_list, start_date, end_date)

    print('Start calculating user portrait...')
    for uid in uid_list:
        print(uid)
        user_portrait(uid, end_date)
    
    print('Start calculating user ranking...')
    user_ranking(uid_list, username_list, end_date)

    print('Successfully create user...')

#检测任务表，有新任务会进行计算，默认取计算时间段的结束日期为创建日期，开始日期为结束日期前的n天
def group_main(args_dict, keyword, remark, group_name, create_time):
    days = 15
    end_date = ts2date(create_time)
    start_date = ts2date(create_time - days * 24 *3600)
    print('Start finding userlist...')
    group_dic = group_create(args_dict, keyword, remark, group_name, create_time, start_date, end_date)

    print('Start calculating group personality...')
    cal_group_personality(group_dic['group_id'], group_dic['userlist'], end_date)

    print('Start calculating group portrait...')
    group_portrait(group_dic['group_id'], group_dic['userlist'], start_date, end_date)
    
    print('Start calculating group ranking...')
    group_ranking(group_dic['group_id'], group_dic['group_name'], group_dic['userlist'], end_date)

    print('Successfully create group...')


def event_main(keywords, event_id, start_date, end_date):
    print('Start creating event...')
    event_mapping_name = 'event_%s' % event_id
    # create_event_mapping(event_mapping_name)
    # userlist = event_create(event_mapping_name, keywords, start_date, end_date)
    # es.update(index=EVENT_INFORMATION,doc_type='text',body={'doc':{'userlist':userlist}},id=event_id)

    # print('Start text analyze...')
    # get_text_analyze(event_id, event_mapping_name)
    
    print('Start event portrait...')
    userlist = es.get(index='event_information',doc_type='text',id=event_id)['_source']['userlist']
    event_portrait(event_id, event_mapping_name, userlist, start_date, end_date)

    print('Successfully create event...')

def politics_main(keywords, politics_id, start_date, end_date):
    print('Start creating politics...')
    politics_mapping_name = 'politics_%s' % politics_id
    create_politics_mapping(politics_mapping_name)
    userlist = politics_create(politics_mapping_name, keywords, start_date, end_date)
    es.update(index=POLITICS_INFORMATION,doc_type='text',body={'doc':{'userlist':userlist}},id=politics_id)
    
    print('Start politics portrait...')
    # userlist = es.get(index='politics_information',doc_type='text',id=politics_id)['_source']['userlist']
    politics_portrait(politics_id, politics_mapping_name, userlist, start_date, end_date)

    print('Successfully create politics...')

if __name__ == '__main__':
    # user_main(['1663765234','3217540085'],'2016-11-13','2016-11-16')
    # group_main(1,2,3,4,5)

    # event_name = "测试事件二"
    # event_pinyin = Pinyin().get_pinyin(event_name, '')
    # create_time = int(time.time())
    # create_date = ts2date(create_time)
    # start_date = '2016-11-13'
    # end_date = '2016-11-27'
    # keywords = "台湾&独立"
    # progress = 0
    # event_id = event_pinyin + "_" + str(create_time)
    # dic = {
    #     'event_name':event_name,
    #     'event_pinyin':event_pinyin,
    #     'create_time':create_time,
    #     'create_date':create_date,
    #     'keywords':keywords,
    #     'progress':progress,
    #     'event_id':event_id,
    #     'start_date':start_date,
    #     'end_date':end_date
    # }
    # es.index(index=EVENT_INFORMATION,doc_type='text',body=dic,id=event_id)
    # time.sleep(1)
    # event_main(keywords, event_id, start_date, end_date)


    # politics_name = "测试政策一"
    # politics_pinyin = Pinyin().get_pinyin(politics_name, '')
    # create_time = int(time.time())
    # create_date = ts2date(create_time)
    # start_date = '2016-11-13'
    # end_date = '2016-11-27'
    # keywords = "股市"
    # progress = 0
    # politics_id = politics_pinyin + "_" + str(create_time)
    # dic = {
    #     'politics_name':politics_name,
    #     'politics_pinyin':politics_pinyin,
    #     'create_time':create_time,
    #     'create_date':create_date,
    #     'keywords':keywords,
    #     'progress':progress,
    #     'politics_id':politics_id,
    #     'start_date':start_date,
    #     'end_date':end_date
    # }
    # es.index(index=POLITICS_INFORMATION,doc_type='text',body=dic,id=politics_id)


    # dic = {
    #     "remark": "第九次群体测试",
    #     "keyword": "",
    #     "create_condition": { 
    #         "machiavellianism_index": 0,
    #         "narcissism_index": 5,
    #         "psychopathy_index": 0,
    #         "extroversion_index": 0,
    #         "nervousness_index": 0,
    #         "openn_index": 0,
    #         "agreeableness_index": 1,
    #         "conscientiousness_index": 0
    #     },
    #     "group_name": "测试九",
    #     "group_pinyin": "ceshijiu",
    #     "create_time": 1480176000,
    #     "create_date": "2016-11-27",
    #     "progress": 0
    # }
    # es.index(index='group_task',doc_type='text',id='ceshijiu_1480176000',body=dic)

    # user_query_body = {
    #     'query':{
    #         'match_all':{}
    #     }
    # }
    # user_generator = get_user_generator(USER_INFORMATION, user_query_body, USER_ITER_COUNT)
    # for res in user_generator:
    #     uid_list = []
    #     username_list = []
    #     for hit in res:
    #         uid_list.append(hit['_source']['uid'])
    #         username_list.append(hit['_source']['username'])
    #     user_ranking(uid_list, username_list, '2016-11-27')

    es.update(index='politics_information',doc_type='text',id='ceshizhengceyi_1552983497',body={'doc':{'progress':0}})

    # es.delete(index='event_information',doc_type='text',id='ceshishijianliu_1552978686')

    pass