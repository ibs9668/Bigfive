# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "event_message_type"
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
              "message_type": {
                "index": "not_analyzed",
                "type": "long"
              },
              "message_count": {
                "index": "not_analyzed",
                "type": "long"
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