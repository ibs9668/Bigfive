# Bigfive
大五人格，版权所有，翻版必究。
## flask_cache问题解决：
    修改 XXX/site-packages/flask_cache/jinja2ext.py
    from flask.ext.cache import make_template_fragment_key
    为 from flask_cache import make_template_fragment_key