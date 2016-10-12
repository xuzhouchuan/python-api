#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: main.py
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
from session import Session
#from app.models import Log


app = Flask(__name__)
api = Api(app)
mysql = MySQL(cursorclass=MySQLdb.cursors.DictCursor)
db = SQLAlchemy(app, use_native_unicode='utf8')
session = Session()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'test_oa'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_oa?charset=utf8'
mysql.init_app(app)


from models import *
from resource import UserResource, DocClassResource, DocClassListResource, DocResource, BorrowAuthorityResource, ViewLog, ApplyForResource, VolumneResource, VolumneListResource, DocListResource
api.add_resource(UserResource,'/user')
api.add_resource(DocClassResource, '/docclass/<int:dclass_id>')
api.add_resource(DocClassListResource, '/docclass')
api.add_resource(VolumneResource, '/volumne/<int:v_id>')
api.add_resource(VolumneListResource, '/volumne')
api.add_resource(DocResource, '/doc/<int:d_id>')
api.add_resource(DocListResource, '/doc')
api.add_resource(BorrowAuthorityResource, '/borrow')
api.add_resource(ViewLog, '/viewlog')
api.add_resource(ApplyForResource, '/apply')

session.check_thread()


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
    
    user = User.query.filter_by(username=request.form['username']).first()
    log = Log(user.id, datetime.now(), "login", "", "");
    db.session.add(log)
    db.session.commit()

    return jsonify(message)

def check_login(name, password):
    user = User.query.filter_by(username=name, password=password).first()
    if user is None:
        return None
    token = session.add_user(name)

    return token
