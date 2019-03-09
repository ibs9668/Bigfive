# -*- coding: utf-8 -*-

from flask import Blueprint ,request,jsonify
import json
from bigfive.hotevent.utils import *

mod = Blueprint('hotevent',__name__,url_prefix='/hotevent')

@mod.route('/test')
def test():
    result = 'This is hotevent!'
    return json.dumps(result,ensure_ascii=False)

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
    result = get_geo(s,e)
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

@mod.route('/renge',methods=['GET'])
def renge():
    result = get_renge()
    return jsonify(result)