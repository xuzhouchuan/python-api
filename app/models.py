#!/usr/bin/env python
#-*- coding:utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: models.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/07 13:26:06
"""

from passlib.apps import custom_app_context as pwd_context
from app import db, app
from datetime import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer 
                          as Serializer, BadSignature, SignatureExpired)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    createid = db.Column(db.Integer, db.ForeignKey('user.id'))

    #__table_args__ = {'mysql_engine':'InnoDB'}

    def __init__(self, username, password, createid):
        self.username = username
        self.password = password
        self.createid = createid

    def __repr__(self):
        return '<User %s, create_by:%d>' % (self.username, self.createid)

    def to_json(self):
        return {'id' : self.id,
                'name' : self.username,
                'create_user_id' : self.createid
               }
    def verify_password(self, password):
        return password == self.password

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id' : self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

#门类，树状层级目录
class DocClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    parent_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    #docclass，是Volumne对象的一个属性，可以通过Volumne.docclass来获取这个volumne的docclass了
    volumnes = db.relationship('Volumne', backref=db.backref('docclass', lazy='joined'), lazy='dynamic')
    properties = db.relationship('VolumneProperty', cascade="all,delete", backref=db.backref('docclass', lazy='joined'), lazy='dynamic')
    level = db.Column(db.Integer)
    #0:旧的形式；1:新的形式，卷是不存在的，为了 统一形式加了这一层
    type = db.Column(db.Integer)

    #__table_args__ = (db.UniqueConstraint('parent_id', 'name', name='_parent_id_name_uc'), {'mysql_engine': 'InnoDB'})

    def __init__(self, name, parent_id, level, type):
        self.name = name
        self.parent_id = parent_id
        self.level = level
        self.type = type
    
    def __repr__(self):
        return '<DocClass %r, %d>' % (self.name, self.parent_id)
    
    def to_json(self):
        return {'id' : self.id,
                'name' : self.name,
                'parent_id' : self.parent_id,
                'level' : self.level,
                'type' : self.type
                }

#卷
class Volumne(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512))
    docclass_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    #0:旧的形式；1:新的形式，卷是不存在的，为了 统一形式加了这一层
    type = db.Column(db.Integer, default=0)
    #volumne成了Doc的一个属性
    docs = db.relationship('Doc', backref=db.backref('volumne', lazy='joined'), lazy='dynamic')
    values = db.relationship('VolumneValue', cascade="all,delete", backref=db.backref('volumne', lazy='joined'), lazy='dynamic')
    properties = db.relationship('DocProperty', cascade="all,delete", backref=db.backref('volumne', lazy='joined'), lazy='dynamic')

    #__table_args__ = (db.UniqueConstraint('docclass_id', 'name', name='_docclass_id_name_uc'),{'mysql_engine': 'InnoDB'})

    def __init__(self, name, docclass_id, type=0):
        self.name = name
        self.docclass_id = docclass_id
        self.type = type

    def to_json(self):
        return {'id' : self.id,
                'name' : self.name,
                'docclass_id' : self.docclass_id,
                'type' : self.type
               }

#件
class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512))
    volumne_id = db.Column(db.Integer, db.ForeignKey('volumne.id'))
    path = db.Column(db.String(2048))
    #type意义和Volumne中的type一样，只是冗余存储
    type = db.Column(db.Integer, default=0)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_time = db.Column(db.DateTime)
    values = db.relationship('DocValue', cascade="all,delete", backref=db.backref('doc', lazy='joined'), lazy='dynamic')

    #__table_args__ = (db.UniqueConstraint('volumne_id', 'name', name='_volumne_id_name_uc'), {'mysql_engine': 'InnoDB'})

    def __init__(self, name, volumne_id, path, type, uploader_id, upload_time):
        self.name = name
        self.volumne_id = volumne_id
        self.path = path
        self.type = type
        self.uploader_id = uploader_id
        self.upload_time = upload_time

    def __repr__(self):
        return '<Doc %s, %d, %d>' % (self.name, self.id, self.volumne_id)

    def to_json(self):
        return {'id' : self.id,
                'name' : self.name,
                'volumne_id' : self.volumne_id,
                'volume' : self.volumne.name,
                'path' : self.path,
                'uploader' : self.uploader_id,
                'upload_time' : self.upload_time.strftime('%Y%m%d %H:%M:%S')
               }

class VolumneProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    docclass_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    order = db.Column(db.Integer)

    #__table_args__ = {'mysql_engine':'InnoDB'}

    def __init__(self, name, docclass_id, order):
        self.name = name
        self.docclass_id = docclass_id
        self.order = order

    def to_json(self):
        return {'id': self.id,
                'name': self.name,
                'docclass_id': self.docclass_id,
                'order': self.order
               }

class DocProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    volumne_id = db.Column(db.Integer, db.ForeignKey('volumne.id'))
    order = db.Column(db.Integer)

    #__table_args__ = {'mysql_engine':'InnoDB'}

    def __init__(self, name, volumne_id, order):
        self.name = name
        self.volumne_id = volumne_id
        self.order = order

    def to_json(self):
        return {'id': self.id,
                'name': self.name,
                'volumne_id': self.volumne_id,
                'order': self.order
               }

class VolumneValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(1024))
    property_id = db.Column(db.Integer, db.ForeignKey('volumne_property.id'))
    volumne_id = db.Column(db.Integer, db.ForeignKey('volumne.id'))
    property_name = db.Column(db.String(1024))
    order = db.Column(db.Integer)

    #__table_args__ = {'mysql_engine':'InnoDB'}

    def __init__(self, value, property_id, volumne_id, property_name, order):
        self.value= value
        self.property_id = property_id
        self.volumne_id = volumne_id
        self.property_name = property_name
        self.order = order

    def to_json(self):
        return {'id' : self.id,
                'property_name': self.property_name,
                'property_id': self.property_id,
                'value': self.value,
                'volumne_id': self.volumne_id,
                'order': self.order
               }


class DocValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(1024))
    property_id = db.Column(db.Integer, db.ForeignKey('doc_property.id'))
    doc_id = db.Column(db.Integer, db.ForeignKey('doc.id'))
    property_name = db.Column(db.String(1024))
    order = db.Column(db.Integer)

    #__table_args__ = {'mysql_engine':'InnoDB'}

    def __init__(self, value, property_id, doc_id, property_name, order):
        self.value= value
        self.property_id = property_id
        self.doc_id = doc_id
        self.property_name = property_name
        self.order = order
    
    def to_json(self):
        return {'id': self.id,
                'value' : self.value,
                'property_id': self.property_id,
                'property_name': self.property_name,
                'order': self.order,
                'doc_id': self.doc_id
               }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    optime = db.Column(db.DateTime)
    optype = db.Column(db.String(128))
    opinfo = db.Column(db.String(1024))
    exinfo = db.Column(db.String(1024))

    def __init__(self, user_id, optime, optype, opinfo, exinfo):
        self.user_id = user_id
        self.optime = optime
        self.optype = optype
        self.opinfo = opinfo
        self.exinfo = exinfo

    def __repr__(self):
        return '<Log %s %s %s>' % (self.user_id, self.optime, self.optye)

    def to_json(self):
        return {'user_id' : self.user_id,
                'optime' : self.optime,
                'optype' : self.optype,
                'opinfo' : self.opinfo,
                'exinfo' : self.exinfo
                }

class BorrowAuthority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doc_id = db.Column(db.Integer, db.ForeignKey('doc.id'))
    docclass_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __init__(self, user_id, doc_id, docclass_id, start_time, end_time):
        self.user_id = user_id
        self.doc_id = doc_id
        self.docclass_id = docclass_id
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        if self.docclass_id is not None:
            return '<Authority %d docclass:%d %s %s>' % (self.user_id, self.docclass_id, self.start_time, self.end_time)
        elif self.doc_id is not None:
            return '<Authority %d doc:%d %s %s>' % (self.user_id, self.doc_id, self.start_time, self.end_time)

    def to_json(self):
        return {'id' : self.id,
                'user_id' : self.user_id,
                'doc_id' : self.doc_id,
                'docclass_id' : self.docclass_id,
                'start_time' : self.start_time,
                'end_time' : self.end_time
               }

class ApplyFor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doc_id = db.Column(db.Integer, db.ForeignKey('doc.id'))
    docclass_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    passed = db.Column(db.Boolean)

    def __init__(self, user_id, doc_id, docclass_id, start_time, end_time):
        self.user_id = user_id
        self.doc_id = doc_id
        self.docclass_id = docclass_id
        self.start_time = start_time
        self.end_time = end_time
        self.passed = False

    def __repr__(self):
        if self.docclass_id is not None:
            return '<ApplyFor %d docclass:%d %s %s>' % (self.user_id, self.docclass_id, self.start_time, self.end_time)
        elif self.doc_id is not None:
            return '<ApplyFor %d doc:%d %s %s>' % (self.user_id, self.doc_id, self.start_time, self.end_time)

    def to_json(self):
        return {'id' : self.id,
                'user_id' : self.user_id,
                'doc_id' : self.doc_id,
                'docclass_id' : self.docclass_id,
                'start_time' : self.start_time,
                'end_time' : self.end_time,
                'passed' : self.passed
               }

def init_db():
    db.create_all()
    db.session.commit()
    table_names = []
    for clazz in db.Model._decl_class_registry.values():
        try:
            table_names.append(clazz.__tablename__)
        except:
            pass
    #set utf8 or not work well
    for table in table_names:
        db.engine.execute("alter table %s convert to character set utf8" % table)
    print table_names
    admin = User('root', 'root', 1)
    test = User('test', 'test', 1)
    db.session.add(admin)
    db.session.add(test)
    if True:
        name = ['root', u'最高检', u'办公厅', u'检察长办公室', u'秘书处', u'人大代表联络处', u'新规则文书档案', u'老规则文书档案']
        parent = [1, 1, 2, 3, 3, 3, 4, 4]
        level = [0, 1, 2, 3, 3, 3, 4, 4]
        type = [None, None, None, None, None, None, 0, 1]
        for i in range(0, len(name)):
            dep = DocClass(name[i], parent[i], level[i], type[i])
            db.session.add(dep)
            db.session.commit()
    else:
        depart = DocClass(u'你好', 1, True)
        db.session.add(depart)
        db.session.commit()

    users = User.query.all()
    print users[0].id

    if True:
        for i in range(13):
            log = Log(1, datetime.now(), "null", "null", "null")
            db.session.add(log)
            db.session.commit()

    print users
    classs = DocClass.query.all()
    print classs

def drop_db():
    db.drop_all()

if __name__ == '__main__':
    pass
