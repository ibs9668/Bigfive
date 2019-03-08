import sys
sys.path.append('../../../')

from 

from config import *
from time_utils import *
from global_utils import *

def main():
    normal_list = subopinion_content(topic,start_ts,over_ts,weibo_limit) #读主观微博
    weibo_classify = json.loads(weibo_comments_list(taskid,normal_list,start_ts,over_ts))

def subopinion_content(topic,start_ts,end_ts,weibo_limit):
    # query_body ={'query':{
    #                 'bool':{
    #                     'must_not':[
    #                         {'wildcard':{'text':'*【*】*'}}],
    #                     'must':[
    #                         {'range':{'timestamp':{'lt':end_ts,'gte':start_ts}}
    #                     }]
    #                 }
    #             },
    #             'size':200#weibo_limit  
    #             }
    # subopinion_results = weibo_es.search(index=topic,doc_type=weibo_index_type,body=query_body)['hits']['hits']#['_source']
    subopinion_results = []
    for weibo_index in ES_INDEX_LIST:
        weibo_generator = get_event_weibo_generator(weibo_index, weibo_query_body, USER_WEIBO_ITER_COUNT)
            for res in weibo_generator:
                subopinion_results.extend(res)

    normal_list = []
    for key_weibo in subopinion_results:
        text_weibo = key_weibo['_source']['text']
        mid_weibo = key_weibo['_source']['mid']
        timestamp = key_weibo['_source']['timestamp']
        try:
            comment = key_weibo['_source']['comment']
        except:
            comment = 0
        try:
            retweeted = key_weibo['_source']['retweeted']
        except:
            retweeted = 0
        uid = key_weibo['_source']['uid']
        normal_list.append({'news_id':'weibo','content':text_weibo,'id':mid_weibo,'datetime':ts2datetime_full(timestamp),'comment':comment,'retweeted':retweeted,'uid':uid})
    return normal_list    

def weibo_comments_list(weibo_list,start_ts,end_ts,cluster_num=-1,cluster_eva_min_size=default_cluster_eva_min_size,vsm=default_vsm,calculation_label=1):#weibo_list把微博读进来
    task_result_file = os.path.join(RESULT_WEIBO_FOLDER, taskid)
    if os.path.exists(task_result_file) and calculation_label == 0:
        # 从已有数据文件加载结果集
        with open(task_result_file) as dump_file:
            dump_dict = json.loads(dump_file.read())
            ratio_results = dump_dict["ratio"]
            sentiratio_results = dump_dict["sentiratio"]
            before_filter_count = dump_dict["before_filter_count"]
            after_filter_count = dump_dict["after_filter_count"]

        return json.dumps({"ratio": ratio_results, "sentiratio": sentiratio_results, \
                "before_filter_count": before_filter_count, "after_filter_count": after_filter_count})

    comments = weibo_list
    print 'weibo_list:',len(comments)
    cal_results = weibo_calculation(comments, cluster_num=cluster_num, \
            cluster_eva_min_size=int(cluster_eva_min_size), version=vsm)
    features = cal_results['cluster_infos']['features']
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
        download_item["comment"] = comment["comment"]
        download_item["datetime"] = comment["datetime"]
        download_item["retweeted"] = comment["retweeted"]
        download_item["uid"] = comment["uid"]
        # download_item["same_from"] = comment["same_from"]
        download_items.append(download_item)
        if ('clusterid' in comment) and (comment['clusterid'][:8] != 'nonsense') : 
            clusterid = comment['clusterid']

            try:
                cluster_ratio[clusterid] += 1
            except KeyError:
                cluster_ratio[clusterid] = 1
            try:
                cluster_results[clusterid].append(comment)
            except KeyError:
                cluster_results[clusterid] = [comment]


        if comment['clusterid'][:8] == 'nonsense':
            rub_results.append(comment)

    ratio_results = dict()
    ratio_total_count = sum(cluster_ratio.values())
    for clusterid, ratio in cluster_ratio.iteritems():
        if clusterid in features:
            feature = features[clusterid]
            if feature and len(feature):
                ratio_results[','.join(feature[:3])] = float(ratio) / float(ratio_total_count)

    # 子观点分类去重
    cluster_dump_dict = dict()
    for clusterid, contents in cluster_results.iteritems():
        #print clusterid
        if clusterid in features:
            feature = features[clusterid]
            if feature and len(feature):
                dump_dict = dict()
                for comment in contents:
                    same_from_cluster = comment["same_from"]
                    try:
                        dump_dict[same_from_cluster].append(comment)
                    except KeyError:
                        dump_dict[same_from_cluster] = [comment]
                    cluster_dump_dict[clusterid] = dump_dict
    
    task = taskid.split('_')
    for key in features.keys():
        #print features[key],type(features[key])
        keys = ('_').join(features[key])
        index_body={'name':task[0],'start_ts':start_ts,'end_ts':end_ts,'ratio':json.dumps(ratio_results),'cluster':json.dumps(key),'features':json.dumps(features),'keys':keys,'cluster_dump_dict':json.dumps(cluster_dump_dict[key])}
        # print index_body
        #print subopinion_index_type,subopinion_index_name
        print 'dddddddddddddddddddd'
        weibo_es.index(index=subopinion_index_name,doc_type=subopinion_index_type,id=key,body=index_body)


    return json.dumps({"features":features,"ratio": ratio_results,"cluster_dump_dict":cluster_dump_dict})#features关键词和类的对应