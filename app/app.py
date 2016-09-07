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
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
import MySQLdb.cursors
from app.resource import *
from app.session import Session


app = Flask(__name__)
api = Api(app)
mysql = MySQL(cursorclass=MySQLdb.cursors.DictCursor)
db = SQLAlchemy(app, use_native_unicode='utf8')
session = Session()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'oa'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_oa?charset=utf8'
mysql.init_app(app)

api.add_resource(User,'/user')
api.add_resource(DocClass, '/docclass')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/is_login', methods=['POST', 'GET'])
def is_login():
    return jsonify(error=0,
                   data=session.valid_login_user(request.form['token']))

@app.route('/login', methods=['POST'])
def login():
    message = {'error' : 0, 'message' : '', 'data' : {}}
    token = check_login(request.form['username'], request.form['password'])
    if token is not None:
        message['message'] = 'successful login'
        message['data']['token'] = token
    else:
        message['error'] = 1
        message['message'] = 'invalid username or uncorrect password'

    return jsonify(message)

def check_login(name, password):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE name = '" + name + "' AND pass = '" + password + "'")
    data = cursor.fetchone()
    if data is None:
        return None
    token = session.add_user(name)

    return token
