import pymysql

import conf.settings


class Mymetaclass(type):
    _instance = None

    def __init__(cls, class_name, bases, dic):
        super(Mymetaclass, cls).__init__(class_name, bases, dic)
        columns = []
        for k, v in dic.items():
            if isinstance(v, Field):
                column = '%s %s' % (v.name, v.column_type)
                if v.primary_key:
                    column += ' primary key'
                    cls.pri_key = v.name
                if v.auto_increment:
                    column += ' auto_increment'
                if v.default != None:
                    column += " default '%s'" % v.default
                columns.append(column)
        columns = ','.join(columns)
        conn = Connection()
        sql = "create table %s (%s)" % (cls.__name__, columns)
        conn.execute(sql)


class Field:
    def __init__(self, name, column_type, default=None, primary_key=False, auto_increment=False):
        self.name = name
        self.column_type = column_type
        self.default = default
        self.primary_key = primary_key
        self.auto_increment = auto_increment


class OldDBSingle(type):
    instance = None

    def __call__(cls, *args, **kwargs):
        if OldDBSingle.instance == None:
            obj = object.__new__(cls)
            obj.__init__(*args, **kwargs)
            OldDBSingle.instance = obj
        return OldDBSingle.instance


class Dbhandler(metaclass=OldDBSingle):

    def __init__(self):
        self.conn = Connection()

    def save(self, obj):
        column = []
        values = []
        for k, v in obj.__dict__.items():
            column.append(k)
            values.append(v)
        lis = ["%s" for k in obj.__dict__]
        column = ','.join(column)
        lis = ','.join(lis)
        # sql = "insert into %s(%s) values(%s)"   % (obj.__class__.__name__, column, lis)
        res = self.conn.execute("insert into %s(%s) values(%s)" % (obj.__class__.__name__, column, lis), values)
        return res

    def delete(self, obj):
        sql = 'delete from %s where %s = %s' % (
            obj.__class__.__name__, obj.__class__.pri_key, getattr(obj, obj.__class__.pri_key))
        res = self.conn.execute(sql)

        return res

    def update(self, obj):
        lis = [k + '=%s' for k in obj.__dict__]
        values = [v for k, v in obj.__dict__.items()]
        lis = ','.join(lis)
        sql = "update %s set %s where %s =%s" % (
            obj.__class__.__name__, lis, obj.__class__.pri_key, getattr(obj, obj.__class__.pri_key))
        res = self.conn.execute(sql, values)
        return res

    def get(self, cls, id):
        sql = 'select * from %s where %s = %s' % (cls.__name__, cls.pri_key, id)
        print(sql)
        res = self.conn.execute(sql, is_selected=True)
        dic = res[0]
        obj = object.__new__(cls)
        for k, v in dic.items():
            setattr(obj, k, v)
        return obj

    def select_many(self, cls, condition, limit=None):
        sql = 'select * from %s where %s' % (cls.__name__, condition)
        if limit:
            sql += ' limit %s,%s' % (limit[0], limit[1])
        lis = self.conn.execute(sql, is_selected=True)
        obj_lis = []
        for dic in lis:
            obj = object.__new__(cls)
            obj.__dict__ = dic
            obj_lis.append(obj)
        return obj_lis


class ConnectionSingerton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not ConnectionSingerton._instance:
            obj = object.__new__(cls)
            obj.__init__(*args, **kwargs)
            ConnectionSingerton._instance = obj
        return ConnectionSingerton._instance


class Connection(metaclass=ConnectionSingerton):
    user = conf.settings.user
    password = conf.settings.password
    database = conf.settings.database
    charset = conf.settings.charset
    autocommit = conf.settings.autocommit
    max_pool_count = conf.settings.max_pool_count
    current_pool = 0

    def __init__(self):
        self.pool = []
        for i in range(3):
            conn = self.create_connect()
            self.pool.append(conn)

    def create_connect(self):
        self.current_pool += 1
        return pymysql.connect(
            ip="127.0.0.1",
			port="3306",
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            autocommit=self.autocommit)

    def get_conn(self):
        while True:
            if not self.pool:
                if self.current_pool < self.max_pool_count:
                    self.pool.append(self.create_connect())
                    continue
                continue
            return self.pool.pop()

    def execute(self, sql, condition=None, is_selected=False):
        conn = self.get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        # if not condition:
        affect_rows = 0
        try:
            affect_rows = cursor.execute(sql, condition)
        except Exception as e:
            print(e)
        self.pool.append(conn)
        if is_selected:
            return cursor.fetchall()
        return affect_rows
