# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_activity"
index_info={
        "settings": {
          "number_of_shards":3,
          "number_of_replicas":1
        },
        "mappings": {
          "text": {
            "properties": {
              "activity_direction": {
                "properties": {
                  "count": {
                    "type": "long"
                  },
                  "geo2geo": {
                    "index": "not_analyzed",
                    "type": "string"
                  }
                }
              },
              "group_id": {
                "index": "not_analyzed",
                "type": "string"
              },
              "main_end_geo": {
                "properties": {
                  "count": {
                    "type": "long"
                  },
                  "main_end_geo": {
                    "index": "not_analyzed",
                    "type": "string"
                  }
                }
              },
              "main_start_geo": {
                "properties": {
                  "count": {
                    "type": "long"
                  },
                  "main_start_geo": {
                    "index": "not_analyzed",
                    "type": "string"
                  }
                }
              },
              "timestamp": {
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

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))