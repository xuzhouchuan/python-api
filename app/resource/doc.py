#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: doc.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/05 00:37:00
"""
from flask_restful import Resource, reqparse
import copy
import os
import time
import datetime
from flask import jsonify
import werkzeug
from werkzeug import secure_filename
from app import db
from app.models import DocClass, Doc, User, BorrowAuthority, Log
from flask import send_file

SAVE_DIR = './upload_files/'
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif','doc','docx','xls','xlsx'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
        

class DocResource(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass

    def _parse_request(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action', required=True)
        parser.add_argument('file_id')
        parser.add_argument('content')
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location=['files', 'form'])
        parser.add_argument('docclass_id', type=int)
        parser.add_argument('username', required=True)
        return parser.parse_args()

    def get(self):
        args = self._parse_request()
        message = copy.deepcopy(DocResource.RETURN_MESSAGE)
        if args['action'] == 'upload':
            message['error'] = 1
            message['message'] = 'method can\'t be used as post'
        else:
            self._process_action(args, message)
        if args['action'] != 'get':
            return jsonify(error=message['error'], message=message['message'], data=message['data'])
        else:
            if message['error'] != 0:
                return message, 412

            user = User.query.filter_by(username=args['username']).first()
            log = Log(user.id, datetime.datetime.now(), "download", "filename:%s" % args['file_name'], "")
            db.session.add(log)
            db.session.commit()

            fh = open(args['path'], 'rb')
            return send_file(fh, attachment_filename = args['file_name'], as_attachment=True)
    def post(self):
        args = self._parse_request()
        print args
        message = copy.deepcopy(DocResource.RETURN_MESSAGE)
        self._process_action(args, message)
        if args['action'] != 'get':
            return jsonify(error=message['error'], message=message['message'], data=message['data'])
        else:
            if message['error'] != 0:
                return message, 412
            fh = open(args['path'], 'rb')
            return send_file(fh, attachment_filename = args['file_name'], as_attachment=True)

    def _process_action(self, args, message):
        if 'action' not in args or args['action'] is None:
            message['error'] = 2
            message['message'] = 'no action provided'
        elif args['action'] == 'upload':
            self._upload(args, message)
        elif args['action'] == 'get':
            self._get_doc(args, message)
        elif args['action'] == 'get_info':
            self._get_doc_info(args, message)
        elif args['action'] == 'del':
            self._del_doc(args, message)
        elif args['action'] == 'get_all':
            self._get_all_doc(args, message)

    def _upload(self, args, message):
        if 'file' not in args or args['file'] is None:
            message['error'] = 3
            message['message'] = 'no file selected to upload'
            return
        if 'docclass_id' not in args or args['docclass_id'] is None:
            message['error'] = 8
            message['message'] = 'no docclass_id provided'
            return
        file = args['file']
        file_name = secure_filename(file.filename)
        if not allowed_file(file_name):
            message['error'] = 4
            message['message'] = 'not support file_type, support file type:%s' % ','.join(ALLOWED_EXTENSIONS)
            return
        extension = file_name.rsplit('.', 1)[1].lower()
        user = User.query.filter_by(username=args['username']).first()
        if user is None:
            message['error'] = 5
            message['message'] = 'user not exist:%s' % args['username']
            return
        user_id = user.id
        docclazz = DocClass.query.get(args['docclass_id'])
        if docclazz is None:
            message['error'] = 6
            message['message'] = 'docclass not exist:%d' % args['docclass_id']
            return
        docclazz_id = docclazz.id
        save_name = '%d_%s_%s' % (docclazz.id, time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())), file_name)
        save_dir = os.path.abspath(SAVE_DIR)
        if not os.path.isdir(save_dir):
            try:
                os.makedir(save_dir) 
            except:
                print "make dir :%s error" % SAVE_DIR
        path = os.path.join(save_dir, save_name)
        file.save(path)
        new_doc = Doc(file_name, docclazz_id, path, extension, None, user_id, datetime.datetime.now())
        db.session.add(new_doc)
        db.session.commit()
        message['error'] = 0
        message['message'] = 'upload file successful'

    def _get_doc(self, args, message):
        if 'file_id' not in args or args['file_id'] is None:
            message['error'] = 7
            message['message'] = 'no file name provided'
            return
        file_id = args['file_id']
        doc = Doc.query.get(file_id)
        if doc is None:
            message['error'] = 9
            message['message'] = 'file not exist in database'
            return
        args['file_name'] = doc.name
        args['path'] = doc.path
        binary = None
        with open(doc.path, 'r') as fh:
            binary = fh.read()

        message['data'] = binary
        message['message'] = 'success'
    def _get_doc_info(self, args, message):
        if 'file_id' not in args or args['file_id'] is None:
            message['error'] = 7
            message['message'] = 'no file name provided'
            return
        file_id = args['file_id']
        doc = Doc.query.get(file_id)
        if doc is None:
            messagy['error'] = 9
            message['message'] = 'file not exist in database'
            return
        args['file_name'] = doc.name
        args['path'] = doc.path
        message['data'] = doc.to_json()
        message['message'] = 'get info successful'

    def _del_doc(self, args, message):
        if 'file_id' not in args or args['file_id'] is None:
            message['error'] = 7
            message['message'] = 'no file name provided'
            return
        file_id = args['file_id']
        doc = Doc.query.get(file_id)
        if doc is None:
            message['error'] = 9
            message['message'] = 'file not exist in database'
            return
        path = doc.path
        doc_name = doc.name
        db.session.delete(doc)
        db.session.commit()
        print path
        if path is not None:
            os.remove(path)
        message['message'] = 'delete file:%s successful' % doc_name

    def _get_all_doc(self, args, message):
        if 'username' not in args or args['username'] is None:
            message['error'] = 10
            message['message'] = 'username not provided'
            return 
        name = args['username']
        res = []
        docs = Doc.query.filter(Doc.id>=0).all()
        if name == 'root':
            #auths = BorrowAuthority.query.filter(BorrowAuthority.doc_id>=1).all()
            #docs = Doc.query.filter(Doc.id>=0).all()
            for doc in docs:
                res.append(doc.to_json())

        else:
            auths = []
            user = User.query.filter_by(username=name).first()
            auths = BorrowAuthority.query.filter_by(user_id=user.id).all()
            for doc in docs:
                flag = False
                for au in auths:
                    if flag == True:
                        break
                    if au.doc_id is None:
                        pass
                    else:
                        if au.end_time >= datetime.datetime.now() and au.start_time <= datetime.datetime.now():
                            if au.doc_id == doc.id:
                                print au.doc_id, au.end_time
                                flag = True
                            #doc = Doc.query.get(au.doc_id)
                            #res.append(doc.to_json())
                if flag == False:
                    doc.path = ""
                res.append(doc.to_json())
        message['data'] = res

        



