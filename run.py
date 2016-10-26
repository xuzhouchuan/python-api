#!/usr/bin/python
#coding=utf-8
"""
File: run.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2016/09/04 21:33:27
"""

from app import app


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8002, debug = True, threaded=True)
