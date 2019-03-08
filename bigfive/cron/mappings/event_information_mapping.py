# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "event_information"

####事件基本信息表 event_information  
index_info = {
    "settings": {
        "analysis": {
            "analyzer": {
                "caseSensitive": {
                    "type": "custom",
                    "filter": "lowercase",
                    "tokenizer": "keyword"
                },
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
        "text": { #索引类型
            "properties": {
                "event_id":{ #群体id
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "event_name":{#群体名称
                    "analyzer":"caseSensitive",
                    "type" : "string"
                },
                "event_pinyin":{#群体名称拼音
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "create_time":{#创建时间
                    "type" : "long"
                },
                "create_date":{   #创建日期
                    "format": "dateOptionalTime",
                    "type": "date"
                },
                "userlist":{#用户列表
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "userlist_important":{#重要用户列表（网络PageRank排名靠前）
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "keywords":{#关键词
                    "analyzer": "my_analyzer",
                    "type" : "string"
                },
                "progress":{#计算状态
                    "type" : "long"
                },
            }
        }
    }
}


exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))