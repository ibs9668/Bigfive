import time
import sys
sys.path.append('../')

from config import *
from time_utils import *
from cal_task import user_insert, group_create, group_ranking
from portrait.group.cron_group import group_activity

def user_main():
    user_insert()

def group_main():
    args_dict = {
        'machiavellianism_index':1,
        'narcissism_index':2,
        'psychopathy_index':3,
        'extroversion_index':0,
        'nervousness_index':0,
        'openn_index':0,
        'agreeableness_index':0,
        'conscientiousness_index':0,
    }
    keyword = ''
    remark = '明哥的确是厉害'
    group_name = '明哥厉害'
    create_time = int(time.time())

    print('Start finding userlist...')
    group_dic = group_create(args_dict,keyword,remark,group_name,create_time)

    print('Start calculating group activity...')
    group_activity(group_dic['group_id'], group_dic['userlist'], '2016-11-27', 15)
    
    print('Start calculating group ranking...')
    group_ranking(group_dic)


if __name__ == '__main__':
    group_main()