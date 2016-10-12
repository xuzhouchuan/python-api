#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: volumne.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/10/11 16:42:17
"""
from flask_restful import Resource, reqparse, abort
import copy
import json
from flask import jsonify
from app import db
from app.models import DocClass, Volumne, VolumneProperty, DocProperty, VolumneValue, Doc


class VolumneListResource(Resource):
    def __init__(self):
        pass
    def get(self):
        pass
    def post(self):
        #add a volumne
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', required=True)
        parser.add_argument('docclass_id', type=int, required=True)
        parser.add_argument('doc_properties', action='append', default=[])
        parser.add_argument('values', action='append', default=[])
        args = parser.parse_args()

        doc_class = DocClass.query.get(args['docclass_id'])
        if doc_class is None or doc_class.level != 4:
            abort(403, message='doc class not exist or not leaf doc class')

        maybe_exit = Volumne.query.filter_by(docclass_id=args['docclass_id'], name=args['name']).first()
        if maybe_exit is not None:
            abort(403, message='doc class {} already has the volumne:{}'.format(doc_class.name, args['name']))

        new_vol = Volumne(args['name'], args['docclass_id'], doc_class.type)
        db.session.add(new_vol)
        db.session.commit()

        #add doc_properties
        order = 0
        for prop in args['doc_properties']:
            doc_prop = DocProperty(prop, new_vol.id, order)
            order += 1
            db.session.add(doc_prop)
        db.session.commit()

        #add values
        for key_value in args['values']:
            k, v = key_value.split('=')
            vol_prop = VolumneProperty.query.filter_by(name=k, docclass_id=args['docclass_id']).first()
            if vol_prop is None:
                abort(403, messsage='volumne property {} not exist'.format(k))
            new_value = VolumneValue(v, vol_prop.id, new_vol.id, vol_prop.name, vol_prop.order)
            db.session.add(new_value)
        db.session.commit()

        return new_vol.to_json(), 200



class VolumneResource(Resource):
    def __init__(self):
        pass

    def get(self, v_id):
        #get a volumne
        vol = Volumne.query.get(v_id)
        if vol is None:
            abort(403, message='volumne id:{} not exist'.format(vol))
        result = vol.to_json()
        result['docs'] = []
        result['values'] = []
        result['doc_properties'] = []
        #docs
        for doc in vol.docs:
            result['docs'].append(doc.to_json())
        #values
        for v in vol.values:
            result['values'].append(v.to_json())
            result['values'].sort(key=lambda e:e['order'])
        #doc_props
        for d_prop in vol.properties:
            result['doc_properties'].append(d_prop.to_json())
            result['doc_properties'].sort(key=lambda e:e['order'])

        return result, 200

    def put(self, v_id):
        #modify a volumne
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name')
        parser.add_argument('values', action='append', default=[])
        args = parser.parse_args()

        vol = Volumne.query.get(v_id)
        if vol is None:
            abort(403, message='volumne id:{} not exist'.format(vol))

        if args.get('name', None) is not None:
            vol.name = args['name']

        for k_v in args['values']:
            k, v = k_v.split('=')
            vol_prop = VolumneProperty.query.filter_by(docclass_id=vol.docclass_id,
                    name=k).first()
            if vol_prop is None:
                continue
            vol_value = VolumneValue.query.filter_by(property_id=vol_prop.id, volmne_id=vol.id).first()
            if vol_value is not None:
                vol_value.value = v
            else:
                new_value = VolumneValue(v, vol_prop.id, vol.id, vol_prop.name, vol_prop.order)
                db.session.add(new_value)
            db.session.commit()


    def delete(self, v_id):
        #delete a volumne
        vol = Volumne.query.get(v_id)
        if vol is None:
            abort(403, message='volumne id:{} not exist'.format(vol))
        doc = Doc.query.filter_by(volumne_id=v_id).first()
        if doc is not None:
            abort(403, message='volumne:{} has doc:{}'.format(vol.name, doc.name))

        db.session.delete(vol)
        db.session.commit()
        return '', 204


