# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_domain_topic"


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
              "timestamp":{ #记录时间
                      "type" : "date",
                      "index" : "not_analyzed"
              },
              "uid":{                             
                  "type":"string",
                  "index":"not_analyzed"
                    
              },
                
              "domain_followers":{    # 粉丝划分领域               
                  "type":"string",
                  "index":"not_analyzed"

                    
              },
                
              "domain_weibo":{    #微博划分领域                     
                  "type":"string",
                  "index":"not_analyzed"

                    
              },
                
              "domain_verified":{    #用户注册信息划分领域                     
                  "type":"string",
                  "index":"not_analyzed"

                    
              },                              
              "main_domain":{ #最可能领域
                  "type":"string",
                  "analyzer":"ik_smart"
                    
              },
              
              'topic_art':{ 
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
              ,'topic_computer':{ 
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
              ,'topic_economic':{ 
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
              ,'topic_education':{ 
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
              ,'topic_environment':{ 
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
              ,'topic_medicine':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
              ,'topic_military':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_politics':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_sports':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_traffic':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_life':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_anti_corruption':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_employment':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_violence':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_house':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_law':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_peace':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_religion':{ #最可能领域
                  "type":"double",
                  "index":"not_analyzed"
                    
              }
            ,'topic_social_security':{ #最可能领域
                  "type":"double",
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