#-*- encoding:utf-8 -*-
import json
import re
from textrank4zh import TextRank4Keyword, TextRank4Sentence

# key_words
def text_rank(text, keywords_num):
    keywords = []
    tr4w = TextRank4Keyword()
    tr4w.analyze(text=text.encode('utf-8', 'ignore'), lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
    for item in tr4w.get_keywords(keywords_num, word_min_len= 1):
        keywords.append(item.word)

    # keywords = ','.join(keywords)
    # return json.dumps(keywords, ensure_ascii=False)
    return keywords


# micro_words
def micro_words(text):
    if isinstance(text, str):
        RE = re.compile(u'#([a-zA-Z-_⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+)#', re.UNICODE)
        # hashtag = '&'.join(RE.findall(text))
        hashtag = RE.findall(text)

    return hashtag


# sensitive_words
def createWordTree():
    wordTree = [None for x in range(256)]
    wordTree.append(0)
    nodeTree = [wordTree, 0]
    awords = []

    for b in open('sensitive_words.txt', 'r'):
        awords.append(b.strip().split('\t')[0].encode('utf-8', 'ignore'))

    for word in awords:
        temp = wordTree
        for a in range(0,len(word)):
            # index = ord(word[a])
            index = word[a]

            if a < (len(word) - 1):
                if temp[index] == None:
                    node = [[None for x in range(256)],0]
                    temp[index] = node
                elif temp[index] == 1:
                    node = [[None for x in range(256)],1]
                    temp[index] = node
                
                temp = temp[index][0]
            else:
                temp[index] = 1

    return nodeTree 


def searchWord(str, nodeTree):
    temp = nodeTree
    words = []
    word = []
    a = 0
    while a < len(str):
        # index = ord(str[a])
        index = str[a]
        temp = temp[0][index]
        if temp == None:
            temp = nodeTree
            a = a - len(word)
            word = []
        elif temp == 1 or temp[1] == 1:
            word.append(index)
            words.append(word)
            a = a - len(word) + 1 
            word = []
            temp = nodeTree
        else:
            word.append(index)
        a = a + 1

    map_words = {}
    for w in words:
        iter_word = b"".join([chr(x).encode('latin1') for x in w]).decode('utf-8')
        if not map_words.__contains__(iter_word):
            map_words[iter_word] = 1
        else:
            map_words[iter_word] = map_words[iter_word] + 1
    
    return map_words


def cal_sensitive(text):

    node = createWordTree()
    sensitive_words_dict = searchWord(text.encode('utf-8', 'ignore'), node)

    sensitive_score_dict = { "1": 1,"2": 5,"3": 10}
    sensitive_words_weight = dict()
    for b in open('sensitive_words.txt', 'r'):
        word = b.strip().split('\t')[0]
        weight =  b.strip().split('\t')[1]
        sensitive_words_weight[word] =  weight

    item = dict()
    if sensitive_words_dict:
        item['sensitive_words_string'] = "&".join(sensitive_words_dict.keys())
        item['sensitive_words_dict'] = sensitive_words_dict
    else:
        item['sensitive_words_string'] = ""
        item['sensitive_words_dict'] = {}

    score = 0
    if sensitive_words_dict:
        for k,v in sensitive_words_dict.items():
            tmp_stage = sensitive_words_weight.get(k, 0)
            if tmp_stage:
                score += v*sensitive_score_dict[str(tmp_stage)]

    return score, item


if __name__ == '__main__':

    text = "这间酒店位于北京东三环，里面摆放很多雕塑，文艺气息十足。答谢宴于晚上8点开始。"
    keywords=text_rank(text,5)
    print(keywords)

    text = "#新年快乐#狗年大吉"
    hastag = micro_words(text)
    print(hastag)


    text = '屠杀暴政宝宝wink做的越来越好了[酷]'
    score, item= cal_sensitive(text)
    print(score, item)
    print(item['sensitive_words_string'])

    
