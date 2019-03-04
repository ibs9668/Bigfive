# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_emotion"


###用户情绪特征表  user_emotion
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
                  "date":{
                      "format": "dateOptionalTime",
                      "type":"date"
                  },
                  "uid":{                             
                      "type":"string",
                      "index":"not_analyzed"
                        
                  },
                    
                  "nuetral":{  #中性                           
                      "type":"long"
                        
                  },                              
                  "positive":{#积极
                      "type":"long"
                        
                  },
                  "negtive":{#消极
                      "type":"long"
                        
                  }
                    
              }
          }
      }
  }


exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))