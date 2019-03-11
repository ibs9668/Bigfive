import sys
sys.path.append('../../../')
from config import *
from time_utils import *
from global_utils import *

from user_ip import get_user_activity
from user_topic import get_user_topic
from user_domain import get_user_domain
from user_political import get_user_political
from user_text_analyze import word_analysis

def user_portrait(uid, date):
    print('Calculating user position...')
    get_user_activity(uid,date)

    print('Calculating user topic...')
    get_user_topic(uid,date,7)

    print('Calculating user domain...')
    get_user_domain(uid,date,7)

    print('Calculating user political...')
    get_user_political(uid, date, 7)

    print('Calculating word analysis...')
    word_analysis(uid, date, 30)

    print('Calculating word analysis...')


    print('Calculating word analysis...')


    print('Calculating word analysis...')