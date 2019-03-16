#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import scws
import time
import re

SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1

ABSOLUTE_DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './dict'))
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'black.txt')

cx_dict = ['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@']#关键词词性词典
'''
def load_scws():
    s = scws.scws()
    s.set_charset(SCWS_ENCODING)

    s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

    # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
    s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
    # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
    s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

    s.set_rules(SCWS_RULES)
    s.set_ignore(IGNORE_PUNCTUATION)
    return s
'''
class fenci():
    
    def __init__(self):
        pass
    
    def init_fenci(self):
        scws.scws_new()
        scws.scws_set_charset(SCWS_ENCODING)
        scws.scws_set_xdb(CHS_DICT_PATH)
        scws.scws_add_dict(CHT_DICT_PATH)
        scws.scws_set_rule(SCWS_RULES)
        scws.scws_add_dict(CUSTOM_DICT_PATH)
        scws.scws_add_dict(EXTRA_STOPWORD_PATH)
        scws.scws_add_dict(EXTRA_EMOTIONWORD_PATH)
        scws.scws_set_multi(8)
    
    def get_text_fc(self, text, f=None, cx=False):
        if f:
            ret = [token for token in scws.get_res(text) if (token[2] > 0) and (token[1] in f) and (1 < len(token[0]) < 10 or token[0] in single_word_whitelist)]
        else:
            ret = [token for token in scws.get_res(text) if (token[2] > 0) and (1 < len(token[0]) < 10 or token[0] in single_word_whitelist)]
        if cx:
            return [tk[:2] for tk in ret]
        else:
            return [tk[0] for tk in ret]
        
    def __del__(self):
        scws.scws_free()

def load_emotion_words():
    emotion_words = [line.strip('\r\n') for line in open(EXTRA_EMOTIONWORD_PATH)]
    #print(type(emotion_words[0]))
    return emotion_words


def load_one_words():
    one_words = [line.strip('\r\n') for line in open(EXTRA_ONE_WORD_WHITE_LIST_PATH)]
    return one_words

def load_black_words():
    one_words = [line.strip('\r\n') for line in open(EXTRA_BLACK_LIST_PATH)]
    return one_words

single_word_whitelist = set(load_one_words())
black_word = set(load_black_words())

def cut(s, text, f=None, cx=False):
    if f:
        tks = [token for token
               in s.participle(cut_filter(text))
               if token[1] in f and (3 < len(token[0]) < 30 or token[0] in single_word_whitelist) and token[0] not in black_word]
    else:
        tks = [token for token
               in s.participle(cut_filter(text))
               if token[1] in cx_dict and (3 < len(token[0]) < 30 or token[0] in single_word_whitelist) and token[0] not in black_word]

    if cx:
        return tks
    else:
        return [tk[0] for tk in tks]


def cut_filter(w_text):
    pattern_list = [r'\（分享自 .*\）', r'http://t.cn/\w*']
    for i in pattern_list:
        p = re.compile(i)
        w_text = p.sub('', w_text)
    w_text = re.sub(r'[a-zA-z]','',w_text)
    a1 = re.compile(r'\[.*?\]')
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'回复' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\:')
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\s')
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\w',re.L)
    w_text = a1.sub('',w_text)
    if w_text == '转发微博':
        w_text = ''

    return w_text


STUB_REMOTE_FILE_PER_LINE = "remote ssh %(host)s xapian-progsrv %(db_folder)s\n"
STUB_FILE_PER_LINE = "chert %(db_folder)s\n"



