# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.politics.utils import *

mod = Blueprint('politics',__name__,url_prefix='/politics')

@mod.route('/test')
def test():
    result = 'This is politics!'
    return json.dumps(result,ensure_ascii=False)