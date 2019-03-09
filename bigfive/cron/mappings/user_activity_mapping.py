# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_activity"


#用户活动特征  user_activity
index_info = {
    "settings": {
        "number_of_shards": 3,  
        "number_of_replicas":1, 
        "analysis":{ 
            "analyzer":{
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
        }
    },

    "mappings":{
        "text":{
            "properties":{
                "timestamp":{#记录时间
                        "type" : "long",
                        "index" : "not_analyzed"
                },
                "uid":{                             
                    "type":"string",
                    "index":"not_analyzed"
                },
                "ip":{  #ip                         
                    "type":"ip",
                    "index":"not_analyzed"
                },                              
                "geo":{#地理位置
                    "type":"string",
                    "analyzer": "my_analyzer"
                },
                "count":{#统计次数
                    "type":"long",
                    "index":"not_analyzed"
                }
            }
        }
    }
}



# es.indices.delete(index = index_name)
exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))