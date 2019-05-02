import json
import logging
import sqlite3
from os import mkdir
from os.path import abspath, dirname
from time import strftime, localtime, time

import requests

from config import enable_bot, host, group_id, proxy, enable_proxy

ABSPATH = dirname(abspath(__file__))
fake_headers = {
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
}
proxies = {
    "http": f"http://{proxy}",
    "https": f"http://{proxy}",
}


def get(url):
    if enable_proxy:
        return requests.get(url, headers=fake_headers, proxies=proxies).text
    return requests.get(url, headers=fake_headers).text


def get_json(url):
    return json.loads(get(url))


def get_logger(module):
    logger = logging.getLogger(module)
    if not logger.handlers:
        logger.setLevel(level=logging.DEBUG)

        # 格式化
        formatter = logging.Formatter(
            f'%(asctime)s - %(filename)s[line:%(lineno)d] - {module} - %(levelname)s: %(message)s')

        # 输出文件
        today = strftime('%m-%d', localtime(time()))
        try:
            file_handler = logging.FileHandler(f"log/log-{today}.log")
        except FileNotFoundError:
            mkdir('log')
            file_handler = logging.FileHandler(f"log/log-{today}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 输出流
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger


# 关于机器人HTTP API https://cqhttp.cc/docs/4.7/#/API
def bot(message):
    if enable_bot:
        # 此处要重定义opener，否则会使用代理访问
        # opener1 = request.build_opener()
        # request.install_opener(opener1)
        # 传入JSON时，应使用这个UA
        headers = {'Content-Type': 'application/json'}
        # 将消息输入dict再转为json
        # 此处不应该直接使用HTTP GET的方式传入数据
        for _group_id in group_id:
            _msg = {
                'group_id': int(_group_id),
                'message': message,
                'auto_escape': True
            }
            _msg = json.dumps(_msg)
            r = requests.post(f'http://{host}/send_group_msg', data=_msg, headers=headers)
            try:
                assert r.status_code == 200
            except AssertionError as e:
                logger = get_logger('Bot')
                logger.exception(e)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('ref.db')
        self.cursor = self.conn.cursor()
        self.logger = get_logger('Database')

    def select(self):
        self.cursor.execute('SELECT ID,REF FROM Youtube')
        values = self.cursor.fetchall()
        return values

    def delete(self, _id):
        self.cursor.execute(f'DELETE FROM Youtube WHERE ID = {_id};')
        self.conn.commit()
        self.logger.info(f"ID: {_id} has been deleted")

    def insert(self, _title, _link, _date):
        self.cursor.execute(
            f"INSERT INTO StreamLink (ID, Title, Link, Date) VALUES (NULL, '{_title}', '{_link}', '{_date}');")
        self.conn.commit()
        self.logger.info(f"Link: {_link} has been inserted")
