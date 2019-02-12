# -*- coding: utf-8 -*-

from flask import Blueprint ,request
import json
from bigfive.firstpage.utils import *

mod = Blueprint('firstpage',__name__,url_prefix='/firstpage')


@mod.route('/test/')
def test():
    result = 'This is firstpage!'
    return json.dumps(result,ensure_ascii=False)


@mod.route('/search/', methods=['GET', 'POST'])
def search():
    keyword = request.args.get('keyword', default='').lower()

    page = request.args.get('page', default='1')
    size = request.args.get('size', default='6')

    order_name = request.args.get('order_name', default='group_name')
    order_type = request.args.get('order_type', default='asc')

    result = search_group(keyword, page, size, order_name, order_type)
    return json.dumps(result, ensure_ascii=False)

# @mod.route('/search/', methods=['GET', 'POST'])
# def search():
#     keyword = request.args.get('keyword', default='').lower()
#
#     page = request.args.get('page', default='1')
#     size = request.args.get('size', default='6')
#
#     person_order_name = request.args.get('person_order_name', default='username')
#     person_order_type = request.args.get('person_order_type', default='asc')
#     group_order_name = request.args.get('group_order_name', default='group_name')
#     group_order_type = request.args.get('group_order_type', default='asc')
#
#     result = search_person_and_group(keyword, page, size, person_order_name, group_order_name, person_order_type, group_order_type)
#     return json.dumps(result, ensure_ascii=False)

