#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: borrow_authority.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/08 13:07:31
"""
from flask_restful import Resource, reqparse
import copy
import json
import datetime
from flask import jsonify

from app.models import  BorrowAuthority, User, DocClass, Doc
from app import db

class BorrowAuthorityResource(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass
    def get(self):
        return self.post()
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action')
        parser.add_argument('auth_id', type=int)
        parser.add_argument('username', required=True)
        parser.add_argument('to_username')
        parser.add_argument('to_doc_id_list', type=int, action='append')
        parser.add_argument('to_docclass_id_list', type=int, action='append')
        parser.add_argument('start_time')
        parser.add_argument('end_time')
        args = parser.parse_args()

        message = copy.deepcopy(BorrowAuthorityResource.RETURN_MESSAGE)
        if args['action'] is None:
            args['action'] = 'get'
        self._process_action(args, message)

        return jsonify(data=message['data'], error=message['error'], messge=message['message'])

    def _process_action(self, args, message):
        if args['action'] == 'get':
            if args['username'] != 'root':
                self._get_authorities(args['username'], message)
            elif args['to_username'] is not None:
                self._get_authorities(args['to_username'], message)
        elif args['action'] == 'get_all':
            if args['username'] != 'root':
                message['error'] = 1
                message['message'] = "not super user, cant get all auth"
                return
            self._get_all_authorities(message)
        elif args['action'] == 'add':
            if args['username'] != 'root':
                message['error'] = 1
                message['message'] = 'not super user, cannot add borrow auth'
                return
            print args
            self._add_authority(args['to_username'], args['to_doc_id_list'],
                    args['to_docclass_id_list'], args['start_time'], args['end_time'], message)
        elif args['action'] == 'del':
            if args['username'] != 'root':
                message['error'] = 1
                message['message'] = 'not super user, cannot del borrow auth'
                return
            self._del_authority(args['auth_id'], message)
        elif args['action'] == 'mod':
            if args['username'] != 'root':
                message['error'] = 1
                message['message'] = 'not super user, cannot mod borrow auth'
                return
            self._mod_authority(args['auth_id'], args['end_time'], message)
        else:
            message['error'] = 2
            message['message'] = 'not support action'
            return
                
    def _get_authorities(self, username, message):
        if username is None:
            message['error'] = 3
            message['message'] = 'user not exist'
        user = User.query.filter_by(username=username).first()
        if user is None:
            message['error'] = 3
            message['message'] = 'user not exist'
            return
        
        auths = BorrowAuthority.query.filter_by(user.id).all()

    def _get_all_authorities(self, message):
        auths = BorrowAuthority.query.filter(BorrowAuthority.end_time >= datetime.datetime.now())
        new_data = []
        for auth in auths:
            new_data.append(auth.to_json())
        message['data'] = new_data
    def _add_authority(self, username, doc_id_list, docclass_id_list, start_time, end_time, message):
        if username is None or (doc_id_list is None  and docclass_id_list is None) or end_time is None:
            message['error'] = 4
            message['message'] = 'no to_username or doc_id, docclass_id, end_time'
            return
        if start_time is None:
            start_time = datetime.datetime.now()
        else:
            try:
                start_time = datetime.datetime.strptime(start_time, '%Y%m%d%H%M%S')
            except:
                message['message'] += ' start time format error(%Y%m%d%H%M%S), to default now'
                start_time = datetime.datetime.now()
        tmp_end_time = None
        try:
            tmp_end_time = datetime.datetime.strptime(end_time, '%Y%m%d%H%M%S')
        except:
            if end_time == 'forever':
                tmp_end_time = datetime.datetime.now() + 3 * 365 * 24 * 60 * 60
            else:
                message['error'] = 6
                message['message'] += 'end time format error(%Y%m%d%H%M%S)'
                return
        end_time = tmp_end_time
        print start_time, '\t', end_time
        if end_time <= start_time:
            message['error'] = 7
            message['message'] += 'end_time <= start_time'
            return
        user = User.query.filter_by(username=username).first()
        if user is None:
            message['error'] = 5
            message['message'] = 'no to_username User'
        if doc_id_list is not None:
            for doc_id in doc_id_list:
                auth = BorrowAuthority(user.id, doc_id, None, start_time, end_time)
                db.session.add(auth)
        if docclass_id_list is not None:
            for docclass_id in docclass_id_list:
                auth = BorrowAuthority(user.id, None, docclass_id, start_time, end_time)
                db.session.add(auth)
        db.session.commit()

    def _del_authority(self, auth_id, message):
        if auth_id is None:
            message['error'] = '10'
            message['message'] = 'auth_id not provided'
        auth = BorrowAuthority.query.get(auth_id)
        if auth is not None:
            db.session.delete(auth)
            db.session.commit()
        message['message'] = 'delete auth successful'
    def _mod_authority(self, auth_id, end_time, message):
        if auth_id is None or end_time is None:
            message['error'] = 11
            message['message'] = 'auth id or end time not supported, cant modify'
            return
        auth = BorrowAuthority.query.get(auth_id)
        if auth is not None:
            auth.end_time = end_time
            db.session.commit()
        message['message'] = 'mod end time successful'






