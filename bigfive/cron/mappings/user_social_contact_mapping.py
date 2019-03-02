# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_social_contact"


###用户社交特征表  user_social_contact
index_info = {
    "settings": {
            "analysis": {
                "analyzer": {
                    "my_analyzer": {
                        "type": "pattern",
                        "pattern": "&"   #自定义分析器，用&作为分词的间隔
                    }
                }
            },
            "number_of_replicas": 1,
            "number_of_shards": 3,
        
    },
    "mappings": {
        "text": { #索引类型
            "properties": {
                "target_name":{ #目标用户名
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "message_type":{#昵称
                    "type" : "long"
                },
                "source":{#网络关系类型
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "source_name":{#网络关系类型
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "target":{#网络关系类型
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "timestamp":{#网络关系类型
                    "type" : "long"
                }
            }
        }
    }
}

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))