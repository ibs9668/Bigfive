import time
import sys
sys.path.append('../')

from config import *
from time_utils import *
from portrait.group.group_emotion import group_emotion
from portrait.group.group_preference_static import domain_topic_static, group_word_static
from cal_task import user_insert, group_create, group_ranking, cal_group_personality, group_attribute
from portrait.group.cron_group import group_activity

def user_main():
    user_insert()

def group_main(args_dict,keyword,remark,group_name,create_time):
    # args_dict = {
    #     'machiavellianism_index':1,
    #     'narcissism_index':5,
    #     'psychopathy_index':0,
    #     'extroversion_index':0,
    #     'nervousness_index':0,
    #     'openn_index':0,
    #     'agreeableness_index':0,
    #     'conscientiousness_index':0,
    # }
    # keyword = ''
    # remark = '第三次群体测试'
    # group_name = '测试三'
    # create_time = date2ts('2016-11-27')

    print('Start finding userlist...')
    group_dic = group_create(args_dict,keyword,remark,group_name,create_time)

    print('Start calculating group activity...')
    group_activity(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'], 15)

    print('Start calculating group personality...')
    cal_group_personality(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group attribute...')
    group_attribute(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group topic static...')
    domain_topic_static(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group word static...')
    group_word_static(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])

    print('Start calculating group emotion...')
    group_emotion(group_dic['group_id'], group_dic['userlist'], group_dic['create_date'])
    
    print('Start calculating group ranking...')
    group_ranking(group_dic)


if __name__ == '__main__':
    # user_main()
    group_main(1,2,3,4,5)