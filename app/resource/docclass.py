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
import app
import copy
import json

class DocClass(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action')
        parser.add_argument('name')
        parser.add_argument('parent_id', type=int)
        parser.add_argument('customizable', type=int)
        parser.add_argument('new_parent_id', type=int)
        parser.add_argument('new_name')
        args = parser.parse_args()

        message = copy.deepcopy(DocClass.RETURN_MESSAGE)

        print args['action']
        if 'action' not in args or args['action'] is None or \
            args['action'] == '':
            args['action'] = 'get_all'
        
        if args['action'] == 'get_all':
            self.get_all_docclass(message)
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
            if 'name' not in args or args['name'] is None:
                message['error'] = 5
                message['message'] = 'mod doclass, no name'
            elif 'parent_id' not in args or args['parent_id'] is None:
                message['error'] = 6
                message['message'] = 'mod docclass, no parent_id'
            else:
                if ('new_parent_id' not in args or args['new_parent_id'] is None) \
                    and ('new_name' not in args or args['new_name'] is None):
                    message['error'] = 7
                    message['message'] = 'mod docclass, no new name or no new parent docclass'
                    
                else:
                    self.mod_docclass(args['name'], args['parent_id'], args['new_name'], args['new_parent_id'], message)
        elif args['action'] == 'del':
            if 'name' not in args or args['name'] is None or 'parent_id' not in args or \
               args['parent_id'] is None:
                message['error'] = 8
                messasge['message'] = 'del docclass, no name or parent'
            self.del_docclass(args['name'], args['parent_id'], message)
        else:
            message['error'] = 1
            message['message'] = 'not support api'

        return json.dumps(message, ensure_ascii=False), 202

    def get_all_docclass(self, message):
        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docclass")
        data = cursor.fetchall()
        if data is not None:
            message['data'] = json.dumps(data) 
        conn.close()
        cursor.close()
    
    def add_docclass(self, name, parent_id, customizable, message):
        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docclass WHERE name='%s' AND parent_id=%d" % (name, parent_id))
        data = cursor.fetchone()
        if data is not None:
            message['error'] = 4
            message['message'] = 'the docclass:%s already exist in it\'s parent' % name
            return

        sql_s = "INSERT INTO docclass(name, parent_id, customizable) VALUES ('%s', %d, %d)" \
                % (name, parent_id, customizable)
        cursor.execute(sql_s)
        conn.commit()
        cursor.close()
        conn.close()
        message['message'] = 'add docclass:%s successful' % name

    def mod_docclass(self, name, parent_id, new_name, new_parent_id, message):
        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docclass WHERE name='%s' AND parent_id=%d" % (name, parent_id))
        data = cursor.fetchone()
        if data is None:
            message['error'] = 7
            message['message'] = 'mod docclass, no docclass:%s' % name
            return
        base_id = data[0]
        if new_name is None and new_parent_id is not None:
            cursor.execute("SELECT * FROM docclass WHERE id=%d" % new_parent_id)
            data = cursor.fetchone()
            if data is None:
                message['error'] = 8
                message['message'] = 'mod docclass, new parent not exist'
                return
            cursor.execute("UPDATE docclass SET parent_id=%d WHERE id=%d" % (new_parent_id, base_id))
        elif new_name is not None and new_parent_id is None:
            cursor.execute("UPDATE docclass SET name='%s' WHERE id=%d" % (new_name, base_id))
        elif new_name is not None and new_parent_id is not None:
            cursor.execute("UPDATE docclass SET name='%s', parent_id=%d WHERE id=%d" % \
                    (new_name, new_parent_id, base_id))
        else:
            print "reach a unexceptable branch"
        conn.commit()
        cursor.close()
        conn.close()
    def del_docclass(self, name, parent_id, message):
        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM docclass WHERE name='%s' AND parent_id=%d" % (name, parent_id))
        data = cursor.fetchone()
        if data is None:
            message['error'] = 9
            message['message'] = 'no such docclass:%s exist' % name
            return
        class_id = data[0]
        cursor.execute("SELECT * FROM doc WHERE class_id=%d" % class_id) 
        data = cursor.fetchone()
        if data is not None:
            message['error'] = 10
            message['message'] = 'docclass:%s not empty, has exist docs' % name
            return
        cursor.execute("DELETE FROM docclass WHERE id=%d" % class_id)
        conn.commit()
        cursor.close()
        conn.close()
        message['message'] = 'remove docclass successfull'

