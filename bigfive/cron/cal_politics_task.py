import sys
sys.path.append('../')
from config import *
from time_utils import *
from cal_main import politics_main

def main():
	query_body = {
		'query':{
			'term':{
				'progress':0
			}
		},
		'sort':{
			'create_time':{
				'order':'asc'
			}
		}
	}
	res = es.search(index=POLITICS_INFORMATION,doc_type='text',body=query_body)['hits']['hits']
	if len(res):
		task = res[0]
		task_id = task['_id']
		politics_id = task['_source']['politics_id']
		keywords = task['_source']['keywords']
		start_date = task['_source']['start_date']
		end_date = task['_source']['end_date']
		# es.update(index=POLITICS_INFORMATION,doc_type='text',id=task_id,body={'doc':{'progress':1}})
		politics_main(keywords, politics_id, start_date, end_date)
		# es.update(index=POLITICS_INFORMATION,doc_type='text',id=task_id,body={'doc':{'progress':2}})

if __name__ == '__main__':
	main()