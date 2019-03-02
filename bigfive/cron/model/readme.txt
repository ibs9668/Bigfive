微博项目人格预测模型使用说明

调用 personality_predict.py  中的 predict_personality(weibo_text_filepath, weibo_profile_filepath) 函数即可预测人格得分

输出：该函数返回一个 N*9 维列表，N 表示用户数，一共9列属性，第一列为用户 ID，第2-9列分别是8个人格维度上的得分
     得分列表以 numpy 中的 npy 格式 和 excel 格式 保存在 result 文件夹中

输入：weibo_text.json 和 weibo_profile.json文件
weibo_text.json 文件中是用户的微博文本数据，必须包括”uid“，”text“关键字段
weibo_profile.json 文件中是用户的基本信息，必须包括“uid”，”follow_count“，”follower_count“,"statuses_count"字段，分别表示用户ID，关注数，粉丝数，所发微博总数
test_data 文件夹中有两个示例数据可供参考

Model 文件中是训练好的回归模型