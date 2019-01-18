# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.person.utils import *

mod = Blueprint('person',__name__,url_prefix='/person')

@mod.route('/test/')
def test():
    result = 'This is person!'
    return json.dumps(result,ensure_ascii=False)