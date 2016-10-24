#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: user.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/04 21:49:09
"""
from flask_restful import Resource, reqparse, abort
from flask import g, jsonify
import copy
import json

from app.models import User
from app import db, auth

class UserListResource(Resource):
    def __init__(self):
        pass

    @auth.login_required
    def get(self):
        if g.user.id != 1:
            abort(403, message='not root user')
        users = User.query.all() 
        result = []
        for user in users:
            result.append(user.to_json())
        return result, 200

    @auth.login_required
    def post(self):
        #add user
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('username', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()

        if g.user.id != 1:
            abort(403, message='not admin')
        
        user = User.query.filter_by(username=args['username']).first()
        if user is not None:
            abort(403, message='user:{} already exist'.format(user.username))

        user = User(args['username'], args['password'], g.user.id)

        db.session.add(user)
        db.session.commit()
        return user.to_json(), 200

class UserResource(Resource):
    def __init__(self):
        pass

    @auth.login_required
    def get(self, u_id):
        if g.user.id != u_id and g.user.id != 1:
            abort(403, message='you cant get others information')
        user = User.query.get(u_id)
        if user is None:
            abort(404, message='user_id:{} not exist'.format(u_id))
        return user.to_json(), 200
    
    @auth.login_required
    def put(self, u_id):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('username', default=None)
        parser.add_argument('password', default=None)
        args = parser.parse_args()

        if g.user.id != 1:
            abort(403, message='not admin')

        user = User.query.get(u_id)
        if user is None:
            abort(403, message='user_id:{} not exist'.format(u_id))

        if args['username'] is not None:
            user.username = args['username']
        if args['password'] is not None:
            user.password = args['password']

        db.session.commit()
        return user.to_json(), 200

    @auth.login_required
    def delete(self, u_id):
        if g.user.id != 1:
            abort(403, message='not admin')
        user = User.query.get(u_id)
        if user is None:
            abort(403, message='user_id:{} not exist'.format(u_id))
        db.session.delete(user)
        db.session.commit()
        return '', 204

