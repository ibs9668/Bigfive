# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_personality"


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
                
              "extroversion_index":{#外倾性                         
                  "type":"double"
              },                              
              "agreeableness_index":{#宜人性
                  "type":"double"
              },
              "conscientiousness_index":{#尽责性
                  "type":"double"
              },
              "nervousness_index":{#神经质
                  "type":"double"
              },
              "openn_index":{#开放性
                  "type":"double"
              },
              "machiavellianism_index":{#马基雅维利主义
                  "type":"double"
              },
              "narcissism_index":{#自恋
                  "type":"double"
              },
              "psychopathy_index":{#精神病态
                  "type":"double"
              },
          }
      }
  }
}

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))