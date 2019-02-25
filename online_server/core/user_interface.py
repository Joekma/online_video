from db.models import User, Movie, Download_history, Announcement
from db.myorm import Dbhandler

dbhandler = Dbhandler()


def open_member(request):
    obj = dbhandler.select_many(User, 'name=%r' % request['name'])[0]
    print(obj)
    if obj.vip == 1:
        return {'status': 'error', 'msg': '已经开通会员了!'}
    obj.vip = 1
    dbhandler.update(obj)
    return {'status': 'ok', 'msg': '开通会员成功!'}


def show_video(request):
    res = dbhandler.select_many(Movie, '1=1')
    lis = [[obj.name, obj.size, obj.author, obj.isvip] for obj in res]
    return {'movie': lis}


def download_video(request):
    lis = dbhandler.select_many(Movie, 'name=%r' % request['name'])
    obj = lis[0]
    h = Download_history(request['uid'], request['name'])
    dbhandler.save(h)
    return {'file_name': obj.name, 'file_path': obj.path, 'file_size': obj.size, 'download': True}


def download_history(request):
    res = dbhandler.select_many(Download_history, 'uid = %s' % request['uid'])
    lis = [[obj.mname, str(obj.time)] for obj in res]
    response = {'history': lis}
    return response


def view_announcement(request):
    res = dbhandler.select_many(Announcement, '1=1')
    lis = [[obj.title, obj.content, str(obj.time)] for obj in res]

    if not res:
        return {'status':'error','msg':'当前无公告!'}
    return {'status':'ok','msg':lis}
