# -*- coding: utf-8 -*-
import time

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

# event index
EVENT_INFORMATION = 'event_information'
EVENT_WORDCLOUD = 'event_wordcloud'
EVENT_RIVER = 'event_river'

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
PERSONALITY_LABEL_LIST=["machiavellianism_label","narcissism_label","psychopathy_label","extroversion_label",\
                        "nervousness_label","openn_label", "agreeableness_label", "conscientiousness_label"]

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
#政治倾向
POLITICAL_LABELS = ['left','right','mid']
LEFT_STA = 6000
RIGHT_STA = 3000


# 测试用的逻辑"今天"及"一周前"
today = '2016-11-27'
a_week_ago = time.strftime('%Y-%m-%d', time.localtime(int(time.mktime(time.strptime(today, '%Y-%m-%d'))) - 7 * 24 * 60 * 60))


map_cities_list = ["安徽","澳门","福建","甘肃","广东","广西","贵州","海南","河北","河南","黑龙江","湖北","湖南","吉林","江苏","江西","辽宁","内蒙古","青海","山东","山西","陕西","上海","四川","台湾","西藏","香港","新疆","云南","浙江","重庆","宁夏","北京","天津","石家庄","唐山","秦皇岛","邯郸","邢台","保定","张家口","承德","沧州","廊坊","衡水","太原","大同","阳泉","长治","晋城","朔州","晋中","运城","忻州","临汾","吕梁","呼和浩特","包头","乌海","赤峰","通辽","鄂尔多斯","呼伦贝尔","巴彦淖尔","乌兰察布","兴安盟","锡林郭勒盟","阿拉善盟","沈阳","大连","鞍山","抚顺","本溪","丹东","锦州","营口","阜新","辽阳","盘锦","铁岭","朝阳","葫芦岛","长春","吉林","四平","辽源","通化","白山","松原","白城","延边朝鲜族自治州","哈尔滨","齐齐哈尔","鸡西","鹤岗","双鸭山","大庆","伊春","佳木斯","七台河","牡丹江","黑河","绥化","大兴安岭地区","上海","南京","无锡","徐州","常州","苏州","南通","连云港","淮安","盐城","扬州","镇江","泰州","宿迁","杭州","宁波","温州","嘉兴","湖州","绍兴","金华","衢州","舟山","台州","丽水","合肥","芜湖","蚌埠","淮南","马鞍山","淮北","铜陵","安庆","黄山","滁州","阜阳","宿州","巢湖","六安","亳州","宣城","福州","厦门","莆田","三明","泉州","漳州","南平","龙岩","宁德","南昌","景德镇","萍乡","九江","新余","鹰潭","赣州","吉安","宜春","抚州","上饶","济南","青岛","淄博","枣庄","东营","烟台","潍坊","济宁","泰安","威海","日照","莱芜","临沂","德州","聊城","滨州","菏泽","郑州","开封","洛阳","平顶山","安阳","鹤壁","新乡","焦作","濮阳","许昌","三门峡","南阳","商丘","信阳","周口","驻马店","武汉","黄石","十堰","宜昌","襄阳","鄂州","荆门","孝感","荆州","黄冈","咸宁","随州","恩施土家族苗族自治州","仙桃","长沙","株洲","湘潭","衡阳","邵阳","岳阳","常德","张家界","益阳","郴州","永州","怀化","娄底","湘西土家族苗族自治州","广州","韶关","深圳","珠海","汕头","佛山","江门","湛江","茂名","肇庆","惠州","梅州","汕尾","河源","阳江","清远","东莞","中山","潮州","揭阳","云浮","南宁","柳州","桂林","梧州","北海","防城港","钦州","贵港","玉林","百色","贺州","河池","来宾","崇左","海口","三亚","五指山","琼海","儋州","文昌","万宁","东方","重庆","成都","自贡","攀枝花","泸州","德阳","绵阳","广元","遂宁","内江","乐山","南充","眉山","宜宾","广安","达州","雅安","巴中","资阳","阿坝藏族羌族自治州","甘孜藏族自治州","凉山彝族自治州","贵阳","六盘水","遵义","安顺","铜仁地区","兴义","毕节地区","黔东南苗族侗族自治州","昆明","曲靖","玉溪","保山","昭通","丽江","墨江哈尼族自治县","临沧","楚雄彝族自治州","红河哈尼族彝族自治州","文山壮族苗族自治州","西双版纳傣族自治州","大理白族自治州","大理白族自治州","德宏傣族景颇族自治州","怒江傈僳族自治州","迪庆藏族自治州","拉萨","昌都地区","山南地区","日喀则地区","那曲地区","林芝地区","西安","铜川","宝鸡","咸阳","渭南","延安","汉中","榆林","安康","商洛","兰州","嘉峪关","金昌","白银","天水","武威","张掖","平凉","酒泉","庆阳","定西","陇南","临夏回族自治州","甘南藏族自治州","西宁","海东地区","海北藏族自治州","黄南藏族自治州","海南藏族自治州","果洛藏族自治州","玉树藏族自治州","海西蒙古族藏族自治州","银川","石嘴山","吴忠","固原","中卫","乌鲁木齐","克拉玛依","吐鲁番地区","哈密地区","昌吉回族自治州","博尔塔拉蒙古自治州","巴音郭楞蒙古自治州","阿克苏地区","阿图什","喀什地区","和田地区","伊犁哈萨克自治州","塔城地区","阿勒泰地区","石河子","香港","澳门","台北","高雄","基隆","台中","台南","新竹","嘉义"]