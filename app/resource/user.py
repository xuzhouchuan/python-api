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
from flask_restful import Resource, reqparse
import copy
import json

from app.models import User
from app import db


class UserResource(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action', required=True)
        parser.add_argument('username', required=True)
        parser.add_argument('password')
        parser.add_argument('create_user')
        args = parser.parse_args()
        message = copy.deepcopy(UserResource.RETURN_MESSAGE)

        return self.process_action(args, message), 200

    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action', required=True)
        parser.add_argument('username', required=True)
        parser.add_argument('password')
        parser.add_argument('create_user')
        args = parser.parse_args()
        message = copy.deepcopy(UserResource.RETURN_MESSAGE)
        return self.process_action(args, message), 200

    def process_action(self, args, message):
        username = args['username']
        if args['action'] == 'add':
            if 'password' not in args or 'create_user' not in args:
                message['error'] = 2
                message['message'] = 'not password or create_user'
            else:
                self.add_user(username, args['password'], args['create_user'], message)
        elif args['action'] == 'del':
            self.del_user(username, message)
        elif args['action'] == 'get':
            self.get_user(username, message)
        else:
            message['error'] = 1
            message['message'] = 'action not support'
        return message
    
    def get_user(self, username, message):
        user = User.query.filter_by(username=username).first()
        if user is None:
            message['error'] = 3
            message['message'] = 'no such user with username:' + username
            return
        message['data'] = user.to_json()

    def del_user(self, username, message):
        user = User.query.filter_by(username=username).first()
        if user is not None:
            db.session.delete(user)
            db.session.commit()

    def add_user(self, username, password, create_user_name, message):
        user = User.query.filter_by(username=username).first()
        create_user = User.query.filter_by(username=create_user_name).first()
        if create_user is None:
            message['error'] = 4
            message['message'] = 'create_user:%s not exist' % create_user
            return
        if user is not None:
            message['error'] = 5
            message['message'] = 'user name:%s already exist' % username
            return
        new_user = User(username, password, create_user.id)
        db.session.add(new_user)
        db.session.commit()
        
        print "INSERT INTO user(name, pass, createid) VALUES ('%s', '%s', %s)" \
                % (username, password, create_user_name)
        message['messsage'] = 'add user successful'




