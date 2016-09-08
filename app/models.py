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

from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(128))
    createid = db.Column(db.Integer, db.ForeignKey('user.id'))

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

class DocClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    parent_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    customizable = db.Column(db.Boolean)
    docs = db.relationship('Doc', backref=db.backref('docclass', lazy='joined'), lazy='dynamic')

    def __init__(self, name, parent_id, customizable):
        self.name = name
        self.parent_id = parent_id
        self.customizable = customizable
    
    def __repr__(self):
        return '<DocClass %r, %d>' % (self.name, self.parent_id)
    
    def to_json(self):
        return {'id' : self.id,
                'name' : self.name,
                'parent_id' : self.parent_id,
                'customizable' : self.customizable
                }

class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    docclass_id = db.Column(db.Integer, db.ForeignKey('doc_class.id'))
    path = db.Column(db.String(1024))
    md5 = db.Column(db.String(64))
    file_type = db.Column(db.String(32))
    content = db.Column(db.PickleType)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_time = db.Column(db.DateTime)

    def __init__(self, name, docclass_id, path, file_type, content, author_id, upload_time):
        self.name = name
        self.docclass_id = docclass_id
        self.path = path
        self.file_type = file_type
        self.content = content
        self.author_id = author_id
        self.upload_time = upload_time

    def __repr__(self):
        return '<Doc %s, %d, %s>' % (self.name, self.author_id, self.file_type)

    def to_json(self):
        return {'id' : self.id,
                'name' : self.name,
                'docclass_id' : self.docclass_id,
                'file_type' : self.file_type,
                'content' : self.content,
                'author_id' : self.author_id
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

def init_db():
    db.drop_all()
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
    depart = DocClass(u'你好', 1, True)
    db.session.add(depart)

    db.session.commit()

    users = User.query.all()
    print users[0].id

    print users
    classs = DocClass.query.all()
    print classs
if __name__ == '__main__':
    pass
