import subprocess
import logging
from urllib.parse import quote

import re
from abc import ABCMeta, abstractmethod
from minio import Minio
from os import name
from retrying import retry

from config import config
from tools import get_logger, ABSPATH, Database, bot, get_ddir
from users_map import user_map


class Upload(metaclass=ABCMeta):
    @abstractmethod
    def upload_item(self, item_path, item_name):
        pass


class S3Upload(Upload):
    def __init__(self):
        self.logger = logging.getLogger('run.s3upload')
        self.minio = Minio(config['s3_server'],
                           access_key=config['s3_access_key'],
                           secret_key=config['s3_secret_key'],
                           secure=True)

    def upload_item(self, item_path, item_name):
        self.minio.fput_object('matsuri', item_name, item_path)


class BDUpload(Upload):
    def __init__(self):
        self.logger = logging.getLogger('run.bdupload')

    def upload_item(self, item_path: str, item_name: str) -> None:
        if 'nt' in name:
            command = [f"{ABSPATH}\\BaiduPCS-Go\\BaiduPCS-Go.exe", "upload", "--nofix"]
        else:
            command = [f"{ABSPATH}/BaiduPCS-Go/BaiduPCS-Go", "upload", "--nofix"]
        command.append(item_path)
        command.append("/")
        subprocess.run(command)

    @retry(stop_max_attempt_number=3)
    def share_item(self, item_name: str) -> str:
        if 'nt' in name:
            command = [f'{ABSPATH}\\BaiduPCS-GO\\BaiduPCS-Go.exe', "share", "set"]
        else:
            command = [f"{ABSPATH}/BaiduPCS-Go/BaiduPCS-Go", "share", "set"]
        command.append(item_name)
        s2 = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding='utf-8', universal_newlines=True)
        share_info = s2.stdout
        if 'https' in share_info:
            share_info = share_info.replace('\n', '')
            self.logger.info(f'{item_name}: Share successful {share_info}')
        else:
            self.logger.error('Share failed')
            raise RuntimeError(f'{item_name} share failed')
        reg = r'https://pan.baidu.com/s/([A-Za-z0-9_-]{23})'
        linkre = re.compile(reg)
        link = re.search(linkre, share_info)
        try:
            link = 'https://pan.baidu.com/s/' + link.group(1)
            return link
        except AttributeError:
            self.logger.exception('get share link error')
            raise RuntimeError('get share link error')


def upload_video(video_dict, user_config):
    upload_way_dict = {'bd': BDUpload,
                       's3': S3Upload}
    upload_way = upload_way_dict.get(config['upload_by'])
    uploader = upload_way()
    ddir = get_ddir(user_config)
    uploader.upload_item(f"{ddir}/{video_dict['Title']}", video_dict['Title'])
    if config['upload_by'] == 'bd':
        share_url = uploader.share_item(video_dict['Title'])
        if config['enable_mongodb']:
            db = Database(user_map(video_dict['User']))
            db.insert(video_dict['Title'], share_url, video_dict['Date'])
    elif config['upload_by'] == 's3':
        if config['enable_mongodb']:
            db = Database(user_map(video_dict['User']))
            db.insert(video_dict['Title'],
                      f"gets3/{quote(video_dict['Title'])}",
                      video_dict['Date'])
    else:
        raise RuntimeError(f'Upload {video_dict["Title"]} failed')
    bot(f"[下载提示] {video_dict['Title']} 已上传, 请查看https://matsuri.design/", user_config)
