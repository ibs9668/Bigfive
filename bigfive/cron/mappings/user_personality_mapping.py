# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_personality"


###用户排名表  user_ranking
index_info = {
    "settings": {
            "analysis": {
                "analyzer": {
                    "my_analyzer": {
                        "type": "pattern",
                        "pattern": "&"   #自定义分析器，用&作为分词的间隔
                    }
                }
            },
            "number_of_replicas": 1,
            "number_of_shards": 3,
        
    },
    "mappings": {
        "text": { #索引类型
            "properties": {
                 "uid":{ #用户uid
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "timestamp":{#时间戳
                    "type" : "long"
                },
                "date":{#日期
                    "format": "dateOptionalTime",
                    "type":"date"
                },
                "machiavellianism_index":{#马基雅维里主义
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "narcissism_index":{#自恋
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "psychopathy_index":{#精神病态
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "extroversion_index":{#外倾性
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "nervousness_index":{#神经质
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "openn_index":{#开放性
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "agreeableness_index":{#宜人性
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "conscientiousness_index":{#尽责性
                    "index":"not_analyzed",
                    "type" : "double"
                },
                "machiavellianism_label":{#马基雅维里主义标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "narcissism_label":{#自恋标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "psychopathy_label":{#精神病态标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "extroversion_label":{#外倾性标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "nervousness_label":{#神经质标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "openn_label":{#开放性标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "agreeableness_label":{#宜人性标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "conscientiousness_label":{#尽责性标签
                    "index":"not_analyzed",
                    "type" : "long"
                },
            }
        }
    }
}

exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))