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

from flask_restful import Resource, reqparse, abort
import copy
import json
import datetime
from flask import jsonify, g
from app import auth, db
from app.models import Log
from sqlalchemy import desc

class ViewLog(Resource):
    def __init__(self):
        pass

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('page_size', type=int, default=10)
        parser.add_argument('page', type=int, default=1)
        args = parser.parse_args()

        if g.user.id != 1:
            abort(403, message='must be root user')

        page = args['page']
        page_size = args['page_size']

        if page_size <= 10:
            page_size = 10
        if page_size >= 50:
            page_size = 50

        paginate = Log.query.paginate(1, page_size, False)
        total = paginate.total
        page_num = paginate.pages
        if page <= 0:
            page = 1
        if page > page_num:
            page = page_num
        paginate = Log.query.order_by(desc(Log.optime)).paginate(page, page_size, False)
        logs = paginate.items
        
        newdata = []
        for log in logs:
            newdata.append(log.to_json())

        return {"data": newdata, "page_num" : page_num, "page_size" : page_size, "log_num": total}, 200

            
