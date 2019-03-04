import requests
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import scan
import time
import os
import json
# es = Elasticsearch(['219.224.134.220:9200'],timeout=1000)
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'

}

def scan_url():
    # query ={
    #     "query": {
    #         "match_all": {}
    #     }
    # }
    # r = scan(es,query,index='user_information',doc_type='text',_source_include=['photo_url,uid'])
    # for item in r:
    #     yield item['_source']
    with open('user_information','r',encoding='utf-8') as fp:
        for line in fp:
            yield json.loads(line)
def download_img(uid,url):
    path = '{}.jpg'.format(uid)
    if os.path.exists(path):
        return
    print(uid)
    r = requests.get(url=url,headers=headers,timeout=10)
    with open(path,'wb') as fp:
        fp.write(r.content)
    time.sleep(2)
if __name__ == '__main__':
    items = scan_url()
    # print(next(items))
    for item in items:
        download_img(item['uid'],item['photo_url'])