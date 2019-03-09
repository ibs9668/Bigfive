# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, Blueprint,session,redirect,make_response
from optparse import OptionParser
from bigfive import create_app


optparser = OptionParser()
optparser.add_option('-p','--port',dest='port',help='Server Http Port Number', default=5000, type='int')
(options, args) = optparser.parse_args()

app = create_app()


# @app.route('/')
# def redirect_2_login():
#     if not session:
#         return redirect('manage/login')
#     return redirect('index/homepage')


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=options.port)
