# -*-coding:utf-8 -*-
from elasticsearch import Elasticsearch

es = Elasticsearch("219.224.134.220:9200")
index_name = "user_information"


###用户基本信息表  user_information
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
            "_id":{
            "path":"uid"
            },
            "properties": {
                 "uid":{ #用户uid
                   "index":"not_analyzed",
                    "type" : "string"
                },
                "username":{#昵称
                    "analyzer":"ik_max_word",
                    "type" : "string"
                },
                "gender":{#性别
                    "index":"not_analyzed",
                    "type" : "long"
                },
               
                "isreal":{#是否认证
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "user_loaction":{#所属地
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "user_birth":{#出生年月
                    "index":"not_analyzed",
                    "type" : "string"
                },
                "fans_num":{#粉丝数
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "weibo_num":{#微博数
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "friends_num":{#关注数
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "create_at":{#用户创建时间
                    "index":"not_analyzed",
                    "type" : "long"
                },
                "description":{#用户描述信息
                    "index":"not_analyzed",
                    "type" : "string"
                },
                 "photo_url":{#头像 URL
                    "index":"not_analyzed",
                    "type" : "string"
                }
            }
        }
    }
}
exist_indice = es.indices.exists(index = index_name)

print(exist_indice)
if not exist_indice:
    print(es.indices.create(index = index_name, body=index_info, ignore = 400))