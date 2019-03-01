import sys
sys.path.append('../')
from config import *
from time_utils import *
from cal_task import group_create

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
	res = es.search(index=GROUP_TASK,doc_type='text',body=query_body)['hits']['hits']
	if len(res):
		task = res[0]
		args_dict = task['_source']['create_condition']
		keyword = task['_source']['keyword']
		remark = task['_source']['remark']
		group_name = task['_source']['group_name']
		create_time = task['_source']['create_time']
		group_create(args_dict,keyword,remark,group_name,create_time)

if __name__ == '__main__':
	main()