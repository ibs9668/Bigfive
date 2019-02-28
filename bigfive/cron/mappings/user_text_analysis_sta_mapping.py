# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_text_analysis_sta"


#用户活动特征  user_activity
index_info = {
    "settings": {
        "number_of_shards": 3,  
        "number_of_replicas":1
    },
    "mappings":{
        "text":{
            "properties":{
                "timestamp":{#记录时间
                    "type" : "date",
                    "index" : "not_analyzed"
                },
                "uid":{                             
                    "type":"string",
                    "index":"not_analyzed"
                },
                
                "keywords":{  #关键词
                    "properties":{
                        "keyword":{
                            "type":"string",
                            "index":"not_analyzed"
                        },
                        "count":{
                            "type":"long"
                        }
                    }
                },
                "hastags":{  #微话题
                    "properties":{
                        "hastag":{
                            "type":"string",
                            "index":"not_analyzed"
                        },
                        "count":{
                            "type":"long"
                        }
                    }
                }, 
                "sensitive_words":{  #敏感词
                    "properties":{
                        "sensitive_word":{
                            "type":"string",
                            "index":"not_analyzed"
                        },
                        "count":{
                            "type":"long"
                        }
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