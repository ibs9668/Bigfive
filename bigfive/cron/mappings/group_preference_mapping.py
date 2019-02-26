# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_preference"


###群体偏好特征表   group_preference 
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
              "timestamp":{  #统计时间
                      "type" : "date",
                      "index" : "not_analyzed"
              },
              "group_id":{    # 群体id                        
                  "type":"string",
                  "index":"not_analyzed"
                    
              },
                
              "domain":{  #领域分布                        
                  "type":"object",
                  "index":"not_analyzed"
                    
              },                              
              "topic":{ #话题分布
                  "type":"object",
                  "index":"not_analyzed"
                    
              }
              ,
              "key_words":{ #关键词
                  "type":"object",
                  "index":"not_analyzed"
                    
              },
              "sensitive_words":{ #敏感词
                  "type":"object",
                  "index":"not_analyzed"
                    
              }
              ,
              "micro_words":{ #微话题
                  "type":"object",
                  "index":"not_analyzed"
                    
              }
                
          }
      }
  }
}

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))