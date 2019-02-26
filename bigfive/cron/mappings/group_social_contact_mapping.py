# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_social_contact"


#群体社交特征表 group_social_contact
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
            "_id":{
                "path":"uid"
            },
            "properties": {
                "group_id":{ #用户uid
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "group_name":{#昵称
                    "analyzer":"ik_max_word",
                    "type" : "string"
                },
                "map_type":{#网络关系类型
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "node": { #节点
                    "index":"not_analyzed",
                    "type": "string"
                },
                "link": { #边
                    "properties": {
                        "source": { #源节点
                            "index":"not_analyzed",
                            "type": "string"
                        },
                        "target": { #目的节点
                            "index":"not_analyzed",
                            "type": "string"
                        }
                    }
                },

            }
        }
    }
}


exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))