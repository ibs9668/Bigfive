# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

ES_HOST = '219.224.134.214'
ES_PORT = 9200
ES_HOST_WEIBO = '219.224.134.225'
ES_PORT_WEIBO = 9225

es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
es_weibo = Elasticsearch(hosts=[{'host': ES_HOST_WEIBO, 'port': ES_PORT_WEIBO}], timeout=1000)

#common parameter
MAX_VALUE = 99999999

#user index
USER_ACTIVITY = 'user_activity'
USER_RANKING = 'user_ranking'
USER_SOCIAL_CONTACT = 'user_social_contact'
USER_INFORMATION = 'user_information'
USER_TEXT_ANALYSIS = 'user_text_analysis'
USER_TEXT_ANALYSIS_STA = 'user_text_analysis_sta'

#group index
GROUP_ACTIVITY = 'group_activity'
GROUP_INFORMATION = 'group_information'
GROUP_RANKING = 'group_ranking'

#cron_user parameter
USER_ITER_COUNT = 100
USER_WEIBO_ITER_COUNT = 10000

#cron_group parameter
GROUP_ITER_COUNT = 100

GROUP_AVE_ACTIVENESS_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_INFLUENCE_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_IMPORTANCE_RANK_THRESHOLD = [0.3, 0.7]
GROUP_DENSITY_THRESHOLD = [0.1, 0.3]