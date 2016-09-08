# python-api
for a simple RESTful to mysql

##Usage:
```bash
    mysql -uxxx -p
    
    drop database test_oa; create database test_oa;
    
    python ./init_db.py 
    python ./run.py
    
    ip:port 127.0.0.1:8080
```

##Features
all need #username# as parameter
+ /docclass
    + /add docclass
        + parameter: action:add, name:docclass_name, parent_id:parent_docclass_id, customizable: whether_customizable(TODO)
    + /del docclass
        + parameter: action:del, docclass_id: to delete docclass's id
    + /mode docclass
        + parameters: action:mod, docclass_id, new_parent_id or new_name
    + /get docclass
        + parameters: action:get_all 
    + /get docs
        + parameters: action:get_docs, docclass_id
+ /doc
    + action:upload, 'file' : mime-file, docclass_id:
    + action:get_doc(means download), file_id: file id
    + action:get_info, file_id:
    + action:del, file_id:
+ /user
    + action:add, username:username, password:password, create_user:create_user_name
    + action:del, username:username
    + action:get, username:username
+ /borrow
    + action:get_all, username:root
    + action:get, username (if root, must provide to to_username)
    + action:add, username:root, to_username:, doc_id_list, docclass_id_list, start_time(optional), end_time (%Y%m%d%H%M%S)
    + action:del, auth_id:
+ /login
    + /parameters: username, password, return a token
+ /is_login
    + /parameters: token: 
##TODO
+ doc类方法
    + 上传
    + 下载（请求文件）
    + 文件列表的获得
+ log类方法
    + log浏览
    + log插入
+ 某id有权限的文件列表
+ 新增删除某id某文件某段时间内的权限
    + 访问时发现过期再删除
+ token访问权限控制及过期逻辑
