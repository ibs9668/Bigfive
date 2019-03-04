# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_domain_topic"


## 用户偏好特征  user_preference
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
              "date":{
              "format": "dateOptionalTime",
              "type": "date"
              },
              "timestamp":{ #记录时间
                      "type" : "long",
                      "index" : "not_analyzed"
              },
              "group_id":{                             
                  "type":"string",
                  "index":"not_analyzed"
                    
              },           
              "domain_static":{ #领域
                  "properties":{
                        "domain_name":{
                            "type":"string",
                            "index":"not_analyzed"
                        },
                        "count":{
                            "type":"long"
                        }
                    }
              },
              "topic_static":{ #话题
                  "properties":{
                        "topic_name":{
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

# es.indices.delete(index = index_name)
exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))
