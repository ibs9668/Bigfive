import sys
sys.path.append('../')
from config import *
from time_utils import *
from cal_main import event_main

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
	res = es.search(index=EVENT_INFORMATION,doc_type='text',body=query_body)['hits']['hits']
	if len(res):
		task = res[0]
		event_id = task['_source']['event_id']
		keywords = task['_source']['keywords']
		start_date = task['_source']['start_date']
		end_date = task['_source']['end_date']
		# es.update(index=EVENT_INFORMATION,doc_type='text',body={'doc':{'progress':1}},id=event_id)   #计算开始，计算状态变为计算中
		event_main(keywords, event_id, start_date, end_date)
		# es.update(index=EVENT_INFORMATION,doc_type='text',body={'doc':{'progress':2}},id=event_id)   #计算结束，计算状态变为计算完成

if __name__ == '__main__':
	main()
	# pass