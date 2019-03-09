# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "event_personality"
index_info={
        "settings": {
          "index": {
            "number_of_shards":3,
            "number_of_replicas":1,
            "analysis": {
              "analyzer": {
                "my_analyzer": {
                  "type": "pattern",
                  "pattern": "&"
                    }
                  }
                }
              }
            },
        "mappings": {
          "text": {
            "properties": {


              "event_id": {
                "index": "not_analyzed",
                "type": "string"
              },

              "extroversion_high":{
                "index": "not_analyzed",
                "type": "object"
              },
              "agreeableness_high": {
                "index": "not_analyzed",
                "type": "object"
              },
              "conscientiousness_high":{
                "index": "not_analyzed",
                "type": "object"
              },
              "nervousness_high":{
                "index": "not_analyzed",
                "type": "object"
              },
              "openn_high": {
                "index": "not_analyzed",
                "type": "object"
              },
              "machiavellianism_high": {
                "index": "not_analyzed",
                "type": "object"
              },
              "narcissism_high":{
                "index": "not_analyzed",
                "type": "object"
              },
              "psychopathy_high": {
                "index": "not_analyzed",
                "type": "object"
              },

               "extroversion_low":{
                "index": "not_analyzed",
                "type": "object"
              },
              "agreeableness_low": {
                "index": "not_analyzed",
                "type": "object"
              },
              "conscientiousness_low":{
                "index": "not_analyzed",
                "type": "object"
              },
              "nervousness_low":{
                "index": "not_analyzed",
                "type": "object"
              },
              "openn_low": {
                "index": "not_analyzed",
                "type": "object"
              },
              "machiavellianism_low": {
                "index": "not_analyzed",
                "type": "object"
              },
              "narcissism_low":{
                "index": "not_analyzed",
                "type": "object"
              },
              "psychopathy_low": {
                "index": "not_analyzed",
                "type": "object"
              },

              "timestamp": {
                "index": "not_analyzed",
                "type": "long"
              },
              "date":{
                "format": "dateOptionalTime",
                "type": "date"
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


# key= group_id+timestamp
