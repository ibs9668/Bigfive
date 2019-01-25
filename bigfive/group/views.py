# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.politics.utils import *

mod = Blueprint('group',__name__,url_prefix='/group')

@mod.route('/test/')
def test():
    result = 'This is group!'
    return json.dumps(result,ensure_ascii=False)