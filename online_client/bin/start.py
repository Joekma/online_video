import os
import sys

from core.admin_interface import admin_interface
from core.user_interface import user_interface

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if __name__ == '__main__':
    while True:
        print('''
1.普通用户
2.管理员用户
q.退出系统
请选择你的身份:''')
        func_dict = {
            '1': user_interface,
            '2': admin_interface
        }
        choice = input('>>:').strip()
        if not choice:
            print('输入不存在!')
            continue
        elif choice == 'q':
            break
        elif choice in func_dict:
            func_dict[choice]()
