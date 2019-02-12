# Bigfive
大五人格，版权所有，翻版必究。
# Python3+
## elasticsearch数据库 1.7.4 -- 对应elasticsearch包1.9.0
## 请将普通的功能函数放到utils.py中，views.py中只放视图函数
## 写接口需要建数据库链接时，从config.py里导变量，不要在代码里写死
## flask_cache问题解决：
    修改 XXX/site-packages/flask_cache/jinja2ext.py
    from flask.ext.cache import make_template_fragment_key
    为 from flask_cache import make_template_fragment_key
