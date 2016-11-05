#!/usr/bin/python
#coding=utf-8
import re
import zipfile
import sys
import os
import datetime
import shutil

def secure_filename(file_name):
    secure_name = re.sub('[" \-~\|\-/]', '_', file_name)
    return secure_name

def parse_volumne_meta(meta_path):
    k_v = []
    with open(meta_path, 'r') as fh:
        lines = fh.readlines()
        keys = None
        values = None
        if len(lines) > 0:
            keys = lines[0].decode('gbk').strip('\r\n').split('\t')
        if len(lines) > 1:
            values = lines[1].decode('gbk').strip('\r\n').split('\t')
        
        for index, key in enumerate(keys):
            if values is not None and len(values) > index:
                k_v.append((key, values[index]))
            else:
                k_v.append((key, None))

    return True, k_v

def parse_doc_meta(meta_path):
    docs = []
    with open(meta_path, 'r') as fh:
        line_1 = fh.readline()
        keys = line_1.decode('gbk').strip('\r\n').split('\t')
        for line in fh:
            doc_meta = []
            one_doc_meta = line.decode('gbk').strip('\r\n').split('\t')
            for index, key in enumerate(keys):
                if len(one_doc_meta) > index:
                    doc_meta.append((key, one_doc_meta[index]))
                else:
                    doc_meta.append((key, None))
            docs.append(doc_meta)

    return True, docs
 
