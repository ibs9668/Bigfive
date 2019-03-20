import sys
sys.path.append('../')
from config import *
from time_utils import *
from cal_main import group_main

def main():
	query_body = {
		'query':{
			'term':{
				'progress':0   #未计算
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
		task_id = task['_id']
		args_dict = task['_source']['create_condition']
		keyword = task['_source']['keyword']
		remark = task['_source']['remark']
		group_name = task['_source']['group_name']
		create_time = task['_source']['create_time']
		create_time = 1480176000
		es.update(index=GROUP_TASK,doc_type='text',id=task_id,body={'doc':{'progress':1}})   #计算中
		cal_status = group_main(args_dict,keyword,remark,group_name,create_time)
		if cal_status:
			es.update(index=GROUP_TASK,doc_type='text',id=task_id,body={'doc':{'progress':2}})   #计算完成
		else:
			print("计算失败，没有满足条件的用户。。。")
			es.update(index=GROUP_TASK,doc_type='text',id=task_id,body={'doc':{'progress':3}})   #计算失败

if __name__ == '__main__':
	main()