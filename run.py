# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, Blueprint,session,redirect,make_response
from optparse import OptionParser
from bigfive import create_app
from flask_cors import CORS

optparser = OptionParser()
optparser.add_option('-p','--port',dest='port',help='Server Http Port Number', default=5000, type='int')
(options, args) = optparser.parse_args()

app = create_app()
CORS(app, supports_credentials=True)
app.secret_key = "ruman"

# @app.route('/')
# def redirect_2_login():
#     if not session:
#         return redirect('manage/login')
#     return redirect('index/homepage')
@app.after_request
def af_request(resp):
    """
    #请求钩子，在所有的请求发生后执行，加入headers。
    :param resp:
    :return:
    """
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=options.port)
