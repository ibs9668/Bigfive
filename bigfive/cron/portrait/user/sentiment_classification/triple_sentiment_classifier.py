# -*- coding: utf-8 -*-

import re
import os
import time
import csv
import sys
from gensim import corpora
sys.path.append('../../../')
from sentiment_classification.utils import *
from sentiment_classification.flow_psy import flow_psychology_classfiy
from scws_utils import fc


AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


emotions_words = load_emotion_words()
emotions_words = [e for e in emotions_words]
t_emotions_words = emotions_words
emotions_words.extend(t_emotions_words)
emotions_words = [w for w in emotions_words]
emotions_words_set = set(emotions_words)
emotion_pattern = re.compile(r'\[(\S+?)\]')


def if_emoticoned_weibo(r):
    # 微博是否包含指定的表情符号集
    emotions = re.findall(emotion_pattern, r['text'])
    is_emoticoned = 1 if set(emotions) & emotions_words_set else 0
    return is_emoticoned

'''define 2 kinds of seed emoticons'''
positive_set = set()
negative_set = set()

with open(os.path.join(AB_PATH, '4groups.csv')) as f:
    for l in f:
        pair = l.rstrip().split('\t')
        if pair[1] == '1' or pair[1] == '4':
            positive_set.add(pair[0])

        if pair[1] == '2' or pair[1] == '3':
            negative_set.add(pair[0])

POSITIVE = 1
NEGATIVE = -1
MIDDLE = 0

def emoticon(text):
    """ Extract emoticons and define the overall sentiment """

    remotions = re.findall(emotion_pattern, text)
    positive = 0
    negative = 0

    for e in remotions:

        if e in positive_set:
            positive = positive + 1
        elif e in negative_set:
            negative = negative + 1
        else:
            pass

    if positive > negative:
        return POSITIVE
    elif positive < negative:
        return NEGATIVE
    else:
        return MIDDLE


'''define subjective dictionary and subjective words weight'''
dictionary_1 = corpora.Dictionary.load(os.path.join(AB_PATH, 'triple_subjective_1.dict'))
step1_score = {}
with open(os.path.join(AB_PATH, 'triple_subjective_1.txt')) as f:
    for l in f:
        lis = l.rstrip().split()
        step1_score[int(lis[0])] = [float(lis[1]), float(lis[2])]

'''define polarity dictionary and polarity words weight'''
dictionary_2 = corpora.Dictionary.load(os.path.join(AB_PATH, 'binary_polarity.dict'))
step2_score = {}
with open(os.path.join(AB_PATH, 'binary_weight.txt')) as f:
    for l in f:
        lis = l.rstrip().split()
        step2_score[int(lis[0])] = [float(lis[1]), float(lis[2])]


def triple_classifier(tweet):
    '''
    输出结果：
    0 中性
    1 积极
    2 生气
    3 焦虑
    4 悲伤
    5 厌恶
    6 消极其他
    '''
    sentiment = MIDDLE
    
    text = tweet['text']
    keywords_list = []

    emoticon_sentiment = emoticon(text)
    if emoticon_sentiment != MIDDLE:
        entries = cut(fc, text)
        entry = [e for e in entries]
        keywords_list = entries
        if emoticon_sentiment == POSITIVE:
            sentiment = emoticon_sentiment
            text = u''
        else:
            sentiment = flow_psychology_classfiy(text)
            if sentiment == 0:
                sentiment = 6
            text = u''
    
    if text != u'':
        entries = fc.get_text_fc(text)
        entry = [e for e in entries]
        keywords_list = entry
        
        
        bow = dictionary_1.doc2bow(entry)
        s = [1, 1]
        for pair in bow:
            s[0] = s[0] * (step1_score[pair[0]][0] ** pair[1])
            s[1] = s[1] * (step1_score[pair[0]][1] ** pair[1])
        if s[0] < s[1]:
            bow = dictionary_2.doc2bow(entry)
            s2 = [1, 1]
            for pair in bow:
                s2[0] = s2[0] * (step2_score[pair[0]][0] ** pair[1])
                s2[1] = s2[1] * (step2_score[pair[0]][1] ** pair[1])
            if s2[0] > s2[1]:
                sentiment = POSITIVE
            elif s2[0] == s2[1]:
                sentiment = MIDDLE
            else:
                sentiment = flow_psychology_classfiy(text)
                if sentiment == 0:
                    sentiment = 6
        else:
            sentiment = MIDDLE        

    return sentiment


if __name__ == '__main__':
    tweet = {'text':'村霸存心不良，挖空心思贿选霸政权之祸国殃民！ 举报广州白云区人和镇明星村，某些道貌岸然的村霸干部！'}
    domain = triple_classifier(tweet)
    print(domain)

