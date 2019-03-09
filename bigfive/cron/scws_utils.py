# -*- coding:UTF-8 -*-
'''
use to set topic, domain, psy model config and utils
write in version:15-12-08
'''
import os
import re
import scws

##对微博文本进行预处理
def cut_filter(text):
    pattern_list = [r'\（分享自 .*\）', r'http://\w*']
    for i in pattern_list:
        p = re.compile(i)
        text = p.sub('', text)
    return text
 
def re_cut(w_text):#根据一些规则把无关内容过滤掉
    w_text = cut_filter(w_text)
    w_text = re.sub(r'[a-zA-z]','',w_text)
    a1 = re.compile(r'\[.*?\]' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'回复' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\:' )
    w_text = a1.sub('',w_text)
    a1 = re.compile(r'\@.*?\s' )
    w_text = a1.sub('',w_text)
    if w_text == u'转发微博':
        w_text = ''

    return w_text


## 加载分词工具

SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1

#ABSOLUTE_DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './dict'))
ABSOLUTE_DICT_PATH = os.path.dirname(os.path.abspath(__file__))
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'scwsfiles/userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'scwsfiles/stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'scwsfiles/emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'scwsfiles/one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'scwsfiles/black.txt')

# cx_dict_test = ['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@']#关键词词性词典

def file(filepath):
    with open(filepath) as f:
        return f.readlines()

def load_one_words():

    one_words = [line.strip('\r\n') for line in file(EXTRA_EMOTIONWORD_PATH)]
    return one_words

def load_black_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)]
    return one_words

single_word_whitelist = set(load_one_words())
single_word_whitelist |= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')

# python2 的一个版本，不建议再使用了  https://github.com/MOON-CLJ/pyscws
# def load_scws():
#     s = scws.Scws()
#     s.set_charset(SCWS_ENCODING)

#     s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
#     s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
#     s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

#     # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
#     s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
#     # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
#     s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

#     s.set_rules(SCWS_RULES)
#     s.set_ignore(IGNORE_PUNCTUATION)
#     return s

# def cut(s, text, f=None, cx=False):
#     if f:
#         tks = [token for token
#                in s.participle(cut_filter(text))
#                if token[1] in f and (3 < len(token[0]) < 30 or token[0] in single_word_whitelist)]
#     else:
#         tks = [token for token
#                in s.participle(cut_filter(text))
#                if 3 < len(token[0]) < 30 or token[0] in single_word_whitelist]
#     if cx:
#         return tks
#     else:
#         return [tk[0] for tk in tks]
# #加载分词工具结束

# for i in cut(load_scws(),"回复 再也没有这种消息更能让我感到高兴的了，牛逼可以我来吹，功劳是你自己的。"):
#     print(i)

###Python3新版本，稍微好一些   https://github.com/xyanyue/python3_scws
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


# fc = fenci()
# fc.init_fenci()
# print(fc.get_text_fc("我都不太明白这是要整个啥,不是我说这个产品,现在咱们讨论的这个啊,包含各种维度的"))

