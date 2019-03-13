# -*- coding: utf-8 -*-

import os
import csv
import time
import sys
import random
from libsvm.python.svmutil import *
sys.path.append('../../')
from scws_utils import fenci
sys.path.append('../../../')
from time_utils import *
from word_cut import word_net
from text_classify import text_net

ABS_PATH = os.path.abspath(os.path.dirname(__file__))

fc = fenci()
fc.init_fenci()

def file(filepath):
    with open(filepath) as f:
        return f.readlines()

def test_data(weibo,flag):
    word_dict = dict()
    with open(ABS_PATH+'/svm/new_feature.csv', 'r') as f:
        reader = csv.reader(f)
        for w,c in reader:
            word_dict[str(w)] = c 

    items = []
    for i in range(0,len(weibo)):
        words = fc.get_text_fc(weibo[i]['content168'])
        row = dict()
        for word in words:
            if str(word[0]) in row:
                row[str(word[0])] = row[str(word[0])] + 1
            else:
                row[str(word[0])] = 1
        items.append(row)


    f_items = []
    for i in range(0,len(items)):
        row = items[i]
        f_row = ''
        f_row = f_row + str(1)
        for k,v in word_dict.items():
            if k in row:
                item = str(word_dict[k])+':'+str(row[k])
                f_row = f_row + ' ' + str(item) 
        f_items.append(f_row)

    with open(ABS_PATH+'/svm_test/test%s.txt' % flag, 'w') as f:
        writer = csv.writer(f)
        for i in range(0,len(f_items)):
            row = []
            row.append(f_items[i])
            writer.writerow((row))
    f.close()
    
def choose_ad(flag):
##    y, x = svm_read_problem('./svm/new_train.txt')
##    m = svm_train(y, x, '-c 4')
##    svm_save_model('./svm/train.model',m)
    m = svm_load_model(ABS_PATH+'/svm/train.model')
    filename = ABS_PATH+'/svm_test/test%s.txt' % flag
    y, x = svm_read_problem(filename)
    p_label, p_acc, p_val  = svm_predict(y, x, m)
    time.sleep(0.5)
    if os.path.isfile(filename):
        os.remove(filename)

    return p_label

def wash_weibo(weibo,label):

    new_list = []
    for i in range(0,len(weibo)):
        weibo[i]['rub_label'] = label[i]
        new_list.append(weibo[i])

    return new_list

def rubbish_classifier(weibo_data):

    flag = str(time.time()) + '_' + str(len(weibo_data))

    test_data(weibo_data,flag)#生成测试数据
    
    label = choose_ad(flag)#广告过滤

    new_list = wash_weibo(weibo_data,label)#清洗结果

    return new_list

#因为cluto聚类的限制所以要对微博进行数量限制，每天随机取相对应限制比例的微博（如有需要可以改成其他取出条件）
def weibo_num_limit(weibo_data, limit_num):
    filter_ratio = limit_num / len(weibo_data)
    weibo_data_dic = {}
    if len(weibo_data) > limit_num:
        for item in weibo_data:
            date = ts2date(item['timestamp'])
            if date in weibo_data_dic:
                weibo_data_dic[date].append(item)
            else:
                weibo_data_dic[date] = [item]

        weibo_data_limit = []
        for date in weibo_data_dic:
            date_data = weibo_data_dic[date]
            index_list = range(len(date_data))
            index_random = random.sample(index_list,int(filter_ratio * len(index_list)))
            weibo_data_limit.extend([date_data[index] for index in index_random])
        print('\t\tWeibo num is limited to %d ...' % len(weibo_data_limit))
        return weibo_data_limit
    else:
        return weibo_data

def opinion_main(weibo_data,k_cluster):
    '''
        观点挖掘主函数：
        输入数据：
        weibo_data：微博列表，[weibo1,weibo2,...]
        k_cluster：子话题个数

        输出数据：
        opinion_name：子话题名称字典，{topic1:name1,topic2:name2,...}
        word_result：子话题关键词对，{topic1:[w1,w2,...],topic2:[w1,w2,...],...}
        text_list：子话题对应的文本，{topic1:[text1,text2,...],topic2:[text1,text2,..],..}
    '''
    print('\t\tGetting keywords...')
    limit_num = 30000
    weibo_data = weibo_num_limit(weibo_data, limit_num)
    word_result,word_weight,word_main = word_net(weibo_data,k_cluster)#提取关键词对
    print('\t\tGetting present text...')
    text_list,opinion_name = text_net(word_result,word_weight,weibo_data)#提取代表文本,会保证每个聚类里面的微博数量是相等的

    return opinion_name,word_result,text_list,word_main

if __name__ == '__main__':
    main('0521',5)#生成训练集
