# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

ES_HOST = '219.224.134.214'
ES_PORT = 9200
ES_HOST_WEIBO = '219.224.134.225'
ES_PORT_WEIBO = 9225
REDIS_HOST = '219.224.134.226'
REDIS_PORT = 10010

es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
es_weibo = Elasticsearch(hosts=[{'host': ES_HOST_WEIBO, 'port': ES_PORT_WEIBO}], timeout=1000)

# common parameter
MAX_VALUE = 99999999

# user index
USER_ACTIVITY = 'user_activity'
USER_DOMAIN_TOPIC = 'user_domain_topic'
USER_RANKING = 'user_ranking'
USER_SOCIAL_CONTACT = 'user_social_contact'
USER_INFORMATION = 'user_information'
USER_TEXT_ANALYSIS = 'user_text_analysis'
USER_TEXT_ANALYSIS_STA = 'user_text_analysis_sta'
USER_INFLUENCE = 'user_influence'
USER_PERSONALITY = 'user_personality'

# group index
GROUP_ACTIVITY = 'group_activity'
GROUP_INFORMATION = 'group_information'
GROUP_RANKING = 'group_ranking'
GROUP_TASK = 'group_task'
GROUP_INFLUENCE = 'group_influence'
GROUP_PERSONALITY = 'group_personality'
GROUP_DOMAIN_TOPIC = 'group_domain_topic'
GROUP_TEXT_ANALYSIS_STA = "group_text_analysis_sta"

# cron_user parameter
USER_ITER_COUNT = 100
USER_WEIBO_ITER_COUNT = 10000

USER_MACHIAVELLIANISM_THRESHOLD = [20,80]
USER_NARCISSISM_THRESHOLD = [20,80]
USER_PSYCHOPATHY_THRESHOLD = [20,80]
USER_EXTROVERSION_THRESHOLD = [20,80]
USER_NERVOUSNESS_THRESHOLD = [20,80]
USER_OPENN_THRESHOLD = [20,80]
USER_AGREEABLENESS_THRESHOLD = [20,80]
USER_CONSCIENTIOUSNESS_THRESHOLD = [20,80]

USER_NORMALIZATION_IMPORTANCE = [25,172]
USER_NORMALIZATION_SENSITIVITY = [0,100]
USER_NORMALIZATION_INFLUENCE = [0,1000]
USER_NORMALIZATION_ACTIVITY = [0,4.33472983]

# cron_group parameter
GROUP_ITER_COUNT = 100

GROUP_AVE_ACTIVENESS_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_INFLUENCE_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_IMPORTANCE_RANK_THRESHOLD = [0.3, 0.7]
GROUP_AVE_SENSITIVITY_RANK_THRESHOLD = [0.3, 0.7]
GROUP_DENSITY_THRESHOLD = [0.1, 0.3]

#人格字典
PERSONALITY_DIC = {
    'machiavellianism_index':{'name':'马基雅维里主义','threshold':USER_MACHIAVELLIANISM_THRESHOLD},
    'narcissism_index':{'name':'自恋','threshold':USER_NARCISSISM_THRESHOLD},
    'psychopathy_index':{'name':'精神病态','threshold':USER_PSYCHOPATHY_THRESHOLD},
    'extroversion_index':{'name':'外倾性','threshold':USER_EXTROVERSION_THRESHOLD},
    'nervousness_index':{'name':'神经质','threshold':USER_NERVOUSNESS_THRESHOLD},
    'openn_index':{'name':'开放性','threshold':USER_OPENN_THRESHOLD},
    'agreeableness_index':{'name':'开放性','threshold':USER_AGREEABLENESS_THRESHOLD},
    'conscientiousness_index':{'name':'尽责性','threshold':USER_CONSCIENTIOUSNESS_THRESHOLD}
}

#画像字典
ATTRIBUTE_DIC = {
    'importance':{'name':'重要度',"threshold":USER_NORMALIZATION_IMPORTANCE},
    'sensitivity':{'name':'敏感度',"threshold":USER_NORMALIZATION_SENSITIVITY},
    'influence':{'name':'影响力',"threshold":USER_NORMALIZATION_INFLUENCE},
    'activity':{'name':'活跃度',"threshold":USER_NORMALIZATION_ACTIVITY}
}

# 情感分类 0中性 1积极
SENTIMENT_INDEX_LIST = [0, 1]
# 微博信息类型表  2评论 3转发
MESSAGE_TYPE_LIST = [2, 3]

# 微博存量数据索引
ES_INDEX_LIST = ["flow_text_2016-11-13", "flow_text_2016-11-14", "flow_text_2016-11-15", "flow_text_2016-11-16",
                 "flow_text_2016-11-17", "flow_text_2016-11-18", "flow_text_2016-11-19", "flow_text_2016-11-20",
                 "flow_text_2016-11-21", "flow_text_2016-11-22", "flow_text_2016-11-23", "flow_text_2016-11-24",
                 "flow_text_2016-11-25", "flow_text_2016-11-26", "flow_text_2016-11-27"]

# 微博话题种类
TOPIC_LIST = ['art', 'computer', 'economic', 'education', 'environment', 'medicine', \
              'military', 'politics', 'sports', 'traffic', 'life', \
              'anti-corruption', 'employment', 'fear-of-violence', 'house', \
              'law', 'peace', 'religion', 'social-security']
zh_TOPIC_LIST = ['文体类_娱乐', '科技类', '经济类', '教育类', '民生类_环保', '民生类_健康', \
                 '军事类', '政治类_外交', '文体类_体育', '民生类_交通', '其他类', \
                 '政治类_反腐', '民生类_就业', '政治类_暴恐', '民生类_住房', '民生类_法律', \
                 '政治类_地区和平', '政治类_宗教', '民生类_社会保障']
# 用户领域种类
txt_labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
              'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'business']
labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg', \
          'lawyer', 'politician', 'mediaworker', 'activer', 'grassroot', 'other', 'business']
zh_labels = ['高校', '境内机构', '境外机构', '媒体', '境外媒体', '民间组织', '法律机构及人士', \
             '政府机构及人士', '媒体人士', '活跃人士', '草根', '其他', '商业人士']

labels_dict = {'university': '高校', 'homeadmin': '境内机构', 'abroadadmin': '境外机构', 'homemedia': '媒体', 'abroadmedia': '境外媒体',
               'folkorg': '民间组织', 'lawyer': '法律机构及人士', 'politician': '政府机构及人士', 'mediaworker': '媒体人士',
               'activer': '活跃人士', 'grassroot': '草根', 'other': '其他', 'business': '商业人士'}
topic_dict = {'art': '文体类_娱乐', 'computer': '科技类', 'economic': '经济类', 'education': '教育类', 'environment': '民生类_环保',
              'medicine': '民生类_健康', 'military': '军事类', 'politics': '政治类_外交', 'sports': '文体类_体育', 'traffic': '民生类_交通',
              'life': '其他类', 'anti_corruption': '政治类_反腐', 'employment': '民生类_就业', 'fear_of_violence': '政治类_暴恐',
              'house': '民生类_住房', 'law': '民生类_法律', 'peace': '政治类_地区和平', 'religion': '政治类_宗教',
              'social_security': '民生类_社会保障', 'violence': '政治类_暴恐',}

outlist = [u'海外', u'香港', u'台湾', u'澳门']
lawyerw = [u'律师', u'法律', u'法务', u'辩护']
STATUS_THRE = 4000
FOLLOWER_THRE = 1000
