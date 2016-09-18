#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: docclass.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/05 00:47:36
"""
from flask_restful import Resource, reqparse
import copy
import json
from flask import jsonify
from app import db
from app.models import DocClass, Doc

class DocClassResource(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass

    def post(self):
        args = self._parse_request()
        message = copy.deepcopy(DocClassResource.RETURN_MESSAGE)
        self._process_action(args, message)
        return jsonify(data=message['data'], error=message['error'], message=message['message'])

        
    def get(self):
        args = self._parse_request()
        message = copy.deepcopy(DocClassResource.RETURN_MESSAGE)
        self._process_action(args, message)
        return jsonify(data=message['data'], error=message['error'], message=message['message'])

    def _process_action(self, args, message):
        if 'action' not in args or args['action'] is None or \
            args['action'] == '':
            args['action'] = 'get_all'
        
        if args['action'] == 'get_all':
            self.get_all_docclass(message)
        elif args['action'] == 'get_docs':
            self.get_docs(args, message)
        elif args['action'] == 'add':
            if 'name' not in args or args['name'] is None:
                message['error'] = 2
                message['message'] = 'add docclass, no name'
            elif 'parent_id' not in args or args['parent_id'] is None:
                message['error'] = 3
                message['message'] = 'no parent_id provide'
            else:
                if 'customizable' not in args or args['customizable'] is None:
                    args['customizable'] = 0 
                self.add_docclass(args['name'], args['parent_id'], args['customizable'], message)

        elif args['action'] == 'mod':
            if 'docclass_id' not in args or args['docclass_id'] is None:
                message['error'] = 11
                message['message'] = 'docclass_id not provide'
            else:
                if ('new_parent_id' not in args or args['new_parent_id'] is None) \
                    and ('new_name' not in args or args['new_name'] is None):
                    message['error'] = 7
                    message['message'] = 'mod docclass, no new name or no new parent docclass'
                    
                else:
                    self.mod_docclass(args['docclass_id'], args['new_name'], args['new_parent_id'], message)
        elif args['action'] == 'del':
            docclass_id = None
            name = None
            parent_id = None
            if 'docclass_id' in args and args['docclass_id'] is not None:
                docclass_id = args['docclass_id'] 
            elif 'name' in args and args['name'] is not None and 'parent_id' in args and \
               args['parent_id'] is not None:
                name = args['name']
                parent_id = args['parent_id']
            else:
                message['error'] = 8
                message['message'] = 'del docclass, no name or parent and no docclass id'
            self.del_docclass(args['name'], args['parent_id'], args['docclass_id'], message)
        else:
            message['error'] = 1
            message['message'] = 'not support api'



    def _parse_request(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action')
        parser.add_argument('username', required=True)
        parser.add_argument('name')
        parser.add_argument('parent_id', type=int)
        parser.add_argument('customizable', type=int)
        parser.add_argument('new_parent_id', type=int)
        parser.add_argument('new_name')
        parser.add_argument('docclass_id', type=int)
        return parser.parse_args()


    def get_all_docclass(self, message):
        doc_clazzes = DocClass.query.all()
        if doc_clazzes is not None:
            message['data'] = []
            for item in doc_clazzes:
                message['data'].append(item.to_json()) 
    
    def add_docclass(self, name, parent_id, customizable, message):
        doc_clazz = DocClass.query.filter_by(name=name, parent_id=parent_id).first()
        if doc_clazz is not None:
            message['error'] = 4
            message['message'] = 'the docclass:%s already exist in it\'s parent' % name
            return
        new_doc_clazz = DocClass(name, parent_id, customizable)
        db.session.add(new_doc_clazz)
        db.session.commit()
        message['message'] = 'add docclass:%s successful' % name

    def mod_docclass(self, docclass_id, new_name, new_parent_id, message):
        doc_clazz = DocClass.query.get(docclass_id)
        if doc_clazz is None:
            message['error'] = 7
            message['message'] = 'mod docclass, no docclass:%s' % name
            return
        if new_name is None and new_parent_id is not None:
            parent_clazz = DocClass.query.get(new_parent_id)
            if parent_clazz is None:
                message['error'] = 8
                message['message'] = 'mod docclass, new parent not exist'
                return
            doc_clazz.parent_id = new_parent_id
            db.session.commit()
        elif new_name is not None and new_parent_id is None:
            doc_clazz.name = new_name
            db.session.commit()
        elif new_name is not None and new_parent_id is not None:
            doc_clazz.name = new_name
            doc_clazz.parent_id = new_parent_id
            db.session.commit()
        else:
            print "reach a unexceptable branch"

    def del_docclass(self, name, parent_id, docclass_id, message):
        doc_clazz = None
        if docclass_id is not None:
            doc_clazz = DocClass.query.get(docclass_id)
        else:
            doc_clazz = DocClass.query.filter_by(name=name, parent_id=parent_id).first()
        if doc_clazz is None:
            message['error'] = 9
            message['message'] = 'no such docclass:%s exist' % name
            return
        doc = Doc.query.filter_by(docclass_id=doc_clazz.id).first()
        if doc is not None:
            message['error'] = 10
            message['message'] = 'docclass:%s not empty, has exist docs' % name
            return
        db.session.delete(doc_clazz)
        db.session.commit()
        message['message'] = 'remove docclass successfull'

    def get_docs(self, args, message):
        if 'docclass_id' not in args or args['docclass_id'] is None:
            message['error'] = 11
            message['message'] = 'docclass_id not provide'
            return
        docclazz = DocClass.query.get(args['docclass_id'])
        if docclazz is None:
            message['error'] = 9
            message['message'] = 'no such docclass:%s exist' % name
            return
        docs = docclazz.docs
        doc_list = []
        for doc in docs:
            doc_list.append(doc.to_json())
        message['data'] = doc_list


