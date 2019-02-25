import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MOVIE_DIR = os.path.join(BASE_DIR, '视频')
if not os.path.exists(MOVIE_DIR):
    os.mkdir(MOVIE_DIR)


ip='127.0.0.1'
port=8080


user = 'root'
password = '1234'
database = 'zaixianshipin'
charset = 'utf8'
autocommit = True
max_pool_count = 5
current_pool = 0