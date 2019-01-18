# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.firstpage.utils import *

mod = Blueprint('firstpage',__name__,url_prefix='/firstpage')

@mod.route('/test/')
def test():
    result = 'This is firstpage!'
    return json.dumps(result,ensure_ascii=False)