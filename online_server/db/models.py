from db.myorm import Mymetaclass, Field


# create table 表名 (字段 数据类型+长度 约束条件);
class User(metaclass=Mymetaclass):
    uid = Field('uid', 'int', None, True, True)
    name = Field('name', 'char(16)')
    password = Field('password', 'char(16)')
    vip = Field('vip', 'tinyint')
    locked = Field('locked', 'tinyint')
    identity = Field('identity', 'tinyint')

    def __init__(self, name, password, vip=0, locked=0, identity=0):
        '''
        :param name: 用户名
        :param password: 密码
        :param vip: 0为未开通vip
        :param locked: 0 未锁定,1 锁定
        :param identity: 0 用户 1管理员
        '''
        self.name = name
        self.password = password
        self.vip = vip
        self.locked = locked
        self.identity = identity


class Movie(metaclass=Mymetaclass):
    mid = Field('mid', 'int', None, True, True)
    name = Field('name', 'char(20)')
    author = Field('author', 'char(10)')
    md5 = Field('md5', 'char(32)')
    size = Field('size', 'char(10)')
    isvip = Field('isvip', 'int')
    path = Field('path', 'varchar(100)')

    def __init__(self, name, author, size, path, md5, isvip=0):
        self.name = name
        self.author = author
        self.size = size
        self.path = path
        self.md5 = md5
        self.isvip = isvip



class Announcement(metaclass=Mymetaclass):
    id = Field('id', 'int', None, True, True)
    title = Field('title', 'varchar(50)')
    content = Field('content', 'varchar(1000)')
    publisher_id = Field('publisher_id', 'tinyint')
    time = Field('time', 'timestamp')

    def __init__(self, title, content, publisher_id):
        '''

        :param title: 公告标题
        :param content: 公告内容
        :param publisher_id: 发布者id
        '''
        self.title = title
        self.content = content
        self.publisher_id = publisher_id


class Download_history(metaclass=Mymetaclass):
    id = Field('id', 'int', None, True, True)
    uid = Field('uid', 'int')
    mname = Field('mname', 'char(50)')
    time = Field('time', 'timestamp')

    def __init__(self, uid, mname):
        self.uid = uid
        self.mname = mname
