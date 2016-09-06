#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: session.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/07 00:10:33
"""

import time
import threading
import thread

#TODO
SESSION_LIFE = 15 * 60 #15min
def make_token(name, timestamp):
    return '%s|%.2f' % (name, timestamp)

class UserInfo(object):
    def __init__(self, name, timestamp):
        self.name = name
        self.timestamp = timestamp
        self.token = make_token(name, timestamp)

class Session(object):
    def __init__(self):
        self.clear_mutex = threading.Lock()
        self.users = {}
    def init(self):
        thread.start_new_thread(self.clear_invalid_user_thread, ())
    def add_user(self, name):
        timestamp = time.time()
        user = UserInfo(name, timestamp)
        if user.token not in self.users:
            self.users[user.token] = user
            return user.token
        else:
            print "unreachable branch for session add user"
            return None

    def valid_login_user(self, token):
        if token in self.users:
            now = time.time()
            if (now - self.users[token].timestamp) >= SESSION_LIFE:
                return False
            else:
                return True
        return False

    def clear_invalid_user_thread(self):
        while True:
            self.clear_mutex.acquire()
            invalid_users = []
            now = time.time()
            for token, user in self.users.iteritems():
                if (now - self.users[token].timestamp) >= SESSION_LIFE:
                   invalid_users.append(token)
            for token in invalid_users:
                self.users.pop(token)
            self.clear_mutex.release()
            print "clear invalid_user:%s" % invalid_users
            time.sleep(30)
            print "clear invalid_user, sleep 30s done"
        
