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
import app
import copy
import json


class User(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action', required=True)
        parser.add_argument('user_name', required=True)
        parser.add_argument('password')
        parser.add_argument('create_user')
        args = parser.parse_args()
        message = copy.deepcopy(User.RETURN_MESSAGE)

        return self.process_action(args, message), 200

    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action', required=True)
        parser.add_argument('user_name', required=True)
        parser.add_argument('password')
        parser.add_argument('create_user')
        args = parser.parse_args()
        message = copy.deepcopy(User.RETURN_MESSAGE)
        return self.process_action(args, message), 200

    def process_action(self, args, message):
        user_name = args['user_name']
        if args['action'] == 'add':
            if 'password' not in args or 'create_user' not in args:
                message['error'] = 2
                message['message'] = 'not password or create_user'
            else:
                self.add_user(user_name, args['password'], args['create_user'], message)
        elif args['action'] == 'del':
            self.del_user(user_name, message)
        elif args['action'] == 'get':
            self.get_user(user_name, message)
        else:
            message['error'] = 1
            message['message'] = 'action not support'
        return message
    
    def get_user(self, user_name, message):
        cursor = app.mysql.connect().cursor()
        cursor.execute("SELECT id,name,createid from user where name = '" + user_name + "'")
        data = cursor.fetchone()
        if data is None:
            message['error'] = 3
            message['message'] = 'no such user with username:' + user_name
            return
        message['data'] = data

    def del_user(self, user_name, message):
        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user where name='" + user_name +"'")
        message['data'] = 'del user'
        conn.commit()
        cursor.close()
        conn.close()

    def add_user(self, user_name, password, create_user, message):
        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE name = '" + create_user +"'")
        data = cursor.fetchone()
        if data is None:
            message['error'] = 4
            message['message'] = 'create_user:%s not exist' % create_user
            return
        create_id = data['id']
        cursor.execute("SELECT * FROM user WHERE name = '" + user_name + "'")
        data = cursor.fetchone()
        if data is not None:
            message['error'] = 5
            message['message'] = 'user name:%s already exist' % user_name
            return
        cursor.execute("INSERT INTO user(name, pass, createid) VALUES ('%s', '%s', %s)" \
                % (user_name, password, create_id))
        conn.commit()
        cursor.close()
        conn.close()
        print "INSERT INTO user(name, pass, createid) VALUES ('%s', '%s', %s)" \
                % (user_name, password, create_id)
        message['messsage'] = 'add user successful'




