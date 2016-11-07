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
from flask_restful import Resource, reqparse, abort
import copy
import json
from flask import jsonify, g
from app import db, auth
from app.models import DocClass, Volumne, VolumneProperty

class DocClassListResource(Resource):
    def __init__(self):
        pass
    
    def get(self):
        #get all doc class
        result = []
        doc_clazzes = DocClass.query.all()
        if doc_clazzes is not None:
            for item in doc_clazzes:
                result.append(item.to_json())
        return jsonify({'docclass' : result})

    @auth.login_required
    def post(self):
        #add a docclass
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name', required=True)
        parser.add_argument('parent_id', type=int, required=True)
        parser.add_argument('properties', action='append', default=[])
        parser.add_argument('type', type=int)
        args = parser.parse_args()

        if g.user.id != 1:
            abort(403, message='not admin')

        #find parent docclass
        parent = DocClass.query.get(args['parent_id']) 
        if parent is None:
            abort(400, message=u"has no parent docclass:{}".format(args['parent_id']))
        #if parent.level + 1 == 4:
            #leaf node, has properties and type
        #    if args.get('properties', None) is None or args.get('type', None) is None:
        #        abort(400, message="leaf docclass, but has not properties or type")
        maybe_exist = DocClass.query.filter_by(parent_id=args['parent_id'], name=args['name']).first()
        if maybe_exist is not None:
            abort(400, message=u'docclass:{} already has a same name child:{}'.format(parent.name, args['name']))
        new_docclass = DocClass(args['name'], args['parent_id'], parent.level + 1,
                args.get('type', None))
        db.session.add(new_docclass)
        db.session.commit()
        #leaf docclass, add property 
        #if new_docclass.level == 4:
        order = 0
        for prop in args['properties']:
            print prop
            new_prop = VolumneProperty(prop, new_docclass.id, order)
            order += 1
            db.session.add(new_prop)
        db.session.commit()

        return new_docclass.to_json(), 201


class DocClassResource(Resource):
    def __init__(self):
        pass

    def get(self, dclass_id):
        #get one docclass
        docclass = DocClass.query.get(dclass_id)
        if docclass is None:
            abort(404, message='docclass {} not exist'.format(dclass_id))

        result = docclass.to_json()
        result['properties'] = []
        result['volumnes'] = []
        props = [p for p in docclass.properties]
        vols = [v for v in docclass.volumnes]
        props.sort(key=lambda e:e.order)
        #properties and volumnes
        for p in props:
            result['properties'].append(p.to_json())
        for v in vols:
            result['volumnes'].append(v.to_json())

        return result, 200
    
    @auth.login_required
    def put(self, dclass_id):
        #modify doc class(cn't modify  properties)
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('name')
        parser.add_argument('type', type=int)
        args = parser.parse_args()

        if g.user.id != 1:
            abort(403, message='not admin')

        doc_clazz = DocClass.query.get(dclass_id)
        if doc_clazz is None:
            abort(404, message='doc class {} not exist'.format(dclass_id))
        if args.get('name', None) is None and args.get('type', None) is None:
            abort(403, message='has no new name or new type parameter')
        if args.get('type', None) is not None and doc_clazz.level != 4:
            abort(403, message='not leaf doc class, cant change type')
        if args.get('name', None) is not None:
            doc_clazz.name = args.get('name', None)
        if args.get('type', None) is not None:
            doc_clazz.type = args.get('type', None)

        db.session.commit()
        return doc_clazz.to_json(), 200

    @auth.login_required
    def delete(self, dclass_id):
        if g.user.id != 1:
            abort(403, message='not admin')
        #delete docclass
        docclass = DocClass.query.get(dclass_id)
        if docclass is None:
            abort(404, message='doc class {} not exist'.format(dclass_id))

        child = DocClass.query.filter_by(parent_id=dclass_id).first()
        if child is not None:
            abort(403, message='doc class {} has child {}'.format(dclass_id, child.name))
        
        db.session.delete(docclass)
        db.session.commit()
        return '', 204






