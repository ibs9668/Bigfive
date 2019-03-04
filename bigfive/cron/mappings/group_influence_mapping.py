# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_influence"


###群体影响力特征表  group_influence 
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
              "timestamp":{ #记录时间
                      "type" : "long",
                      "index" : "not_analyzed"
              },
              "group_id":{ #群体id                            
                  "type":"string",
                  "index":"not_analyzed"
                    
              },
                
              "activity":{  #活跃度                          
                  "type":"double"
                    
              },                              
              "sensitivity":{ #敏感度
                  "type":"double"
                    
              },
              "influence":{#影响力
                  "type":"double"
                    
              }
              ,
              "warning":{#是否达到预警值
                  "type":"boolean"
                    
              }
                
          }
      }
  }
}


exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))