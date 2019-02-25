import os
import sys

from TCPserver.TCPserver import start_server

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if __name__ == '__main__':
    start_server()
