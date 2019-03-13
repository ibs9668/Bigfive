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
EVENT_GEO = 'event_geo'

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


MAP_CITIES_DICT = {'安徽': ['合肥市', '芜湖市', '蚌埠市', '淮南市', '马鞍山市', '淮北市', '铜陵市', '安庆市', '黄山市', '滁州市', '阜阳市', '宿州市', '六安市', '亳州市', '池州市', '宣城市'], '澳门': ['花地瑪堂區', '花王堂區', '望德堂區', '大堂區', '風順堂區', '嘉模堂區', '路氹填海區', '聖方濟各堂區'], '北京': ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '门头沟区', '房山区', '通州区', '顺义区', '昌平区', '大兴区', '怀柔区', '平谷区', '密云县', '延庆县'], '重庆': ['万州区', '涪陵区', '渝中区', '大渡口区', '江北区', '沙坪坝区', '九龙坡区', '南岸区', '北碚区', '綦江区', '大足区', '渝北区', '巴南区', '黔江区', '长寿区', '江津区', '合川区', '永川区', '南川区', '潼南区', '铜梁区', '荣昌区', '璧山区', '梁平县', '城口县', '丰都县', '垫江县', '武隆县', '忠县', '开县', '云阳县', '奉节县', '巫山县', '巫溪县', '石柱土家族自治县', '秀山土家族苗族自治县', '酉阳土家族苗族自治县', '彭水苗族土家族自治县'], '福建': ['福州市', '厦门市', '莆田市', '三明市', '泉州市', '漳州市', '南平市', '龙岩市', '宁德市'], '甘肃': ['兰州市', '嘉峪关市', '金昌市', '白银市', '天水市', '武威市', '张掖市', '平凉市', '酒泉市', '庆阳市', '定西市', '陇南市', '临夏回族自治州', '甘南藏族自治州'], '广东': ['广州市', '韶关市', '深圳市', '珠海市', '汕头市', '佛山市', '江门市', '湛江市', '茂名市', '肇庆市', '惠州市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市', '东莞市', '中山市', '潮州市', '揭阳市', '云浮市'], '广西': ['南宁市', '柳州市', '桂林市', '梧州市', '北海市', '防城港市', '钦州市', '贵港市', '玉林市', '百色市', '贺州市', '河池市', '来宾市', '崇左市'], '贵州': ['贵阳市', '六盘水市', '遵义市', '安顺市', '铜仁市', '黔西南布依族苗族自治州', '毕节市', '黔东南苗族侗族自治州', '黔南布依族苗族自治州'], '海南': ['海口市', '三亚市', '三沙市', '五指山市', '琼海市', '儋州市', '文昌市', '万宁市', '东方市', '定安县', '屯昌县', '澄迈县', '临高县', '白沙黎族自治县', '昌江黎族自治县', '乐东黎族自治县', '陵水黎族自治县', '保亭黎族苗族自治县', '琼中黎族苗族自治县'], '河北': ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市', '衡水市'], '黑龙江': ['哈尔滨市', '齐齐哈尔市', '鸡西市', '鹤岗市', '双鸭山市', '大庆市', '伊春市', '佳木斯市', '七台河市', '牡丹江市', '黑河市', '绥化市', '大兴安岭地区'], '河南': ['郑州市', '开封市', '洛阳市', '平顶山市', '安阳市', '鹤壁市', '新乡市', '焦作市', '濮阳市', '许昌市', '漯河市', '三门峡市', '南阳市', '商丘市', '信阳市', '周口市', '驻马店市', '济源市'], '湖北': ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市', '荆门市', '孝感市', '荆州市', '黄冈市', '咸宁市', '随州市', '恩施土家族苗族自治州', '仙桃市', '潜江市', '天门市', '神农架林区'], '湖南': ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市', '常德市', '张家界市', '益阳市', '郴州市', '永州市', '怀化市', '娄底市', '湘西土家族苗族自治州'], '江苏': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市', '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市'], '江西': ['南昌市', '景德镇市', '萍乡市', '九江市', '新余市', '鹰潭市', '赣州市', '吉安市', '宜春市', '抚州市', '上饶市'], '吉林': ['长春市', '吉林市', '四平市', '辽源市', '通化市', '白山市', '松原市', '白城市', '延边朝鲜族自治州'], '辽宁': ['沈阳市', '大连市', '鞍山市', '抚顺市', '本溪市', '丹东市', '锦州市', '营口市', '阜新市', '辽阳市', '盘锦市', '铁岭市', '朝阳市', '葫芦岛市'], '内蒙古': ['呼和浩特市', '包头市', '乌海市', '赤峰市', '通辽市', '鄂尔多斯市', '呼伦贝尔市', '巴彦淖尔市', '乌兰察布市', '兴安盟', '锡林郭勒盟', '阿拉善盟'], '宁夏': ['银川市', '石嘴山市', '吴忠市', '固原市', '中卫市'], '青海': ['西宁市', '海东市', '海北藏族自治州', '黄南藏族自治州', '海南藏族自治州', '果洛藏族自治州', '玉树藏族自治州', '海西蒙古族藏族自治州'], '山东': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '莱芜市', '临沂市', '德州市', '聊城市', '滨州市', '菏泽市'], '上海': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '闸北区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明县'], '山西': ['太原市', '大同市', '阳泉市', '长治市', '晋城市', '朔州市', '晋中市', '运城市', '忻州市', '临汾市', '吕梁市'], '陕西': ['西安市', '铜川市', '宝鸡市', '咸阳市', '渭南市', '延安市', '汉中市', '榆林市', '安康市', '商洛市'], '台湾': ['台湾省'], '四川': ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市', '广元市', '遂宁市', '内江市', '乐山市', '南充市', '眉山市', '宜宾市', '广安市', '达州市', '雅安市', '巴中市', '资阳市', '阿坝藏族羌族自治州', '甘孜藏族自治州', '凉山彝族自治州'], '天津': ['和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区', '滨海新区', '宁河县', '静海县', '蓟县'], '香港': ['中西區', '灣仔區', '東區', '南區', '油尖旺區', '深水埗區', '九龍城區', '黃大仙區', '觀塘區', '荃灣區', '屯門區', '元朗區', '北區', '大埔區', '西貢區', '沙田區', '葵青區', '離島區'], '新疆': ['乌鲁木齐市', '克拉玛依市', '吐鲁番地区', '哈密地区', '昌吉回族自治州', '博尔塔拉蒙古自治州', '巴音郭楞蒙古自治州', '阿克苏地区', '克孜勒苏柯尔克孜自治州', '喀什地区', '和田地区', '伊犁哈萨克自治州', '塔城地区', '阿勒泰地区', '石河子市', '阿拉尔市', '图木舒克市', '五家渠市', '北屯市', '铁门关市', '双河市'], '西藏': ['拉萨市', '昌都市', '山南地区', '日喀则市', '那曲地区', '阿里地区', '林芝市'], '云南': ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', '楚雄彝族自治州', '红河哈尼族彝族自治州', '文山壮族苗族自治州', '西双版纳傣族自治州', '大理白族自治州', '德宏傣族景颇族自治州', '怒江傈僳族自治州', '迪庆藏族自治州'], '浙江': ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市']}


EMOTION_MAP_NUM_CH = {
    '0':'中性', '1':'积极', '2':'生气', '3':'焦虑', '4':'悲伤', '5':'厌恶', '6':'消极其他'
    }
EMOTION_MAP_EN_CH = {
    'nuetral':'中性', 'positive':'积极', 'angry':'生气', 'anxiety':'焦虑', 'sad':'悲伤', 'hate':'厌恶', 'negtive':'消极其他'
}
EMOTION_MAP_NUM_EN = {
    '0':'nuetral', '1':'positive', '2':'angry', '3':'anxiety', '4':'sad', '5':'hate', '6':'negtive'
    }

DAY = 24*3600