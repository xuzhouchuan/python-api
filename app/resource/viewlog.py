#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: viewlog.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/07 00:20:23
Description:
    not tested.
"""

from flask_restful import Resource, reqparse
import app
import copy
import json
import datetime
from flask import jsonify

class CJsonEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj)  


class ViewLog(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        #parser.add_argument('userid', type=int)
        parser.add_argument('page', type=int)
        args = parser.parse_args()

        message = copy.deepcopy(ViewLog.RETURN_MESSAGE)

        #print args
        #if 'userid' not in args or args['userid'] is None:
        #    message['error'] = 1
        #    message['message'] = 'invalid userid'
        #else:
        if 'page' not in args or args['page'] is None:
            args['page'] = 0
        top = (args['page'] + 1) * 10
        skip = args['page'] * 10

        conn = app.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM log order by id desc limit %d" % top)
        data = cursor.fetchall()
        newdata = []
        for i in range(skip, len(data)):
            newdata.append(data[i])
        if newdata is not None:
            message['data'] = newdata
        conn.close()
        cursor.close()
        #return json.dumps(message, ensure_ascii=False, cls=CJsonEncoder), 202
        return jsonify(data=message['data'], message=message['message'], error=message['error'])

            



