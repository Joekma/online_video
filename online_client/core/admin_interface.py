import hashlib
import os

import core.common
import core.common
from TCPclient.TCPclient import tcpclient

current_admin = None


def auth(func):
    def wrapper(*args, **kwargs):
        if not current_admin:
            print('请先登录!')
            login()
            res = func(*args, **kwargs)
            return res
        res = func(*args, **kwargs)
        return res

    return wrapper


def login(identity=1):
    core.common.login(identity)


def register(identity=1):
    core.common.register(identity)


@auth
def announce():
    while True:
        title = input('请输入公告标题:').strip()
        if not title:
            print('标题不能为空!')
            continue
        content = input('请输入内容:')
        if not content:
            print('内容不能为空!')
            continue
        request = {'interface': 'admin_interface', 'func': 'announce', 'title': title, 'content': content,
                   'publisher_id': current_admin['uid']}
        response = tcpclient(request)
        print(response['msg'])
        break


@auth
def lock_account():
    request = {'interface': 'admin_interface', 'func': 'lock_account', 'task': 'get_account'}
    response = tcpclient(request)
    if not response['user']:
        print('当前无可锁定用户!')
        return
    for user in response['user']:
        print(user)
    while True:
        name = input('请输出要锁定的用户名:')
        if name == 'q':
            return
        if name not in response['user']:
            print('输入的用户名不存在!')
            continue
        request = {'interface': 'admin_interface', 'func': 'lock_account', 'task': 'lock_account', 'name': name}
        response = tcpclient(request)
        print(response['msg'])
        break


@auth
def unlock_account():
    request = {'interface': 'admin_interface', 'func': 'unlock_account', 'task': 'get_account'}
    response = tcpclient(request)
    if not response['user']:
        print('当前无可解锁用户!')
        return
    for user in response['user']:
        print(user)
    while True:
        name = input('请输出要解锁的用户名:')
        if name == 'q':
            return
        if name not in response['user']:
            print('输入的用户名不存在!')
            continue
        request = {'interface': 'admin_interface', 'func': 'unlock_account', 'task': 'lock_account', 'name': name}
        response = tcpclient(request)
        print(response['msg'])
        break


@auth
def upload_video():
    while True:
        name = input('请输入电影名称:(q取消上传电影)')
        if name == 'q':
            return
        author = input('请输入作者:')
        isvip = input('是否为VIP观看?(y/n)')
        path = input('请输入电影路径:')
        path = r'%s' % path
        if not os.path.exists(path):
            print('输入路径不存在!')
            continue
        if not (name and author and isvip and path):
            print('输入不能为空!')
            continue
        isvip = 1 if isvip == 'y' else 0
        size = os.path.getsize(path)
        format_list = ['mp4', 'avi', 'rmvb', 'flv', 'mkv']
        format = path.split(os.path.sep)[-1].lower()
        for i in format_list:
            if not format.endswith(i):
                continue
            md5 = get_md5(path)
            request = {'interface': 'admin_interface', 'func': 'upload_video', 'name': name, 'author': author,
                       'size': size, 'isvip': isvip, 'path': path, 'md5': md5, 'isfile': False}
            res = tcpclient(request)
            if res['status'] == 'error':
                print(res['msg'])
                return
            request = {'interface': 'admin_interface', 'func': 'upload_video', 'name': name, 'author': author,
                       'size': size, 'isvip': isvip, 'from_path': path, 'md5': md5, 'isfile': True}
            res = tcpclient(request, is_upload=True)
            if res:
                print('\r%s' % res['msg'])
                return
        else:
            print('不支持的视频格式!')
            break


@auth
def delete_video():
    request = {'interface': 'admin_interface', 'func': 'delete_video', 'task': 'get_movie'}
    response = tcpclient(request)
    if not response['movie']:
        print('当前无可删除电影!')
        return
    for movies in response['movie']:
        print(movies)
    while True:
        name = input('请输出要锁删除的电影名:')
        if name == 'q':
            return
        if name not in response['movie']:
            print('输入的电影名不存在!')
            continue
        request = {'interface': 'admin_interface', 'func': 'delete_video', 'task': 'delele_movie', 'name': name}
        response = tcpclient(request)
        print(response['msg'])
        break


def get_md5(path):
    size = os.path.getsize(path)
    if size > 1024:
        lis = [0, size // 5, size // 4, size // 3, size // 2]
        s = b''
        with open(path, mode='rb') as f:
            for w in lis:
                f.seek(w, 0)
                s += f.read(200)
    else:
        with open(path, mode='rb') as f:
            s = f.read()
    m = hashlib.md5(s)
    return m.hexdigest()


def admin_interface():
    while True:
        print('''
1.登录
2.注册
3.发布公告
4.锁定账户
5.解锁账户
6.上传视频
7.删除视频 
q.退出''')
        func_dict = {
            '1': login,
            '2': register,
            '3': announce,
            '4': lock_account,
            '5': unlock_account,
            '6': upload_video,
            '7': delete_video
        }
        choice = input('>>:').strip()
        if not choice:
            print('输入不存在!')
            continue
        elif choice == 'q':
            break
        elif choice in func_dict:
            func_dict[choice]()
