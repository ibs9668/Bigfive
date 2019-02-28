import random

def model_cal(uid):
	machiavellianism_index = int(random.random() * 100)
	narcissism_index = int(random.random() * 100)
	psychopathy_index = int(random.random() * 100)
	extroversion_index = int(random.random() * 100)
	nervousness_index = int(random.random() * 100)
	openn_index = int(random.random() * 100)
	agreeableness_index = int(random.random() * 100)
	conscientiousness_index = int(random.random() * 100)
	return machiavellianism_index,narcissism_index,psychopathy_index,extroversion_index,nervousness_index,openn_index,agreeableness_index,conscientiousness_index

def cal_person(uid):
	machiavellianism_index,narcissism_index,psychopathy_index,extroversion_index,nervousness_index,openn_index,agreeableness_index,conscientiousness_index = model_cal(uid)
	return machiavellianism_index,narcissism_index,psychopathy_index,extroversion_index,nervousness_index,openn_index,agreeableness_index,conscientiousness_index

if __name__ == '__main__':
	cal_main()