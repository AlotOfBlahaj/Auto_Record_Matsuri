import json
import logging
from functools import wraps
from os import mkdir
from os.path import abspath, dirname, isdir
from time import strftime, localtime, time, sleep

import pymongo
import requests
from bson import ObjectId
from retrying import retry

from config import config

ABSPATH = dirname(abspath(__file__))
fake_headers = {
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
}
proxies = {
    "http": f"http://{config['proxy']}",
    "https": f"http://{config['proxy']}",
}


@retry(wait_fixed=config['error_sec'])
def get(url: str, mode='text'):
    try:
        if config['enable_proxy']:
            r = requests.get(url, headers=fake_headers, proxies=proxies)
        else:
            r = requests.get(url, headers=fake_headers)
        if mode == 'img':
            return r
        else:
            return r.text
    except requests.RequestException:
        logger = logging.getLogger('run.get')
        logger.exception('Network Error')


def get_json(url: str) -> dict:
    try:
        return json.loads(get(url))
    except json.decoder.JSONDecodeError:
        logger = logging.getLogger('run.get_json')
        logger.exception('Load Json Error')


def get_logger():
    logger = logging.getLogger('run')
    today = strftime('%m-%d', localtime(time()))
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename=f"log/log-{today}.log")
    formatter = logging.Formatter("%(asctime)s[%(levelname)s]: %(filename)s[line:%(lineno)d] - %(name)s : %(message)s")
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.WARNING)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


# 关于机器人HTTP API https://cqhttp.cc/docs/4.7/#/API
def bot(message: str, user_config: dict):
    if config['enable_bot'] and user_config['bot_notice']:
        try:
            group_id = user_config['group_id']
        except KeyError:
            group_id = config['group_id']
        # 传入JSON时，应使用这个UA
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {config["bot_token"]}'}
        for _group_id in group_id:
            _msg = {
                'group_id': int(_group_id),
                'message': message,
                'auto_escape': False
            }
            msg = json.dumps(_msg)
            logger = logging.getLogger('run.bot')
            try:
                requests.post(f'http://{config["bot_host"]}/send_group_msg', data=msg, headers=headers)
                logger.warning(f'{msg}')
            except requests.exceptions.RequestException as e:
                logger.exception(e)


class Database:
    def __init__(self, db: str):
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        _db = client["Video"]
        self.db = _db[db]
        self.logger = logging.getLogger('run.db')

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
            sleep(config['sec'])

    return warp


def check_ddir_is_exist(ddir=config['ddir']):
    if not isdir(ddir):
        try:
            mkdir(ddir)
        except FileNotFoundError:
            logger = logging.getLogger('run.check_ddir')
            logger.exception('下载目录（ddir）配置错误，请选择可用的目录')
            exit(-1)
   

def get_ddir(user_config):
    try:
        if user_config['ddir'] != config['ddir']:
            ddir = f'{config["ddir"]}/{user_config["ddir"]}'
        else:
            ddir = config['ddir']
    except KeyError:
        ddir = config['ddir']
    return ddir
