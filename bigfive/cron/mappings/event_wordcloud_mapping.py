# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "event_wordcloud"

####事件基本信息表 event_information  
index_info = {
    "settings": {
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
                "keywords":{#关键词
                    "properties":{
                        "keyword":{ #群体id
                            "index":"not_analyzed",
                            "type" : "string"
                        },
                        "count":{ #群体id
                            "index":"not_analyzed",
                            "type" : "string"
                        },
                    }
                }
            }
        }
    }
}


exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))