from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import random
import json
es = Elasticsearch(['219.224.134.220:9200'], timeout=1000)
mapping ={
    "settings": {
        "index": {
            "analysis": {
                "analyzer": {
                    "my_analyzer": {
                        "type": "pattern",
                        "pattern": "&"
                    },
                    "caseSensitive": {
                        "type": "custom",
                        "filter": "lowercase",
                        "tokenizer": "keyword"
                    }
                }
            },
            "number_of_shards": "3",
            "number_of_replicas": "1"
        }
    },
    "mappings": {
        "text": {
            "properties": {
                "create_time": {
                    "type": "long"
                },
                "create_date": {
                    "format": "dateOptionalTime",
                    "type": "date"
                },
                "remark": {
                    "analyzer": "caseSensitive",
                    "type": "string"
                },
                "group_id": {
                    "index": "not_analyzed",
                    "type": "string"
                },
                "group_name": {
                    "analyzer": "caseSensitive",
                    "type": "string"
                },
                "group_pinyin": {
                    "type": "string"
                },
                "progress": {
                    "type": "long"
                },
                "keyword": {
                    "analyzer": "caseSensitive",
                    "type": "string"
                },
                "create_condition": {
                    "properties": {
                        "sensitive_index": {
                            "type": "long"
                        },
                        "openn_index": {
                            "type": "long"
                        },
                        "psychopathy_index": {
                            "type": "long"
                        },
                        "agreeableness_index": {
                            "type": "long"
                        },
                        "nervousness_index": {
                            "type": "long"
                        },
                        "liveness_index": {
                            "type": "long"
                        },
                        "machiavellianism_index": {
                            "type": "long"
                        },
                        "importance_index": {
                            "type": "long"
                        },
                        "compactness_index": {
                            "type": "long"
                        },
                        "extroversion_index": {
                            "type": "long"
                        },
                        "conscientiousness_index": {
                            "type": "long"
                        },
                        "narcissism_index": {
                            "type": "long"
                        }
                    }
                }
            }
        }
    }
}

es.indices.create(index='group_task',body=mapping)