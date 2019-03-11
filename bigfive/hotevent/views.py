# -*- coding: utf-8 -*-

from flask import Blueprint ,request,jsonify
import json
from bigfive.hotevent.utils import *

mod = Blueprint('hotevent',__name__,url_prefix='/hotevent')

@mod.route('/test')
def test():
    result = 'This is hotevent!'
    return json.dumps(result,ensure_ascii=False)


@mod.route('/hot_event_list/', methods=['POST'])
def hot_event_list():
    parameters = request.form.to_dict()
    keyword = parameters.get('keyword', '')
    page = parameters.get('page', '1')
    size = parameters.get('size', '10')
    order_name = parameters.get('order_name', 'name')
    order_type = parameters.get('order_type', 'asc')
    result = get_hot_event_list(keyword, page, size, order_name, order_type)
    return jsonify(result)


@mod.route('/create_hot_event/', methods=['POST'])
def create_hot_event():
    parameters = request.form.to_dict()
    event_name = parameters.get('event_name', '')
    keywords = parameters.get('keywords', '')
    location = parameters.get('location', '')
    start_date = parameters.get('start_date', '')
    end_date = parameters.get('end_date', '')
    # try:
    post_create_hot_event(event_name, keywords, location,  start_date, end_date)
    return jsonify(1)
    # except:
    #     return jsonify(0)


@mod.route('/time_hot')
def time_hot():
    s = request.args.get('s','')
    e = request.args.get('e','')
    result = get_time_hot(s,e)
    return jsonify(result)
@mod.route('/geo')
def geo():
    s = request.args.get('s','')
    e = request.args.get('e','')
    type = request.args.get('type','')
    result = get_geo(s,e,type)
    return jsonify(result)

@mod.route('/browser_date',methods=['GET'])
def browser_date():
    date = request.args.get('date','')
    result = get_browser_by_date(date)
    return jsonify(result)

@mod.route('/browser_geo',methods=['GET'])
def browser_geo():
    s = request.args.get('s','')
    e = request.args.get('e','')
    geo = request.args.get('geo','')
    result = get_browser_by_geo(geo,s,e)
    return jsonify(result)

@mod.route('/ingroup_renge',methods=['GET'])
def ingroup_renge():
    result = get_in_group_renge()
    return jsonify(result)
@mod.route('/ingroup_ranking',methods=['GET'])
def ingroup_ranking():
    event_id = request.args.get('eid')
    mtype = request.args.get('mtype')
    result = get_in_group_ranking(event_id,mtype)
    return jsonify(result)


@mod.route('/semantic', methods=['GET'])
def semantic():
    event_id = request.args.get('event_id')
    result = get_semantic(event_id)
    return jsonify(result)

