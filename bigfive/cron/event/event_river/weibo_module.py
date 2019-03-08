from ad_filter import ad_filter
from opinion_produce import rubbish_classifier,opinion_main

def weibo_calculation(comments, cluster_num=COMMENT_WORDS_CLUSTER_NUM, \
        cluster_eva_min_size=CLUSTER_EVA_MIN_SIZE, \
        version=COMMENT_CLUSTERING_PROCESS_FOR_CLUTO_VERSION):
    """评论计算
       将sentiment和clustering的结果进行合并，取并集
       cluster_infos: 聚簇信息
       item_infos:  单条信息列表
                    情绪数据字段：sentiment、same_from、duplicate
                    聚类数据字段：clusterid、weight、same_from、duplicate
                    合并后：sentiment、same_from_sentiment、duplicate_sentiment、
                            clusterid、weight、same_from、duplicate
    """
    print('-------------------------------')
    print('start weibo calculation')

    # backup copy
    comments_copy = copy.deepcopy(comments)

    # 观点计算
    print('start weibo clustering calculation')
    clustering_results = comments_rubbish_clustering_calculation(comments_copy, logger, \
            cluster_num=cluster_num, \
            cluster_eva_min_size=cluster_eva_min_size, \
            version=version)
    print('end weibo clustering calculation')

    return {'cluster_infos': clustering_results['cluster_infos'], 'item_infos': clustering_results['item_infos']}

def comments_rubbish_clustering_calculation(comments, logger, cluster_num=COMMENT_WORDS_CLUSTER_NUM, \
        cluster_eva_min_size=CLUSTER_EVA_MIN_SIZE, \
        version=COMMENT_CLUSTERING_PROCESS_FOR_CLUTO_VERSION):
    """评论垃圾过滤、聚类
       input: comments
           comment中包含news_id, news_content
       cluster_infos: 聚簇信息
       item_infos:单条信息列表, 数据字段：clusterid、weight、same_from、duplicate
    """
    # 无意义信息的clusterid，包括ad_filter分出来的广告，svm分出的垃圾，主客观分类器分出的新闻
    NON_CLUSTER_ID = 'nonsense'

    # 其他类的clusterid
    OTHER_CLUSTER_ID = 'other'

    # 直接显示的clusterid
    DIRECT_CLUSTER_ID = 'direct'
    DIRECT_CLUSTER_FEATURE = [u'聚簇']

    # 最小聚类输入信息条数，少于则不聚类
    MIN_CLUSTERING_INPUT = 20

    # 簇信息，主要是簇的特征词信息
    clusters_infos = {'features': dict()}

    # 单条信息list，每条信息存储 clusterid weight sentiment字段
    items_infos = []

    # 数据字段预处理
    inputs = []
    for r in comments:
        r['title'] = ''
        r['content168'] = r['content'].encode('utf-8')
        r['content'] = r['content168']
        r['text'] = r['content']
        if 'news_content' in r and r['news_content']:
            r['news_content'] = r['news_content'].encode('utf-8')
        else:
            r['news_content'] = ''

        # 简单规则过滤广告
        item = ad_filter(r)
        if item['ad_label'] == 0:
            inputs.append(item)
        else:
            item['clusterid'] = NON_CLUSTER_ID + '_rub'
            items_infos.append(item)

    # svm去除垃圾
    if len(inputs) == 0:
        items = []
    else:
        items = rubbish_classifier(inputs)
    inputs = []
    for item in items:
        if item['rub_label'] == 1:
            item['clusterid'] = NON_CLUSTER_ID + '_rub'
            items_infos.append(item)
        else:
            inputs.append(item)
    
    if len(inputs) >= 500:
        opinion_name,word_result,text_list = opinion_main(inputs,10)
    else:
        opinion_name,word_result,text_list = opinion_main(inputs,5)

    for k,v in word_result.iteritems():
        #name = opinion_name[k]
        clusters_infos['features'][k] = v


##    for k,v in text_list.iteritems():
##        for item in v:
##            row=copy.deepcopy(item)
##            row['clusterid'] = k
##            items_infos.append(row)
    
    final_inputs = []
    for k,v in text_list.iteritems():
        for item in v:
            row=copy.deepcopy(item)
            row['clusterid'] = k
            final_inputs.append(row)

    # 去重，根据子观点类别去重
    cluster_items = dict()
    for r in final_inputs:
        clusterid = r['clusterid']
        try:
            cluster_items[clusterid].append(r)
        except KeyError:
            cluster_items[clusterid] = [r]

    for clusterid, items in cluster_items.iteritems():
        results = duplicate(items)
        items_infos.extend(results)
    
    
    return {'cluster_infos': clusters_infos, 'item_infos': items_infos}