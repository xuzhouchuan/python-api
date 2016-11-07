#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: main.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/04 21:37:13
"""
from flask import Flask, g, make_response
from flask_restful import Api, abort
from flaskext.mysql import MySQL
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask_whooshee import Whooshee
import MySQLdb.cursors
from functools import wraps
import os
import time
import datetime
import shutil
import zipfile
from util import secure_filename, parse_volumne_meta, parse_doc_meta
#from app.models import Log


app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'test_oa'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/test_oa?charset=utf8'
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['WHOOSHEE_WRITE_TIMEOUT'] = 3
app.config['WHOOSHEE_DIR'] = 'search-index'
app.config['WHOOSHEE_MIN_STRING_LEN'] = 1

api = Api(app)
mysql = MySQL(cursorclass=MySQLdb.cursors.DictCursor)
db = SQLAlchemy(app, use_native_unicode='utf8')
auth = HTTPBasicAuth()
whooshee = Whooshee(app)

mysql.init_app(app)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kw):
        print g.user.to_json()
        if g.user.id != 1:
            return make_response(jsonify({'message':'Unauthorized access'}), 200)
        return f(*args, **kw)
    return wrapper

from models import *
from resource import UserResource, DocClassResource, DocClassListResource, DocResource, ViewLog, ApplyForResource, VolumneResource, VolumneListResource, DocListResource, UserListResource, ApplyForListResource
api.add_resource(UserResource, '/user/<int:u_id>')
api.add_resource(UserListResource, '/user')
api.add_resource(DocClassResource, '/docclass/<int:dclass_id>')
api.add_resource(DocClassListResource, '/docclass')
api.add_resource(VolumneResource, '/volumne/<int:v_id>')
api.add_resource(VolumneListResource, '/volumne')
api.add_resource(DocResource, '/doc/<int:d_id>')
api.add_resource(ApplyForResource, '/apply/<int:a_id>')
api.add_resource(ApplyForListResource, '/apply')
api.add_resource(DocListResource, '/doc')
api.add_resource(ViewLog, '/viewlog')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/add_user', methods=['POST'])
@auth.login_required
def new_user():
    if g.user.id != 1:
        return 'not root user, cant add user', 403
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return 'username:{}, passowrd:{}'.format(username, password), 400    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return 'user:{} already exist'.format(username), 400    # existing user
    user = User(username, password, 1)
    #user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    log_info = u'{} 添加用户 user_id:{}, user_name:{}'.format(g.user.username,
            user.id, user.username)
    Log.logging(g.user.id, datetime.datetime.now(), 'add-user', log_info)
    return jsonify(user.to_json())

@app.route('/api/token', methods=['POST', 'GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    Log.logging(g.user.id, datetime.datetime.now(), 'login', u'{} 登录'.format(g.user.username))
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.route('/api/auth/list', methods=['POST', 'GET'])
@auth.login_required
def list_authority():
    if g.user.id != 1:
        return 'not root user, cant apply authority', 403

    result = {'authorities' : [], 'applyfors' : []}
    auths = BorrowAuthority.query.all()
    for a in auths:
        result['authorities'].append(a.to_json())
    result['authorities'].sort(key=lambda e:e['id'], reverse=True)
    applys = ApplyFor.query.all()
    for apl in applys:
        result['applyfors'].append(apl.to_json())
    result['applyfors'].sort(key=lambda e:e['id'], reverse=True)
    return jsonify(result), 200

@app.route('/api/auth/authorize', methods=['GET']) 
@auth.login_required
def apply_authority():
    if g.user.id != 1:
        return 'not root user, cant apply authority', 403
    
    apply_for_id = request.args.get('apply_for_id', None)
    action = request.args.get('action', None)
    if apply_for_id is None or action is None:
        return 'no apply for id or no action', 400
    apply_for = ApplyFor.query.get(apply_for_id)
    if apply_for is None:
        return 'no such a apply for, id is:{}'.format(apply_for_id), 400
    user_name = apply_for.user.username
    vol_name = apply_for.volumne.name
    if action == 'deny':
        apply_for.denied = True
        db.session.commit()
    elif action == 'accept':
        user_id = apply_for.user_id
        vol_id = apply_for.volumne_id
        start_t = apply_for.start_time
        end_t = apply_for.end_time
        #delete old BorrowAuthority
        for bo_au in BorrowAuthority.query.filter_by(user_id=user_id, volumne_id=vol_id):
            db.session.delete(bo_au)
        #insert in to BorrowAuthority
        borrow_auth = BorrowAuthority(user_id,
                vol_id,
                start_t,
                end_t)
        db.session.add(borrow_auth)
        #del in ApplyFor
        db.session.delete(apply_for)
        db.session.commit()

    log_info = u'{} 设置借阅权限:action:{} user:{} volumne:{}'.format(g.user.username,
            action, user_name, vol_name) 
    Log.logging(g.user.id, datetime.datetime.now(), 'authorize', log_info)
    return '', 204

@app.route('/api/search', methods=['GET'])
def search():
    word = request.args.get('w', None)
    if word is None:
        return 'no key word', 400
    result = {'volumnes':[], 'docs':[]}
    #volumne&value
    #order_by_relevance=-1, return all volumne , order by score
    #vols = Volumne.query.join(VolumneValue).whooshee_search(word, order_by_relevance=-1).all()
    #vols = Volumne.query.whooshee_search(word, whoosheer=VolumneVolumneValueWhoosheer).all()
    vols = Volumne.query.whooshee_search(word).all()
    for vol in vols:
        result['volumnes'].append(vol.to_json())
    #doc&value
    #docs = Doc.query.join(DocValue).whooshee_search(word, order_by_relevance=-1).all()

    #docs = Doc.query.whooshee_search(word, whoosheer=DocDocValueWhoosheer).all()
    docs = Doc.query.whooshee_search(word).all()
    for doc in docs:
        result['docs'].append(doc.to_json())
    return jsonify(result), 200

@app.route('/api/batch_volumne', methods=['POST'])
@auth.login_required
def batch_add_volumne():
    if g.user.id != 1:
        return 'not root user, cant add user', 403
    docclass_id_str = request.values.get('docclass_id', None)
    if docclass_id_str is None:
        return 'no docclass id', 400
    docclass_id = int(docclass_id_str)
    zip_file = request.files['zip_file']
    if zip_file.filename == '':
        return 'no zip file', 400
    docclass = DocClass.query.get(docclass_id)
    if docclass is None:
        return 'no such a docclass', 400
    type = docclass.type
    
    zip_filename = secure_filename(zip_file.filename)
    tmp_zip_filename = os.path.join("/tmp", datetime.datetime.now().strftime('%Y%m%d%H%M%S') + zip_filename)
    zip_file.save(tmp_zip_filename)
    zipfd = zipfile.ZipFile(tmp_zip_filename)
    output_zip_dir = os.path.join("/tmp", datetime.datetime.now().strftime('%Y%m%d%H%M%S') + zip_filename.encode('utf-8') + "_dir")
    if os.path.isdir(output_zip_dir):
       shutil.rmtree(output_zip_dir) 
    else:
        os.makedirs(output_zip_dir)
    zipfd.extractall(output_zip_dir)
    #for name in zipfd.namelist():
    #    name = name.decode('string-escape').decode('utf-8')
    #    zipfd.extract(name, output_zip_dir)
    zipfd.close()
    vol_dir_names = os.listdir(output_zip_dir)
    volumne_meta_filename = 'ImgArchiveH.Lst'
    doc_meta_filename = 'ImgArchive.Lst'
    first_time = True
    #one volumne
    for vol_name in vol_dir_names:
        vol_path = os.path.join(output_zip_dir, vol_name)
        volumne_meta_path = os.path.join(vol_path, volumne_meta_filename)
        doc_meta_path = os.path.join(vol_path, doc_meta_filename)
        if not os.path.isfile(volumne_meta_path) or not \
           os.path.isfile(doc_meta_path):
            #print "dir :%s has not meta file:%s\t%s" % (vol_name, volumne_meta_path, doc_meta_path)
            continue
        ret, vol_atts = parse_volumne_meta(volumne_meta_path)
        ret, docs_atts = parse_doc_meta(doc_meta_path)
        #old type
        if type == 0:
            if first_time:
                first_time = False
                #for old_prop in docclass.properties:
                #    db.session.delete(old_prop)
                #db.session.commit()
                vol_props = [x[0] for x in vol_atts]
                order = 0
                for vol_prop in vol_props:
                    old_vp = VolumneProperty.query.filter_by(name=vol_prop, docclass_id=docclass_id).first()
                    if old_vp is not None:
                        continue
                    new_vp = VolumneProperty(vol_prop, docclass_id, order)
                    order += 1
                    db.session.add(new_vp)
                db.session.commit()
            #add volumne and set volumne meta 
            value_str = u' '.join([x[1] for x in vol_atts if x[1] is not None])
            new_volumne = Volumne(vol_name.decode('utf-8'), docclass_id, type, value_str)
            db.session.add(new_volumne)
            db.session.commit()
            for k, v in vol_atts:
                vol_prop = VolumneProperty.query.filter_by(name=k, docclass_id=docclass_id).first()
                if vol_prop is None:
                    print "vol attr:%s not exist" % k
                    continue
                new_value = VolumneValue(v, vol_prop.id, new_volumne.id, vol_prop.name, vol_prop.order)
                db.session.add(new_value)
            db.session.commit()
            #add doc properties
            if len(docs_atts) == 0:
                continue
            doc_props = [x[0] for x in docs_atts[0]]
            order = 0
            for doc_prop in doc_props:
                new_doc_prop = DocProperty(doc_prop, new_volumne.id, order)
                order += 1
                db.session.add(new_doc_prop)
            db.session.commit()
            #add doc and set docs meta
            for doc_prop in docs_atts:
                doc_name = doc_prop[0][1]
                dot_index = doc_name.rfind('.')
                doc_path = doc_name
                if dot_index > 0:
                    doc_path = doc_name[:doc_name.rfind('.')]
                path = os.path.join('upload_document', secure_filename(new_volumne.name), secure_filename(doc_path))
                parent_path = os.path.join('upload_document', secure_filename(new_volumne.name))
                orig_path = os.path.join(vol_path, doc_path.encode('utf-8'))
                v_str = u' '.join([x[1] for x in doc_prop if x[1] is not None])
                new_doc = Doc(doc_path, new_volumne.id, path, type, 1, datetime.datetime.now(), v_str)
                db.session.add(new_doc)
                db.session.commit()
                for k, v in doc_prop:
                    doc_p = DocProperty.query.filter_by(name=k, volumne_id=new_volumne.id).first()
                    if doc_p is None:
                        continue
                    n_doc_v = DocValue(v, doc_p.id, new_doc.id, doc_p.name, doc_p.order)
                    db.session.add(n_doc_v)
                db.session.commit()
                if not os.path.isdir(parent_path):
                    os.makedirs(parent_path)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                print orig_path
                print parent_path
                shutil.move(orig_path, parent_path)
        #new type
        else:
            if len(docs_atts) == 0:
                continue
            props = [x[0] for x in docs_atts[0]]
            #volumne property to docclass
            if first_time:
                first_time = False
                #for old_prop in docclass.properties:
                #    db.session.delete(old_prop)
                #db.session.commit()
                order = 0
                for v_prop in props:
                    old_vp = VolumneProperty.query.filter_by(name=v_prop, docclass_id=docclass_id).first()
                    if old_vp is not None:
                        continue
                    new_vp = VolumneProperty(v_prop, docclass_id, order)
                    order += 1
                    db.session.add(new_vp)
                db.session.commit()
            for doc_info in docs_atts:
                vol_name = doc_info[0][1]
                vol_name = vol_name[:vol_name.rfind('.')]
                #add volumne and set volmne met
                value_str = u' '.join([x[1] for x in doc_info])
                new_vol = Volumne(vol_name, docclass_id, type, value_str)
                db.session.add(new_vol)
                db.session.commit()
                for k, v in doc_info:
                    vp = VolumneProperty.query.filter_by(name=k, docclass_id=docclass_id).first()
                    if vp is None:
                        print "vol attr:%s not exit" % k
                        continue
                    n_v = VolumneValue(v, vp.id, new_vol.id, vp.name, vp.order)
                    db.session.add(n_v)
                    #doc properties
                    n_doc_prop = DocProperty(k, new_vol.id, vp.order)
                    db.session.add(n_doc_prop)
                db.session.commit()
                #add doc
                doc_name = vol_name
                path = os.path.join('upload_document', secure_filename(vol_name), secure_filename(doc_name))
                parent_path = os.path.join('upload_document', secure_filename(vol_name))
                orig_path = os.path.join(vol_path, doc_name)
                n_doc = Doc(doc_name, new_vol.id, path, type, 1, datetime.datetime.now(), value_str)
                db.session.add(n_doc)
                db.session.commit()
                for k, v in doc_info:
                    vp = DocProperty.query.filter_by(name=k, volumne_id=new_vol.id).first()
                    if vp is None:
                        print "vol attr:%s not exit" % k
                        continue
                    n_v = DocValue(v, vp.id, n_doc.id, vp.name, vp.order)
                    db.session.add(n_v)
                db.session.commit()
                if not os.path.isdir(parent_path):
                    os.makedirs(parent_path)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                shutil.move(orig_path, parent_path)

    shutil.rmtree(output_zip_dir)
    os.remove(tmp_zip_filename)
    return 'OK', 200

