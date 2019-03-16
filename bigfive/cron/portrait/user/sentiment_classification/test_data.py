#-*-coding=utf-8-*-
#vision2
import os
import re
import sys
import json
import csv
import time
import heapq
import datetime
from triple_sentiment_classifier import triple_classifier
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from word_textrank import get_keyword,get_keywords_jieba
##from global_utils_ch import abs_path
##from config import load_scws

tr4w = TextRank4Keyword()

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
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]

def input_data():#测试输入

    keyword_dict = dict()
    reader = csv.reader(file('./weibo_data/uid_text_0728.csv', 'rb'))
    start = time.time()
    text_dict = dict()
    text_list = dict()
    mid_list = []
    count = 0
    for mid,text in reader:
        count = count + 1        
        #s, keywords_list = triple_classifier({'text':text})
        #key_dict = get_keyword({'text':text},tr4w)
        key_dict = get_keywords_jieba({'text':text})
        text_dict[mid] = key_dict
        #text_list[mid] = keywords_list
        mid_list.append([mid,text])
        
    end = time.time()
    print 'it takes %s seconds...' % (end-start)
    print count

    with open('./weibo_data/weibo_key_jieba.csv', 'wb') as f:
        writer = csv.writer(f)
        for mid,text in mid_list:
            row_str = ''
            i = 0
            for k in text_dict[mid].keys():
                
                if i == 0:
                    row_str = row_str + str(k)
                    i = 1
                else:
                    row_str = row_str + '&' + str(k)
            writer.writerow((mid,row_str))

    f.close()    
     
##        for k in keywords_list:
##            if keyword_dict.has_key(k):
##                keyword_dict[k] = keyword_dict[k] + 1
##            else:
##                keyword_dict[k] = 1
##
##    n = len(keyword_dict)
##    keyword = TopkHeap(n)
##    count = 0
##    for k,v in keyword_dict.items():
##        keyword.Push((v,k))
##        count = count + v
##
##    keyword_data = keyword.TopK()    
##    
##    with open('./weibo_data/weibo_keyword.csv', 'wb') as f:
##        writer = csv.writer(f)
##        for i in range(0,len(keyword_data)):
##            writer.writerow((keyword_data[i][1].encode('utf-8'),keyword_data[i][0],float(keyword_data[i][0])/float(count)))
##
##    f.close()

if __name__ == '__main__':
    uid_list = input_data()
            
    
