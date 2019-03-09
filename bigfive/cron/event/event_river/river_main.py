import sys
sys.path.append('../../../')
import json

from weibo_module import weibo_calculation

from config import *
from time_utils import *
from global_utils import *

COMMENT_WORDS_CLUSTER_NUM = 5
default_cluster_eva_min_size = 5
default_vsm = 'v1'

def river_main(event_mapping_name):
    print('Getting event weibo...')
    normal_list = subopinion_content(event_mapping_name) #读主观微博
    print('Calculating event river...')
    cluster_ratio,features = weibo_comments_list(normal_list)
    print('End Calculating event river...')
    return cluster_ratio,features

def subopinion_content(event_mapping_name):
    subopinion_results = []
    weibo_query_body = {
        'query':{
            'match_all':{}
        }
    }
    weibo_generator = get_event_weibo_generator(event_mapping_name, weibo_query_body, USER_WEIBO_ITER_COUNT)
    for res in weibo_generator:
        subopinion_results.extend(res)

    normal_list = []
    for key_weibo in subopinion_results:
        text_weibo = key_weibo['_source']['text']
        mid_weibo = key_weibo['_source']['mid']
        timestamp = key_weibo['_source']['timestamp']
        normal_list.append({'content':text_weibo,'id':mid_weibo,'timestamp':timestamp})
    print('event weibo num:%d' % len(normal_list))
    return normal_list    

def weibo_comments_list(weibo_list,cluster_num=COMMENT_WORDS_CLUSTER_NUM,cluster_eva_min_size=default_cluster_eva_min_size,vsm=default_vsm,calculation_label=1):#weibo_list把微博读进来
    # task_result_file = os.path.join(RESULT_WEIBO_FOLDER, taskid)
    # if os.path.exists(task_result_file) and calculation_label == 0:
    #     # 从已有数据文件加载结果集
    #     with open(task_result_file) as dump_file:
    #         dump_dict = json.loads(dump_file.read())
    #         ratio_results = dump_dict["ratio"]
    #         sentiratio_results = dump_dict["sentiratio"]
    #         before_filter_count = dump_dict["before_filter_count"]
    #         after_filter_count = dump_dict["after_filter_count"]

    #     return json.dumps({"ratio": ratio_results, "sentiratio": sentiratio_results, \
    #             "before_filter_count": before_filter_count, "after_filter_count": after_filter_count})

    comments = weibo_list
    cal_results = weibo_calculation(comments, cluster_num=cluster_num, \
            cluster_eva_min_size=int(cluster_eva_min_size), version=vsm)
    features = cal_results['cluster_infos']['features']
    word_main = cal_results['cluster_infos']['word_main']
    item_infos = cal_results['item_infos']
  
    cluster_ratio = dict()
    senti_ratio = dict()
    sentiment_results = dict()
    cluster_results = dict()
    rub_results = []

    # 过滤前文本数
    before_filter_count = len(item_infos)
    # 过滤后文本数
    after_filter_count = 0

    download_items = []
    for comment in item_infos:
        #print comment["clusterid"]
        download_item = {}
        #comment = item_infos[comment]
        download_item["id"] = comment["id"]
        download_item["text"] = comment["text"]
        download_item["clusterid"] = comment["clusterid"]
        download_item["ad_label"] = comment["ad_label"]
        # download_item["comment"] = comment["comment"]
        download_item["timestamp"] = comment["timestamp"]
        # download_item["retweeted"] = comment["retweeted"]
        # download_item["uid"] = comment["uid"]
        # download_item["same_from"] = comment["same_from"]
        download_items.append(download_item)
        weibo_date = ts2date(comment["timestamp"])
        if ('clusterid' in comment) and (comment['clusterid'][:8] != 'nonsense') : 
            clusterid = comment['clusterid']

            if weibo_date in cluster_ratio:
                cluster_ratio[weibo_date][clusterid] += 1
            else:
                cluster_ratio[weibo_date] = {str(i):0 for i in range(cluster_num)}
            try:
                cluster_results[clusterid].append(comment)
            except KeyError:
                cluster_results[clusterid] = [comment]


        if comment['clusterid'][:8] == 'nonsense':
            rub_results.append(comment)

    return cluster_ratio,features

if __name__ == '__main__':
    event_mapping_name = 'event_ceshishijianyi_1551942139'
    river_main(event_mapping_name)