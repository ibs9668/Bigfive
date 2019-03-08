import sys
sys.path.append('../../')
import os
import time
from scws_utils import load_scws, cut

CUT_BLACK_WORDS = 'usedfiles/black.txt'
EXTRA_BLACK_LIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), CUT_BLACK_WORDS)

s = load_scws()

cx_dict = set(['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@','j']) # 关键词词性词典, 保留名词、动词、形容词
cx_dict_noun = set(['Ng','n','nr','ns','nt','nz']) # 关键词词性词典, 保留名词


def load_black_words():
    one_words = set([line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)])
    return one_words

black_words = load_black_words()

def cut_words(text):
    '''分词, 加入黑名单过滤单个词，保留名词、动词、形容词
       input
           texts: 输入text的list，utf-8
       output:
           terms: 关键词list
    '''
    if not isinstance(text, str):
        raise ValueError("cut words input text must be string")

    cx_terms = cut(s, text, cx=True)

    return [term for term, cx in cx_terms if cx in cx_dict and term not in black_words]


def cut_words_noun(text):
    '''分词, 加入黑名单过滤单个词，保留名词
       input
           texts: 输入text的list，utf-8
       output:
           terms: 关键词list
    '''
    if not isinstance(text, str):
        raise ValueError("cut words input text must be string")

    cx_terms = cut(s, text, cx=True)

    return [term for term, cx in cx_terms if cx in cx_dict_noun and term not in black_words]

