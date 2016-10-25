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
from flask import Flask, g, make_response
from flask_restful import Api, abort
from flaskext.mysql import MySQL
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
import MySQLdb.cursors
from functools import wraps
import time
import datetime
#from app.models import Log


app = Flask(__name__)
api = Api(app)
mysql = MySQL(cursorclass=MySQLdb.cursors.DictCursor)
db = SQLAlchemy(app, use_native_unicode='utf8')
auth = HTTPBasicAuth()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'test_oa'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_oa?charset=utf8'
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
mysql.init_app(app)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kw):
        print g.user.to_json()
        if g.user.id != 1:
            return make_response(jsonify({'message':'Unauthorized access'}), 200)
        return f(*args, **kw)
    return wrapper

from models import *
from resource import UserResource, DocClassResource, DocClassListResource, DocResource, ViewLog, ApplyForResource, VolumneResource, VolumneListResource, DocListResource, UserListResource, ApplyForListResource
api.add_resource(UserResource, '/user/<int:u_id>')
api.add_resource(UserListResource, '/user')
api.add_resource(DocClassResource, '/docclass/<int:dclass_id>')
api.add_resource(DocClassListResource, '/docclass')
api.add_resource(VolumneResource, '/volumne/<int:v_id>')
api.add_resource(VolumneListResource, '/volumne')
api.add_resource(DocResource, '/doc/<int:d_id>')
api.add_resource(ApplyForResource, '/apply/<int:a_id>')
api.add_resource(ApplyForListResource, '/apply')
api.add_resource(DocListResource, '/doc')
api.add_resource(ViewLog, '/viewlog')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/add_user', methods=['POST'])
@auth.login_required
def new_user():
    if g.user.id != 1:
        return 'not root user, cant add user', 403
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return 'username:{}, passowrd:{}'.format(username, password), 400    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return 'user:{} already exist'.format(username), 400    # existing user
    user = User(username, password, 1)
    #user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    log_info = u'{} 添加用户 user_id:{}, user_name:{}'.format(g.user.username,
            user.id, user.username)
    Log.logging(g.user.id, datetime.datetime.now(), 'add-user', log_info)
    return jsonify(user.to_json())

@app.route('/api/token', methods=['POST', 'GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    Log.logging(g.user.id, datetime.datetime.now(), 'login', u'{} 登录'.format(g.user.username))
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.route('/api/auth/list', methods=['POST', 'GET'])
@auth.login_required
def list_authority():
    if g.user.id != 1:
        return 'not root user, cant apply authority', 403

    result = {'authorities' : [], 'applyfors' : []}
    auths = BorrowAuthority.query.all()
    for a in auths:
        result['authorities'].append(a.to_json())
    result['authorities'].sort(key=lambda e:e['id'], reverse=True)
    applys = ApplyFor.query.all()
    for apl in applys:
        result['applyfors'].append(apl.to_json())
    result['applyfors'].sort(key=lambda e:e['id'], reverse=True)
    return jsonify(result), 200

@app.route('/api/auth/authorize', methods=['GET']) 
@auth.login_required
def apply_authority():
    if g.user.id != 1:
        return 'not root user, cant apply authority', 403
    
    apply_for_id = request.args.get('apply_for_id', None)
    action = request.args.get('action', None)
    if apply_for_id is None or action is None:
        return 'no apply for id or no action', 400
    apply_for = ApplyFor.query.get(apply_for_id)
    if apply_for is None:
        return 'no such a apply for, id is:{}'.format(apply_for_id), 400
    user_name = apply_for.user.username
    vol_name = apply_for.volumne.name
    if action == 'deny':
        apply_for.denied = True
        db.session.commit()
    elif action == 'accept':
        user_id = apply_for.user_id
        vol_id = apply_for.volumne_id
        start_t = apply_for.start_time
        end_t = apply_for.end_time
        #delete old BorrowAuthority
        for bo_au in BorrowAuthority.query.filter_by(user_id=user_id, volumne_id=vol_id):
            db.session.delete(bo_au)
        #insert in to BorrowAuthority
        borrow_auth = BorrowAuthority(user_id,
                vol_id,
                start_t,
                end_t)
        db.session.add(borrow_auth)
        #del in ApplyFor
        db.session.delete(apply_for)
        db.session.commit()

    log_info = u'{} 设置借阅权限:action:{} user:{} volumne:{}'.format(g.user.username,
            action, user_name, vol_name) 
    Log.logging(g.user.id, datetime.datetime.now(), 'authorize', log_info)
    return '', 204
    
