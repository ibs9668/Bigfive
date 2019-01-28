# -*- coding: utf-8 -*-
from flask import Blueprint ,request,jsonify

import json

from bigfive.group.utils import *
import traceback
mod = Blueprint('group',__name__,url_prefix='/group')

@mod.route('/test/')
def test():
    result = 'This is group!'
    return json.dumps(result,ensure_ascii=False)

@mod.route('/create_group/',methods=['POST'])
def cgroup():
    """创建群体"""
    # data = request.form.to_dict()

    data = request.json
    result = create_group(data)
    return jsonify(1)

@mod.route('/delete_group/',methods=['POST'])
def dgroup():
    """删除群体"""
    # gid = request.form.get('gid')
    gid = request.json.get('gid')
    return jsonify(1)

@mod.route('/search_group/',methods=['GET'])
def sgroup():
    """搜索群体"""
    group_name = request.args.get('gname','')
    remark = request.args.get('remark','')
    create_time = request.args.get('ctime','')
    page = request.args.get('page','1')
    size = request.args.get('size','10')
    result = search_group(group_name,remark,create_time,page,size)
    return json.dumps(result,ensure_ascii=False)