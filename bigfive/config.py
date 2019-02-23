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

#group index
GROUP_ACTIVITY = 'group_activity'
GROUP_INFORMATION = 'group_information'
GROUP_RANKING = 'group_ranking'

#cron_group parameter
GROUP_ITER_COUNT = 100

GROUP_AVE_ACTIVENESS_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_INFLUENCE_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_IMPORTANCE_RANK_THRESHOLD = [0.3, 0.7]
