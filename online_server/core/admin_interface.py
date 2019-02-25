import os

from db.models import Announcement
from db.models import User, Movie
from db.myorm import Dbhandler

handler = Dbhandler()

error = {'status': 'error', 'msg': 'unknown error'}


def announce(request):
    title = request['title']
    content = request['content']
    publisher_id = request['publisher_id']
    obj = Announcement(title, content, publisher_id)
    res = handler.save(obj)
    if not res:
        return error
    return {'status': 'ok', 'msg': '成功发布公告!'}


def lock_account(request):
    if request['task'] == 'get_account':
        res = handler.select_many(User, 'locked=0')
        lis = [obj.name for obj in res]
        response = {'user': lis}
        return response
    else:
        lis = handler.select_many(User, 'name=%r and identity=0' % request['name'])
        obj = lis[0]
        obj.locked = 1
        res = handler.update(obj)
        if not res:
            return error
        return {'status': 'ok', 'msg': '锁定用户成功!'}


def unlock_account(request):
    if request['task'] == 'get_account':
        res = handler.select_many(User, 'locked=1')
        lis = [obj.__dict__['name'] for obj in res]
        response = {'user': lis}
        return response
    else:
        lis = handler.select_many(User, 'name=%r and identity=0' % request['name'])
        obj = lis[0]
        obj.locked = 0
        res = handler.update(obj)
        if not res:
            return error
        return {'status': 'ok', 'msg': '解锁用户成功!'}


def upload_video(request, path=None):
    if not path:
        if handler.select_many(Movie, 'md5=%r' % request['md5']):
            return {'status': 'error', 'msg': '该电影已存在！'}
        return {'status': 'ok', 'msg': '开始接收视频'}
    if not request:
        return error
    obj = Movie(request['name'], request['author'], request['size'], path, request['md5'], isvip=request['isvip'])
    handler.save(obj)
    return {'status': 'ok', 'msg': '上传视频成功！'}


def delete_video(request):
    if request['task'] == 'get_movie':
        res = handler.select_many(Movie, '1=1')
        lis = [obj.__dict__['name'] for obj in res]
        response = {'movie': lis}
        return response
    else:
        lis = handler.select_many(Movie, 'name=%r' % request['name'])
        obj = lis[0]
        os.remove(obj.path)
        res = handler.delete(obj)
        if not res:
            return error
        return {'status': 'ok', 'msg': '电影删除成功!'}
