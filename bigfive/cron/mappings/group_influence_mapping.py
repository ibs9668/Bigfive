# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_influence"


###用户影响力   user_influence
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
                      "type" : "long"
              },
              "date":{#记录日期
                      "format": "dateOptionalTime",
                      "type" : "date"
              },
              "group_id":{                             
                  "type":"string",
                  "index":"not_analyzed"
              },
                
              "activity":{#活跃度                         
                  "type":"double"
              },                              
              "sensitivity":{#敏感度
                  "type":"double"
              },
              "influence":{#影响力
                  "type":"double"
              },
              "importance":{#重要度
                  "type":"double"
              },
              "density":{#紧密度
                  "type":"double"
              },
              "activeness_star":{#活跃度星级
                  "type":"long"
              },                              
              "influence_star":{#敏感度星级
                  "type":"long"
              },
              "importance_star":{#影响力星级
                  "type":"long"
              },
              "sensitivity_star":{#重要度星级
                  "type":"long"
              },
              "density_star":{#紧密度星级
                  "type":"long"
              },
          }
      }
  }
}

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))