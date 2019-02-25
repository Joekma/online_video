mport json
import os
import socket
import struct

from conf.settings import SAVE_DIR, ip, port
from lib.common import show_process

client = socket.socket()
client.connect((ip, port))
head = client.recv(4)
requeset_size = struct.unpack('i', head)[0]
data = client.recv(requeset_size).decode('utf-8')
data = json.loads(data)
if not data:
    pass
else:
    announcement = json.loads(data)
    print('----------来自服务器的最新公告----------')
    print('标题:%s\n内容:%s\n发布时间:%s\n\n' % (announcement['title'], announcement['content'], announcement['time']))


def tcpclient(request, is_upload=None):
    requeset_byte = json.dumps(request).encode('utf-8')
    head_bytes = struct.pack('i', len(requeset_byte))
    client.send(head_bytes)
    client.send(requeset_byte)
    if is_upload:
        file_path = request['from_path']
        file_size = request['size']
        total_size = 0
        with open(file_path, mode='rb') as f:
            while total_size < file_size:
                data = f.read(1024)
                client.send(data)
                total_size += len(data)
                show_process(total_size / file_size)
    head = client.recv(4)
    requeset_size = struct.unpack('i', head)[0]
    data = client.recv(requeset_size)
    response = json.loads(data)
    if response.get('download'):
        file_name = response['file_name']
        path = os.path.join(SAVE_DIR, file_name)
        file_size = int(response['file_size'])
        total_size = 0
        with open(path, mode='ab') as f:
            while total_size < file_size:
                if file_size - total_size < 1024:
                    data = client.recv(file_size - total_size)
                else:
                    data = client.recv(1024)
                f.write(data)
                total_size += len(data)
                show_process(total_size / file_size)
        response = {'status': 'ok', 'msg': '下载成功!'}
    return response
