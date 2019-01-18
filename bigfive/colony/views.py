# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.colony.utils import *

mod = Blueprint('colony',__name__,url_prefix='/colony')

@mod.route('/test/')
def test():
    result = 'This is colony!'
    return json.dumps(result,ensure_ascii=False)