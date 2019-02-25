import core.common
from TCPclient.TCPclient import tcpclient

current_user = None


def auth(func):
    def wrapper(*args, **kwargs):
        if not current_user:
            print('请先登录!')
            login()
            res = func(*args, **kwargs)
            return res
        res = func(*args, **kwargs)
        return res

    return wrapper


def login(identity=0):
    core.common.login(identity)


def register(identity=0):
    core.common.register(identity)


@auth
def open_member():
    while True:
        choice = input('即将开通会员是否确认?(y/n)')
        if choice =='n':
            return
        if not choice:
            print('选择不能为空!')
        request = {'interface': 'user_interface', 'func': 'open_member', 'name': current_user['name']}
        response = tcpclient(request)
        print(response['msg'])
        break


@auth
def show_video():
    request = {'interface': 'user_interface', 'func': 'show_video'}
    response = tcpclient(request)
    if not response['movie']:
        print('当前服务器无电影!')
        return
    for movie in response['movie']:
        print('电影名:%s,大小:%.2fMB,作者:%s,VIP影片:%s' % (movie[0], float(movie[1]) / 1024 / 1024, movie[2],
                                                   '是' if movie[3] == 1 else '否'))
    return response['movie']


@auth
def download_video():
    movie_list = show_video()
    if not movie_list:
        return
    movie_name = input('请选择要下载的电影名:').strip()
    if movie_name == 'q':
        return
    if not current_user['vip']:
        for movie in movie_list:
            if movie[0] == movie_name and movie[3] == 0:
                request = {'interface': 'user_interface', 'func': 'download_video', 'name': movie_name}
                response = tcpclient(request)
                print('\r%s' % response['msg'])
        else:
            print('该电影为会员视频!')
    request = {'interface': 'user_interface', 'func': 'download_video', 'name': movie_name, 'uid': current_user['uid']}
    response = tcpclient(request)
    print(response['msg'])


@auth
def download_history():
    request = {'interface': 'user_interface', 'func': 'download_history', 'uid': current_user['uid']}
    response = tcpclient(request)
    for history in response['history']:
        print('下载电影:%s,下载时间:%s' % (history[0], history[1]))


@auth
def view_announcement():
    request = {'interface': 'user_interface', 'func': 'view_announcement'}
    response = tcpclient(request)
    for announcement in response['msg']:
        print('标题:%s\n内容:%s\n时间:%s\n\n' % (announcement[0], announcement[1], announcement[2]))


def user_interface():
    while True:
        print('''
1.登录
2.注册
3.开会员
4.查看视频
5.下载视频 
6.查看下载记录
7.查看公告
q.退出''')
        func_dict = {
            '1': login,
            '2': register,
            '3': open_member,
            '4': show_video,
            '5': download_video,
            '6': download_history,
            '7': view_announcement
        }
        choice = input('>>:').strip()
        if not choice:
            print('输入不存在!')
            continue
        elif choice == 'q':
            break
        elif choice in func_dict:
            func_dict[choice]()
