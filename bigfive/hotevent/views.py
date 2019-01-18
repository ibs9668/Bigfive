# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.hotevent.utils import *

mod = Blueprint('hotevent',__name__,url_prefix='/hotevent')

@mod.route('/test/')
def test():
    result = 'This is hotevent!'
    return json.dumps(result,ensure_ascii=False)