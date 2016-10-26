#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: manage.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/10/13 10:47:44
"""

from flask_script import Manager, Server
from app import app
from app.models import *


print app
manager = Manager(app)

@manager.command
def drop():
    if prompt_bool("Are you sure you want to lose all your data"):
        drop_db()

@manager.command
def create():
    init_db()

@manager.command
def update_index():
    "update search index"
    reindex()

@manager.command
def hello():
    print "hello"


#manager.add_command("runserver", Server(host='0.0.0.0', port=8001))


if __name__ == "__main__":
    manager.run()
