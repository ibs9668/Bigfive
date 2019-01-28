# -*- coding: utf-8 -*-
from flask import Blueprint ,request,jsonify

import json

from bigfive.group.utils import *

mod = Blueprint('group',__name__,url_prefix='/group')

@mod.route('/test/')
def test():
    result = 'This is group!'
    return json.dumps(result,ensure_ascii=False)

@mod.route('/create_group/',methods=['POST'])
def cgroup():
    """创建群体"""
    # data = request.form.to_dict()
    try:
        data = request.json
        result = create_group(data)
    except:
        return jsonify({'ok':0,'data':[]})
    return jsonify({'ok':1,'data':[]})

@mod.route('/delete_group/',methods=['POST'])
def dgroup():
    """删除群体"""
    gid = request.form.get('gid')
    try:
        result = delete_group(gid)
    except:
        return jsonify({'ok':0,'data':[]})
    return jsonify({'ok':1,'data':[]})
    # return jsonify({'gid':group_id})

@mod.route('/search_group/',methods=['GET'])
def sgroup():
    """搜索群体"""
    group_name = request.args.get('gname')
    remark = request.args.get('remark')
    create_time = request.args.get('ctime')
    page = request.args.get('page','1')
    result = search_group(group_name,remark,create_time,page)
    return json.dumps(result,ensure_ascii=False)