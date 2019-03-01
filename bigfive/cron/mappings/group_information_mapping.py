# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_information"

####群体基本信息表 group_information  
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
            "path":"group_id"
            },
            "properties": {
                 "group_id":{ #群体id
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "group_name":{#昵称
                    "analyzer":"ik_max_word",
                    "type" : "string"
                },
                "create_time":{#创建时间
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "create_condition":{#创建条件
                    "index":"not_analyzed",
                    "type" : "object"
                },
                "remark":{#备注
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "state":{#进度
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "user_lst":{#用户列表
                    "index":"not_analyzed",
                    "type" : "array"
                },
                 ,
                "group_pinyin": {#拼音
                    "index":"not_analyzed",
                    "type" : "string"
                }
            }
        }
    }
}

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))

# 插入数据
# es.index(index=index_name,doc_type="text",
#     body={
    
#             })