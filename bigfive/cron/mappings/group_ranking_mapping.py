# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "group_ranking"


###群体排名表 group_ranking
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
                 "group_id":{ #群体id
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "group_name":{#群体名称
                    "analyzer":"ik_max_word",
                    "type" : "string"
                },
                "influence_index":{#影响力指数
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "machiavellianism_index":{#马基雅维里主义
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "narcissism_index":{#自恋
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "psychopathy_index":{#精神病态
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "extroversion_index":{#外倾性
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "nervousness_index":{#神经质
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "openn_index":{#开放性
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "agreeableness_index":{#宜人性
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "conscientiousness_index":{#尽责性
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "compactness_index":{#紧密度
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "liveness_index":{#活跃度
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "importance_index":{#重要度
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "sensitive_index":{#敏感度
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "liveness_star":{#活跃度星级
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "importance_star":{#重要度星级
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "sensitive_star":{#敏感度星级
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "influence_star":{#影响力星级
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "compactness_star":{#紧密度星级
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