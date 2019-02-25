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
                    "type":"pattern",
                    "patern":"&"
                }
            }
        }
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
                
                "ip":{  #IP地址                         
                    "type":"ip",
                    "index":"not_analyzed"
                    
                },                              
                "location":{#地点
                    "type":"string",
                    "analyzer": "my_analyzer"
                    
                },
                "sensitive_ip":{#敏感IP
                    "type":"ip",
                    "index":"not_analyzed"
                    
                },
                "sensitive_location":{ #敏感地址
                    "type":"string",
                    "analyzer": "my_analyzer"
                    
                }
                
            }
        }
    }
}




exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))