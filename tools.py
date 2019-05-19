import json
import logging
from functools import wraps
from os import mkdir
from os.path import abspath, dirname
from time import strftime, localtime, time, sleep

import pymongo
import requests
from bson import ObjectId
from retrying import retry

from config import enable_bot, host, group_id, proxy, enable_proxy, sec_error, sec

ABSPATH = dirname(abspath(__file__))
fake_headers = {
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
}
proxies = {
    "http": f"http://{proxy}",
    "https": f"http://{proxy}",
}


@retry(wait_fixed=sec_error)
def get(url: str, mode='text'):
    try:
        if enable_proxy:
            r = requests.get(url, headers=fake_headers, proxies=proxies)
        else:
            r = requests.get(url, headers=fake_headers)
        if mode == 'img':
            return r
        else:
            return r.text
    except requests.RequestException:
        logger = get_logger('Requests')
        logger.exception('Network Error')


def get_json(url: str) -> dict:
    try:
        return json.loads(get(url))
    except json.decoder.JSONDecodeError:
        logger = get_logger('Json')
        logger.exception('Load Json Error')


def get_logger(module):
    logger = logging.getLogger(module)
    if not logger.handlers:
        logger.setLevel(level=logging.DEBUG)
        # 格式化
        formatter = logging.Formatter(
            f'%(asctime)s[%(levelname)s]: %(filename)s[line:%(lineno)d] - {module}: %(message)s')

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
            try:
                requests.post(f'http://{host}/send_group_msg', data=_msg, headers=headers)
            except requests.exceptions.RequestException as e:
                logger = get_logger('Bot')
                logger.exception(e)


class Database:
    def __init__(self, db: str):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        _db = client["Video"]
        self.db = _db[db]
        self.logger = get_logger('Database')

    def select(self):
        values = self.db.find()
        return values

    def delete(self, _id):
        self.db.delete_one({"_id": ObjectId(_id)})
        self.logger.info(f"ID: {_id} has been deleted")

    def insert(self, _title, _link, _date):
        vdict = {"Title": _title,
                 "Link": _link,
                 "Date": _date}
        result = self.db.insert_one(vdict)
        self.logger.info(result)


def while_warp(func):
    @wraps(func)
    def warp(*args, **kwargs):
        while True:
            func(*args, *kwargs)
            sleep(sec)

    return warp
