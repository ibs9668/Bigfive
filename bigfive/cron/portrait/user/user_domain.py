#-*-coding=utf-8-*-

import os
import re
import sys
import json
import csv
import heapq
from decimal import *
import jieba

import sys
sys.path.append('../../../')
from config import *
from time_utils import *
from global_utils import ESIterator

ABS_PATH = os.path.dirname(os.path.abspath(__file__))


#############微博文本######################
##加载领域词典

def load_train():

    domain_dict = dict()
    domain_count = dict()
    for i in txt_labels:
        reader = csv.reader(open(os.path.join(ABS_PATH, 'domain_dict/%s.csv'% i), 'r'))
        word_dict = dict()
        count = 0
        for f,w_text in reader:
            f = f.strip('\xef\xbb\xbf')
            word_dict[str(w_text)] = float(f)
            count = count + float(f)
        domain_dict[i] = word_dict
        domain_count[i] = count

    len_dict = dict()
    total = 0
    for k,v in domain_dict.items():
        len_dict[k] = len(v)
        total = total + len(v)
    
    return domain_dict,domain_count,len_dict,total

DOMAIN_DICT,DOMAIN_COUNT,LEN_DICT,TOTAL = load_train()

##标准化领域字典
def start_p():

    domain_p = dict()
    for name in txt_labels:
        domain_p[name] = 0

    return domain_p

DOMAIN_P = start_p()
##标准化结束

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in range(len(self.data))])]

def com_p(word_list,domain_dict,domain_count,len_dict,total):

    p = 0
    test_word = set(word_list.keys())
    train_word = set(domain_dict.keys())
    c_set = test_word & train_word
    p = sum([float(domain_dict[k]*word_list[k])/float(domain_count) for k in c_set])

    return p

def rank_dict(has_word):

    n = len(has_word)
    keyword = TopkHeap(n)
    count = Decimal(0)
    for k,v in has_word.items():
        keyword.Push((v,k))
        count = count + Decimal(v)

    if count > 0:
        keyword_data = keyword.TopK()
        label = txt_labels[txt_labels.index(keyword_data[0][1])]
    else:
        label = 'other'
        keyword_data = keyword.TopK()
    return label,keyword_data

def domain_classfiy_by_text(user_weibo):#根据用户微博文本进行领域分类
    '''
    输入数据：字典
    {uid:{'key1':f1,'key2':f2...},...}
    输出数据：字典
    {uid:label1,uid2:label2,...}
    '''

    result_data = dict()
    p_data = dict()
    for k,v in user_weibo.items():
        start = time.time()
        domain_p = DOMAIN_P
        for d_k in domain_p.keys():
            domain_p[d_k] = com_p(v,DOMAIN_DICT[d_k],DOMAIN_COUNT[d_k],LEN_DICT[d_k],TOTAL)#计算文档属于每一个类的概率
            end_time = time.time()
        label,rank_data = rank_dict(domain_p)
        result_data[k] = label
        p_data[k] = rank_data

    return result_data,p_data
    

####################认证类型##########################

def user_domain_classifier_v2(user):
    r = user
    label = labels[11]

    verified_type = r['verified_type']
    location = r['user_location']
    province = location.split(' ')[0]

    followers_count = r['fans_num']
    statuses_count = r['statusnum']

    name = r['username']
    description = r['description']

    if verified_type == 4:
        label = labels[0] # 高校微博

    elif verified_type == 1:
        label = labels[7]#政府机构及人士
        
    elif verified_type == 8 or verified_type == 7 or verified_type == 2:
        if province not in outlist:
            label = labels[1] # 境内机构
        else:
            label = labels[2] # 境外机构

    elif verified_type == 3:
        if location not in outlist:
            label = labels[3] # 境内媒体
        else:
            label = labels[4] # 境外媒体 

    elif verified_type == 5 or verified_type == 6:
        label = labels[5] # 民间组织

    elif verified_type == 0:
        text = name + description
        segment_list= " ".join(jieba.cut(text, cut_all=False))
        kwdlist = segment_list.split(' ')

        # kwdlist = cut(s, text)
        lawyer_weight = sum([1 for keyword in kwdlist if keyword in lawyerw]) # 律师
        adminw_weight = sum([1 for keyword in kwdlist if keyword in adminw]) # 政府官员
        mediaw_weight = sum([1 for keyword in kwdlist if keyword in mediaw]) # 媒体人士
        businessw_weight = sum([1 for keyword in kwdlist if keyword in businessw]) # 商业人士

        max_weight = 0
        '''
        if max_weight < lawyer_weight:
            max_weight = lawyer_weight
            label = labels[6]
        '''
        
        if max_weight < businessw_weight:
            max_weight = businessw_weight
            label = labels[12]

        if max_weight < adminw_weight:
            max_weight = adminw_weight
            label = labels[7]

        if max_weight < mediaw_weight:
            max_weight = mediaw_weight
            label = labels[8]

        if max_weight == 0:
            label = labels[9]

        if lawyer_weight!=0:
            label = labels[6]

    elif verified_type == 220 or verified_type == 200:
        label = labels[9]

    elif verified_type == 400:
        label = labels[11]    

    else:
        if followers_count >= FOLLOWER_THRE and statuses_count >= STATUS_THRE:
            label = labels[10] # 草根

        lawyer_weight = 0
        text = name + description
        segment_list= " ".join(jieba.cut(text, cut_all=False))
        kwdlist = segment_list.split(' ')

        # kwdlist = cut(s, text)
        lawyer_weight = sum([1 for keyword in kwdlist if keyword in lawyerw])

        if lawyer_weight != 0:
            label = labels[6]

    return label



###################用户&&粉丝结构#####################
def readProtoUser():
    f = open(os.path.join(ABS_PATH, "protou_combine/protou.txt"), "r")
    protou = dict()
    for line in f:
        area=line.split(":")[0]
        if area not in protou:
            protou[area]=set()
        for u in (line.split(":")[1]).split():
            protou[area].add(str(u))

    return protou

proto_users = readProtoUser()

def readTrainUser():

    txt_list = ['abroadadmin','abroadmedia','business','folkorg','grassroot','activer',\
                'homeadmin','homemedia','lawyer','mediaworker','politician','university']
    data = dict()
    for i in range(0,len(txt_list)):
        f = open(os.path.join(ABS_PATH, "domain_combine/%s.txt" % txt_list[i]),"r")
        item = []
        for line in f:
            line = line.strip('\r\n')
            item.append(line)
        data[txt_list[i]] = set(item)
        f.close()

    return data

train_users = readTrainUser()


def getFieldFromProtou(uid, protou_dict=train_users):#判断一个用户是否在种子列表里面

    result = 'Null'
    for k,v in protou_dict.items():
        if uid in v:
            return k

    return result


def user_domain_classifier_v1(friends, fields_value=txt_labels, protou_dict=proto_users):#根据用户的粉丝列表对用户进行分类
    mbr = {'university':0, 'homeadmin':0, 'abroadadmin':0, 'homemedia':0, 'abroadmedia':0, 'folkorg':0, 
          'lawyer':0, 'politician':0, 'mediaworker':0, 'activer':0, 'grassroot':0, 'other':0, 'business':0}
   
    # to record user with friends in proto users

    if len(friends) == 0:
         mbr['other'] += 1
    else:
        for area in fields_value:
            c_set = set(friends) & set(protou_dict[area]) #计算粉丝和每个领域的交集个数，并存在 {mbr} 中
            mbr[area] = len(c_set)
     
    count = 0
    count = sum([v for v in mbr.values()])

    if count == 0:
        return 'other',mbr
    
    sorted_mbr = sorted(mbr.items(), key=lambda x: x[1], reverse=True)  ##排序，粉丝数最多的领域 即为用户所在领域
    field1 = sorted_mbr[0][0]

    return field1,mbr


####################从3种分类结果选出一个标签##################
r_labels = ['university', 'homeadmin', 'abroadadmin', 'homemedia', 'abroadmedia', 'folkorg',]
def get_recommend_result(v_type,label):#根据三种分类结果选出一个标签

    if v_type == 'other':#认证类型字段走不通
        if label[0] != 'other':
            return label[0]
        else:
            return label[2]

    if label[1] in r_labels:#在给定的类型里面分出来的身份
        return label[1]

    if label[1] == 'politician' and v_type == 1:
        return label[1]

    if label[1] == 'activer' and (v_type == 220 or v_type == 200):
        return label[1]

    if label[1] == 'other' and v_type == 400:
        return label[1]

    if label[0] != 'other':#根据粉丝结构分出来身份
        return label[0]
    else:
        return label[2]

####################################

def stopwordslist():

    stopwords = [line.strip() for line in open('stop_words.txt').readlines()]
    return stopwords

def segment(doc):
    '''
    用jieba分词对输入文档进行分词，并保存至本地（根据情况可跳过）
    '''
    seg_list = " ".join(jieba.cut(doc, cut_all=False)) #seg_list为str类型

    return seg_list


def wordCount(segment_list):
    '''
        该函数实现词频的统计，并将统计结果存储至本地。
        在制作词云的过程中用不到，主要是在画词频统计图时用到。
    '''
    stopwords = stopwordslist()
    # print len(stopwords)
    word_lst = []
    word_dict = {}
   
    word_lst = segment_list.split(' ')
    for item in word_lst:
        if item not in stopwords:
            if item not in word_dict: 
                word_dict[item] = 1
            else:
                word_dict[item] += 1

    word_dict_sorted = dict(sorted(word_dict.items(), \
    key = lambda item:item[1], reverse=True))#按照词频从大到小排序

    return word_dict_sorted



######################领域分类主函数###################
zh_text = ['nick_name','rel_name','description','sp_type','user_location']


# def get_uidlist():
#     query_body = {"query": {"bool": {"must": [{"match_all": { }}]}},"size":15000}
#     es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"]
#     uid_list = []
#     for es_item in es_result:
#         uid_list.append(es_item["_id"])
#     return uid_list


def get_uid_weibo(uid,index_name):

    uid_word_dict = dict()
    uid_text = ""

    for index_item in index_name:

        query_body ={"query": {"bool": {"must":[{"term": {"uid": uid}}]}}}
        sort_dict = {'_id':{'order':'asc'}}
        try:
            ESIterator1 = ESIterator(0,sort_dict,1000,index_item,"text",query_body,es_weibo)
            while True:
                try:
                    #一千条es数据
                    es_result = next(ESIterator1)
                    if len(es_result):
                        for i in range(len(es_result)):
                            uid_text += es_result[i]["_source"]["text"] 
                    else:
                        pass
                       
                except StopIteration:
                    #遇到StopIteration就退出循环
                    break
        except:
            continue

    if uid_text != "":
        segment_list = segment(uid_text)
        word_count_dict = wordCount(segment_list)
        uid_word_dict[uid] = word_count_dict
    else:
        return uid_word_dict

    return uid_word_dict



def get_user(uid):
    user_dict = dict()
    query_body = {"query":{"bool":{"must":[{"term":{"uid":uid}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}
    
    if es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"] != []:
        es_result = es.search(index="user_information", doc_type="text",body=query_body)["hits"]["hits"][0]["_source"]
    else:
        return {uid:{"verified_type":"other","fans_num":0,"username":"","description":"","verified_type":999,"statusnum":0,\
                "user_location":""}}



    user_dict = dict()
    information_dict = dict()

    information_dict["user_location"] = es_result["user_location"]
    information_dict["fans_num"] = es_result["fans_num"]
    information_dict["username"] = es_result["username"]
    information_dict["description"] = es_result["description"]

    try:
        information_dict["verified_type"] = es.search(index="weibo_user", doc_type="text",body=query_body)["hits"]["hits"][0]["_source"]["verified_type"]
        information_dict["statusnum"] = es.search(index="weibo_user", doc_type="text",body=query_body)["hits"]["hits"][0]["_source"]["statuses_count"]
    except Exception as ex:
        information_dict["verified_type"] = 999
        information_dict["statusnum"] = 0 

    user_dict[uid] = information_dict
        
    return user_dict

def get_friends(uid):
    friends_list = []
    query_body = {"query":{"bool":{"must":[{"term":{"uid":uid}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}
    try:
        friends_list = es.search(index="weibo_user", doc_type="text",body=query_body)["hits"]["hits"][0]["_source"]["friends"]
    except Exception as ex:
        friends_list = []

    return friends_list


def domain_classfiy(uid,uid_weibo,timestamp):#领域分类主函数
    '''
    用户领域分类主函数
    输入数据示例：
    uid_list:uid列表 [uid1,uid2,uid3,...]
    uid_weibo:分词之后的词频字典  {uid1:{'key1':f1,'key2':f2...}...}

    输出数据示例：
    domain：标签字典
    {uid1:[label1,label2,label3],uid2:[label1,label2,label3]...}
    注：label1是根据粉丝结构分类的结果，label2是根据认证类型分类的结果，label3是根据用户文本分类的结果

    re_label：推荐标签字典
    {uid1:label,uid2:label2...}
    '''
    domain_dict = dict()
    domain_label =""

    if not len(uid_weibo) :
        return domain_dict,domain_label
    else:
        pass

    users = get_user(uid) #用户信息字典
    f = get_friends(uid) #粉丝列表

    k =  uid
    result_label = []
    sorted_mbr = dict()
    field1 = getFieldFromProtou(k, protou_dict=train_users)#判断uid是否在种子用户里面

    if field1 != 'Null':#该用户在种子用户里面
        result_label.append(field1)
        domain_dict["field1"] = field1
    else:
        if len(f):
            field1,sorted_mbr = user_domain_classifier_v1(f, fields_value=txt_labels, protou_dict=proto_users) #根据用户粉丝分类
        else:
            field1 = 'other'
            sorted_mbr = {'university':0, 'homeadmin':0, 'abroadadmin':0, 'homemedia':0, 'abroadmedia':0, 'folkorg':0, \
                          'lawyer':0, 'politician':0, 'mediaworker':0, 'activer':0, 'grassroot':0, 'other':0, 'business':0}
        
        result_label.append(field1)
        domain_dict["field1"] = field1
    

    r = list(users.values())[0]
    if r == 'other':
        field2 = 'other'
    else: 
        field2 = user_domain_classifier_v2(r)  #根据注册信息分类
    result_label.append(field2)
    domain_dict["field2"] = field2

    if k in uid_weibo.keys() and len(uid_weibo[k]):
        field_dict,result = domain_classfiy_by_text({k: uid_weibo[k]})#根据用户文本进行分类
        field3 = field_dict[k]
    else:
        field3 = 'other'
    result_label.append(field3)
    domain_dict["field3"] = field3
            

    if r == 'other':
        domain_label = get_recommend_result('other',result_label)#没有认证类型字段
    else:
        domain_label = get_recommend_result(r['verified_type'],result_label)

    return domain_dict,domain_label

def save_user_domain(uid,timestamp,domain,r_domain):
    id_body = {
            "query":{
                "ids":{
                    "type":"text",
                    "values":[
                        str(uid)+"_"+str(timestamp)
                    ]
                }
            }
        }

    if domain!={} and r_domain!="":

        if es.search(index=USER_DOMAIN_TOPIC, doc_type='text', body= id_body)["hits"]["hits"] != []:
            es.update(index=USER_DOMAIN_TOPIC, doc_type='text', id=str(uid)+"_"+str(timestamp), body = {
            "doc":{
            "domain_followers":domain["field1"],
            "domain_weibo":domain["field3"],
            "domain_verified":domain["field2"],
            "main_domain" : r_domain,
            "has_new_information":1
                    } })
           
        else:
            es.index(index=USER_DOMAIN_TOPIC, doc_type='text', id=str(uid)+"_"+str(timestamp), body = {
            "timestamp":timestamp,
            "uid":uid,
            "domain_followers":domain["field1"],
            "domain_weibo":domain["field3"],
            "domain_verified":domain["field2"],
            "main_domain" : r_domain,
            "has_new_information":1,
            "topic_art":0,
            "topic_computer":0,
            "topic_economic":0,
            "topic_education":0,
            "topic_environment":0,
            "topic_medicine":0,
            "topic_military":0,
            "topic_politics":0,
            "topic_sports":0,
            "topic_traffic":0,
            "topic_life":0,
            "topic_anti_corruption":0,
            "topic_employment":0,
            "topic_violence":0,
            "topic_house":0,
            "topic_law":0,
            "topic_peace":0,
            "topic_religion":0,
            "topic_social_security":0
                    } )
           
    else:
        if es.search(index=USER_DOMAIN_TOPIC, doc_type='text', body= id_body)["hits"]["hits"] != []:
            es.update(index=USER_DOMAIN_TOPIC, doc_type='text', id=str(uid)+"_"+str(timestamp), body = {
            "doc":{
            "domain_followers":"other",
            "domain_weibo":"other",
            "domain_verified":"other",
            "main_domain" : "other",
            "has_new_information":0
                    } })
          
        else:
            es.index(index=USER_DOMAIN_TOPIC, doc_type='text', id=str(uid)+"_"+str(timestamp), body = {
            "timestamp":timestamp,
            "uid":uid,
            "domain_followers":"other",
            "domain_weibo":"other",
            "domain_verified":"other",
            "main_domain" : "other",
            "has_new_information":0,
            "topic_art":0,
            "topic_computer":0,
            "topic_economic":0,
            "topic_education":0,
            "topic_environment":0,
            "topic_medicine":0,
            "topic_military":0,
            "topic_politics":0,
            "topic_sports":0,
            "topic_traffic":0,
            "topic_life":0,
            "topic_anti_corruption":0,
            "topic_employment":0,
            "topic_violence":0,
            "topic_house":0,
            "topic_law":0,
            "topic_peace":0,
            "topic_religion":0,
            "topic_social_security":0
                    } )
            

def get_user_domain(uid,start_date,end_date):
    
    for day in get_datelist_v2(start_date,end_date):
        timestamp = date2ts(day)
        index_list = []
        for i in range(7):
            date = ts2date(date2ts(day) - i*DAY)
            index_list.append('flow_text_%s' % date)

        uid_weibo = get_uid_weibo(uid,index_list)
        domain,r_domain = domain_classfiy(uid,uid_weibo,timestamp)

        save_user_domain(uid,timestamp,domain,r_domain)


if __name__ == '__main__':
    user_domain_run(ES_INDEX_LIST)