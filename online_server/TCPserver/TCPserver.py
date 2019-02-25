import json
import os
import select
import socket
import struct
from threading import Thread

from conf.settings import MOVIE_DIR
from conf.settings import ip, port
from core import common, admin_interface, user_interface
from db.models import Announcement
from db.myorm import Dbhandler

server = socket.socket()
server.bind((ip, port))
server.listen(5)

rlist = [server, ]
wlist = []


def start_server():
    while True:
        rl, xl, _ = select.select(rlist, wlist, [], 1)
        for r in rl:
            if r == server:
                conn, addr = server.accept()
                db = Dbhandler()
                res = db.select_many(Announcement, '1=1 order by time desc', limit=(0, 1))
                if not res:
                    msg = {}
                else:
                    msg = res[0].__dict__
                    msg['time'] = str(msg['time'])
                requeset_byte = json.dumps(msg).encode('utf-8')
                head_bytes = struct.pack('i', len(requeset_byte))
                conn.send(head_bytes)
                conn.send(requeset_byte)
                rlist.append(conn)
                continue
            try:
                head = r.recv(4)
                if not head:
                    r.close()
                    rlist.remove(r)
                    continue
            except ConnectionResetError as e:
                r.close()
                rlist.remove(r)
                continue
            requeset_size = struct.unpack('i', head)[0]
            data = r.recv(requeset_size)
            dic = json.loads(data)
            res = {}
            if dic['interface'] == 'common':
                if dic['func'] == 'register':
                    res = common.register(dic)
                elif dic['func'] == 'login':
                    res = common.login(dic)
            elif dic['interface'] == 'admin_interface':
                if dic['func'] == 'announce':
                    res = admin_interface.announce(dic)
                if dic['func'] == 'lock_account':
                    res = admin_interface.lock_account(dic)
                if dic['func'] == 'unlock_account':
                    res = admin_interface.unlock_account(dic)
                if dic['func'] == 'upload_video':
                    if dic['isfile'] == False:
                        res = admin_interface.upload_video(dic)
                    else:
                        def recive(conn, dic1):
                            file_name = dic1['name']
                            path = os.path.join(MOVIE_DIR, file_name)
                            file_size = dic1['size']
                            total_size = 0
                            rlist.remove(r)
                            with open(path, mode='ab') as f:
                                try:
                                    while total_size < file_size:
                                        if file_size - total_size < 1024:
                                            data = conn.recv(file_size - total_size)
                                        else:
                                            data = conn.recv(1024)
                                        f.write(data)
                                        total_size += len(data)
                                except ConnectionResetError:
                                    conn.close()
                                    f.close()
                                    os.remove(path)
                                    return
                            res = admin_interface.upload_video(dic1, path=path)
                            response = {'status': 'ok', 'msg': '上传成功!'} if res else {'status': 'error',
                                                                                     'msg': 'unknown error'}
                            requeset_byte = json.dumps(response).encode('utf-8')
                            head_bytes = struct.pack('i', len(requeset_byte))
                            conn.send(head_bytes)
                            conn.send(requeset_byte)
                            rlist.append(conn)
                            return

                        Thread(target=recive, args=(r, dic)).start()
                        continue
                if dic['func'] == 'delete_video':
                    res = admin_interface.delete_video(dic)
            elif dic['interface'] == 'user_interface':
                if dic['func'] == 'open_member':
                    res = user_interface.open_member(dic)
                elif dic['func'] == 'show_video':
                    res = user_interface.show_video(dic)
                elif dic['func'] == 'download_video':
                    res = user_interface.download_video(dic)
                elif dic['func'] == 'download_history':
                    res = user_interface.download_history(dic)
                elif dic['func'] == 'view_announcement':
                    res = user_interface.view_announcement(dic)
            requeset_byte = json.dumps(res).encode('utf-8')
            head_bytes = struct.pack('i', len(requeset_byte))
            r.send(head_bytes)
            r.send(requeset_byte)
            if res.get('download'):
                def send(res2, conn):
                    file_path = res2['file_path']
                    file_size = int(res2['file_size'])
                    total_size = 0
                    rlist.remove(conn)
                    with open(file_path, mode='rb') as f:
                        try:
                            while total_size < file_size:
                                data = f.read(1024)
                                conn.send(data)
                                total_size += len(data)
                        except ConnectionResetError:
                            conn.close()
                            f.close()
                            return
                    rlist.append(conn)
                    return

                Thread(target=send, args=(res, r)).start()
