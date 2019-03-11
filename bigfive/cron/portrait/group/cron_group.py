import sys
sys.path.append('../../../')

from config import *
from time_utils import *

from group_activity import group_activity
from group_attribute import group_attribute_long
from group_emotion import group_emotion_long
from group_preference_static import domain_topic_static, group_word_static

#计算群组的画像，给定用户列表、开始和结束日期进行计算
def group_portrait(group_id, uid_list, start_date, end_date):
    print('Calculating group position...')
    group_activity(group_id, uid_list, start_date, end_date)

    print('Calculating user domain and topic...')
    domain_topic_static(group_id, uid_list, end_date)
    
    print('Calculating word analysis...')
    group_word_static(group_id, uid_list, end_date)

    print('Calculating group attribute...')
    group_attribute_long(group_id, uid_list, start_date, end_date)

    print('Calculating group emotion...')
    group_emotion_long(group_id, uid_list, start_date, end_date)