import sys
sys.path.append('../../')

from config import *
from time_utils import *
from global_utils import *

#计算词云的分布字典
#输入：["中国&美国","好人&坏人&男人",...]
#输出：{"中国":5,"好人":3,...}
def word_cloud(keywords_list):
	result = {}
	for keywords_string in keywords_list:
		keyword_list = keywords_string.split('&')
		for keyword in keyword_list:
			try:
				result[keyword] += 1
			except:
				result[keyword] = 1
	return result
