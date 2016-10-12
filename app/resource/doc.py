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
import datetime
import os.path
import re
from flask_restful import Resource, reqparse, abort
from flask import jsonify
from app import db
from app.models import DocClass, Volumne, VolumneProperty, DocProperty, VolumneValue, Doc, DocValue


UPLOAD_DIR ="upload_document"

def secure_filename(file_name):
    secure_name = re.sub('[" \-~\|\-/]', '_', file_name)
    return secure_name

class DocListResource(Resource):
    def __init__(self):
        pass
    def get(self):
        pass
    
    def post(self):
        #add a doc
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', required=True)
        parser.add_argument('volumne_id', type=int, required=True)
        parser.add_argument('values', action='append', default=[])
        args = parser.parse_args()

        vol = Volumne.query.get(args['volumne_id'])
        if vol is None:
            abort(403, message='volumne id:{} not exist'.format(args['volumne_id']))

        maybe_exist = Doc.query.filter_by(volumne_id=args['volumne_id'],
                name=args['name']).first()
        if maybe_exist is not None:
            abort(403, message=u'volumne:{} already has the same name doc:{}'.format(vol.name, args['name']))

        path = os.path.join(UPLOAD_DIR, secure_filename(vol.name), secure_filename(args['name']))

        new_doc = Doc(args['name'], vol.id, path, vol.type, 1, datetime.datetime.now())
        
        db.session.add(new_doc)
        db.session.commit()
        #upload values
        for k_v in args['values']:
            k, v = k_v.split('=')
            doc_prop = DocProperty.query.filter_by(name=k, volumne_id=vol.id).first()
            if doc_prop is None:
                #if property not exist, ignore it, TODO
                continue
            old_value = DocValue.query.filter_by(doc_id=new_doc.id, property_id=doc_prop.id).first()
            if old_value is not None:
                old_value.value = v
            else:
                new_value = DocValue(v, doc_prop.id, new_doc.id, doc_prop.name, doc_prop.order)
                db.session.add(new_value)
        db.session.commit()
        #upload files
        #TODO

        return new_doc.to_json()


class DocResource(Resource):
    RETURN_MESSAGE = {'error' : 0, 'message' : '', 'data' : ''}
    def __init__(self):
        pass

    def get(self, d_id):
        #get a doc
        doc = Doc.query.get(d_id)
        if doc is None:
            abort(404, message="doc id:{} not exist".format(d_id))

        result = doc.to_json()
        result['values'] = []
        result['files'] = []
        #property values
        for v in doc.values:
            result['values'].append(v.to_json())
        result['values'].sort(key=lambda e:e['order'])
        #files
        #TODO
        return result, 200

    def put(self, d_id):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('values', action='append', default=[])
        args = parser.parse_args()

        doc = Doc.query.get(d_id)
        if doc is None:
            abort(404, message="doc id:{} not exist".format(d_id))

        for k_v in args['values']:
            k, v = k_v.split('=')
            changed = False
            for vals in doc.values:
                if vals.property_name == k:
                    vals.value = v
                    changed = True
                    break
            if not changed:
                prop = DocProperty.query.filter_by(name=k, volumne_id = doc.volumne.id).first()
                if prop is None:
                    continue
                new_value = DocValue(v, prop.id, doc.id, prop.name, prop.order)
                db.session.add(new_value)
        db.session.commit()
        #modify upload file #TODO
        return doc.to_json(), 200

    def delete(self, d_id):
        doc = Doc.query.get(d_id)
        if doc is None:
            abort(404, message="doc id:{} not exist".format(d_id))
        #TODO rm -rf path
        db.session.delete(doc)
        db.session.commit()
        return '', 204

        



