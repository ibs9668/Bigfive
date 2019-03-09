import time
import sys
import json
sys.path.append('../')
sys.path.append('event')
sys.path.append('event/event_river')
from xpinyin import Pinyin

from config import *
from time_utils import *
from portrait.group.group_emotion import group_emotion_long
from portrait.group.group_preference_static import domain_topic_static, group_word_static
from cal_task import user_insert, group_create, group_ranking, cal_group_personality
from portrait.group.cron_group import group_activity, group_attribute_long
from cron_event import event_create, get_text_analyze
from event_mapping import create_event_mapping

def user_main():
    user_insert()

def group_main(args_dict,keyword,remark,group_name,create_time):
    # args_dict = {
    #     'machiavellianism_index':0,
    #     'narcissism_index':0,
    #     'psychopathy_index':0,
    #     'extroversion_index':0,
    #     'nervousness_index':0,
    #     'openn_index':0,
    #     'agreeableness_index':0,
    #     'conscientiousness_index':0,
    # }
    # keyword = '语言'
    # remark = '第五次群体测试'
    # group_name = '测试五'
    # create_time = date2ts('2016-11-27')

    print('Start finding userlist...')
    group_dic = group_create(args_dict,keyword,remark,group_name,create_time)

    print('Start calculating group activity...')
    group_activity(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'], 15)

    print('Start calculating group personality...')
    cal_group_personality(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group attribute...')
    group_attribute_long(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'], 15)

    print('Start calculating group topic static...')
    domain_topic_static(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group word static...')
    group_word_static(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group emotion...')
    group_emotion_long(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'], 15)
    
    print('Start calculating group ranking...')
    group_ranking(group_dic)


def event_main(keywords, event_id, start_date, end_date):
    print('Start creating event...')
    event_mapping_name = 'event_%s' % event_id
    create_event_mapping(event_mapping_name)
    userlist = event_create(event_mapping_name, keywords, start_date, end_date)
    es.update(index=EVENT_INFORMATION,doc_type='text',body={'doc':{'userlist':userlist}},id=event_id)

    print('Start text analyze...')
    # get_text_analyze(event_id, event_mapping_name)
    

if __name__ == '__main__':
    # user_main()
    # group_main(1,2,3,4,5)

    event_name = "测试事件三"
    event_pinyin = Pinyin().get_pinyin(event_name, '')
    create_time = 1551942139 #int(time.time())
    create_date = ts2date(create_time)
    start_date = '2016-11-13'
    end_date = '2016-11-27'
    keywords = "崛起"
    progress = 2
    event_id = event_pinyin + "_" + str(create_time)
    dic = {
        'event_name':event_name,
        'event_pinyin':event_pinyin,
        'create_time':create_time,
        'create_date':create_date,
        'keywords':keywords,
        'progress':progress,
        'event_id':event_id,
        'start_date':start_date,
        'end_date':end_date
    }
    es.index(index=EVENT_INFORMATION,doc_type='text',body=dic,id=event_id)
    time.sleep(1)
    event_main(keywords, event_id, start_date, end_date)