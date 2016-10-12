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
修改需要登录并且用户是root用户（HTTP BASIC AUTH，在包头中）
+ /docclass
    + /add docclass
        /docclass POST, name, parent_id, properties（volumne的属性名，多个值，properties=xxx&properties=yyy), type(=0, old, 1, new)
        example:curl -u root:password http://127.0.0.1:8080/docclass -d 'name=level4&parent_id=11&type=1&properties=名字&properties=时间'
    + /del docclass
        /docclass/<doc_id> DELETE
        example: curl -u root:password http://127.0.0.1:8080/doclcass -X DELETE
    + /mode docclass
        /docclass/<doc_id> PUT, name, type
        example: curl -u root:password http://127.0.0.1:8080/docclass/<doc_id> -X PUT -d 'name=newname&type=nametype'
    + /get docclass
        + /docclass GET (get all docclass)
        + /docclass/<doc_id> GET (get one docclass)
        example: curl http://127.0.0.1:8080/docclass/<doc_id>
+ /volumne
    + add volumne
        + /volumne POST, name, docclass_id, doc_properties（包含的doc需要具备的属性名，多个值），values（对应docclass的properties)
        +example: curl -u root:password http://127.0.0.1:8080/volumne -d 'name=vol1&doclass_id=6&doc_properties=时间&docproperties=地点&values=prop1=val1&values=prop2=val2&values=prop3=val3'
    + delete/put/get just as docclass
+ /doc
    +as volumne and docclass, parameters see file:resource/doc.py
       
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
