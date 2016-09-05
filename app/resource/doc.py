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
import app
import copy
import json

class Doc(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass
    def get(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('action', required=True)
        parser.add_argument('name', required=True)
        #TODO
        return 'not support'

