#!/usr/bin/python
#coding=utf-8

from flask_restful import Resource, reqparse, abort
import copy
import json
from flask import jsonify, g
from app import db, auth
from app.models import Volumne, BorrowAuthority, ApplyFor 


class BorrowAuthorityListResource(Resource):
    def __init__(self):
        pass
    def get(self):
        result = []
        auths = BorrowAuthority.query.all()
        for a in auths:
            result.append(a.to_json())
        result.sort(key=lambda e:e['id'], reverse=True)
        return jsonify({'authorities' : result})

class BorrowAuthorityResource(Resource):
    def __init__(self):
        pass



