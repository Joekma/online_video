import core.admin_interface
import core.user_interface
from TCPclient.TCPclient import tcpclient




def login(identity):
    while True:
        username = input('请输入用户名:')
        if username == 'q':
            break
        password = input('请输入密码:')
        if not username and password:
            print('用户名或密码不能为空!')
            continue
        requeset = {'interface': 'common', 'func': 'login', 'name': username, 'password': password,
                    'identity': identity}
        response = tcpclient(requeset)
        if response['status'] == 'ok':
            if response['user']['identity'] == 0:
                core.user_interface.current_user = response['user']
            else:
                core.admin_interface.current_admin = response['user']
            print(response['msg'])
            break
        print(response['msg'])


def register(identity):
    while True:
        username = input('请输入注册用户名:')
        if username == 'q':
            break
        password = input('请输入注册密码:')
        if not username and password:
            print('用户名或密码不能为空!')
            continue
        requeset = {'interface': 'common', 'func': 'register', 'name': username, 'password': password,
                    'identity': identity}
        response = tcpclient(requeset)
        if response['status'] == 'ok':
            print(response['msg'])
            break
        print(response['msg'])



