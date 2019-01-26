# -*- coding: utf-8 -*-
import re

from elasticsearch import Elasticsearch

from bigfive.config import ES_HOST, ES_PORT
es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}])


def judge_uid_or_nickname(keyword):
    return True if re.findall('^\d+$', keyword) else False


def index_to_score_rank(index):
    index_to_score_rank_dict = {
        -1: [0, 101],
        1: [0, 20],
        2: [20, 40],
        3: [40, 60],
        4: [60, 80],
        5: [80, 101],
    }
    return index_to_score_rank_dict[index]

