# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_information"

####群体基本信息表 group_information  
index_info = {
    "settings": {
            "analysis": {
                "analyzer": {
                    "caseSensitive": {
                        "type": "custom",
                        "filter": "lowercase",
                        "tokenizer": "keyword"
                    }
                }
            },
            "number_of_replicas": 1,
            "number_of_shards": 3,
        
    },
    "mappings": {
        "text": { #索引类型
            "properties": {
                "group_id":{ #群体id
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "group_name":{#群体名称
                    "analyzer":"caseSensitive",
                    "type" : "string"
                },
                "group_pinyin":{#群体名称拼音
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
                "remark":{#备注
                    "analyzer":"caseSensitive",
                    "type" : "string"
                },
                "userlist":{#用户列表
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "keywords":{#关键词
                    "type" : "string"
                },
                "create_condition":{   #创建条件
                    "properties":{
                        "machiavellianism_index":{
                            "type" : "long"
                        },
                        "narcissism_index":{
                            "type" : "long"
                        },
                        "psychopathy_index":{
                            "type" : "long"
                        },
                        "extroversion_index":{
                            "type" : "long"
                        },
                        "nervousness_index":{
                            "type" : "long"
                        },
                        "openn_index":{
                            "type" : "long"
                        },
                        "agreeableness_index":{
                            "type" : "long"
                        },
                        "conscientiousness_index":{
                            "type" : "long"
                        },
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