# -*-coding:utf-8 -*-
import sys
sys.path.append('../../')
from config import *

#创建事件的mapping
def create_event_mapping(index_name):
    index_info = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "my_analyzer":{
                      "tokenizer":"my_tokenizer"
                    }
                },
                "tokenizer":{
                    "my_tokenizer":{
                        "type": "pattern",
                        "pattern":"&"
                    }
                }
            },
            "number_of_replicas": 1,
            "number_of_shards": 3,
        },
        "mappings": {
            "text": {
                "properties": {
                    "root_uid": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "sentiment": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "ip": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "user_fansnum": {
                        "type": "long"
                    },
                    "mid": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "message_type": {
                        "type": "long"
                    },
                    "geo": {
                        "analyzer": "my_analyzer",
                        "type": "string"
                    },
                    "uid": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "root_mid": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "keywords_string": {
                        "type": "string"
                    },
                    "text": {
                        "index": "not_analyzed",
                        "type": "string"
                    },
                    "timestamp": {
                        "type": "long"
                    },
                    "comment": {
                        "type": "long"
                    },
                    "retweeted": {
                        "type": "long"
                    },
                }
            }
        }
    }


    exist_indice = es.indices.exists(index = index_name)

    if not exist_indice:
        es.indices.create(index = index_name, body=index_info, ignore = 400)
        print('事件mapping创建成功...')
    else:
        raise('事件已经存在，请检查...')