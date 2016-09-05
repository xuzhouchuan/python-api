#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: __init__.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/04 21:37:13
"""
from flask import Flask
from flask_restful import Api
from flaskext.mysql import MySQL
from app.resource import *


app = Flask(__name__)
api = Api(app)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'oa'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

api.add_resource(User,'/user')
api.add_resource(DocClass, '/docclass')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

