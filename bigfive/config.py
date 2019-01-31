# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch

ES_HOST = '219.224.134.214'
ES_PORT = 9200

es = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}], timeout=1000)
