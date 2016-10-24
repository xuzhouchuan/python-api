#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: apply_for.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/16 21:18:24
"""
from flask_restful import Resource, reqparse, abort
import copy
import json
import datetime
from flask import jsonify, g

from app.models import ApplyFor, Volumne
from app import db, auth

class ApplyForListResource(Resource):
    def __init__(self):
        pass
    
    @auth.login_required
    def get(self):
        result = []
        applys = []
        if g.user.id == 1:
            applys = ApplyFor.query.all()
        else:
            applys = ApplyFor.query.filter_by(user_id=g.user.id).all()
        for apl in applys:
            result.append(apl.to_json())
        result.sort(key=lambda e:e['id'], reverse=True)

        return jsonify(result), 200

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('volumne_id', required=True)
        parser.add_argument('start_time', required=True)
        parser.add_argument('end_time', required=True)
        args = parser.parse_args()

        vol_id = args['volumne_id']
        start_s = args['start_time']
        end_s = args['end_time']
        if vol_id is None or start_s is None or end_s is None:
            abort(400, message='must supply volumne_id, start_time, end_time')
        vol = Volumne.query.get(vol_id)
        if vol is None:
            abort(400, message='volumne not exist')
        old_apply_for = ApplyFor.query.filter_by(volumne_id=vol_id, user_id=g.user.id).first()
        if old_apply_for is not None:
            abort(400, message=u'you already have a request on volumne:{}'.format(vol.name))
        start_t = datetime.datetime.strptime(start_s, '%Y-%m-%d %H:%M:%S')
        end_t = datetime.datetime.strptime(end_s, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        if end_t <= now or start_t >= end_t:
            print "%s:%s:%s" % (now, start_t, end_t)
            abort(400,
                  message="end time:{} must after start time:{}, and after now{}".format(end_s, start_s, now))
        apply_for = ApplyFor(g.user.id, vol_id, start_t, end_t)
        db.session.add(apply_for)
        db.session.commit()
        return '', 204

class ApplyForResource(Resource):
    def __init__(self):
        pass
    
    def get(self, a_id):
        pass

    def put(self, a_id):
        return 'empty method', 200

    @auth.login_required
    def delete(self, a_id):
        apply = ApplyFor.query.get(a_id)
        if apply is None or (apply.user_id != g.user.id and g.user.id != 1):
            abort(403, message='no apply or you have no permission to del this applyfor')

        db.session.delete(apply)
        db.session.commit()
        return '', 204
