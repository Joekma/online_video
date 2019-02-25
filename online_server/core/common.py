from db.models import User
from db.myorm import Dbhandler

dbhandler = Dbhandler()


def register(request):
    if not dbhandler.select_many(User, 'name=%r and identity=%s' % (request['name'], request['identity'])):
        dbhandler.save(User(request['name'], request['password'], identity=request['identity']))
        return {'status': 'ok', 'msg': '注册成功!'}
    return {'status': 'error', 'msg': '该用户名已存在!'}


def login(request):
    obj = dbhandler.select_many(User, 'name=%r and password=%r and identity=%s' % (
        request['name'], request['password'], request['identity']))
    if obj:
        if obj[0].locked == 1:
            return {'status': 'error', 'msg': '该用户已被锁定!'}
        return {'status': 'ok', 'msg': '登陆成功!', 'user': obj[0].__dict__}
    return {'status': 'error', 'msg': '用户名或密码错误!'}
