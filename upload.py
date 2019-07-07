import re
import subprocess
from abc import ABCMeta, abstractmethod
from os import name
from urllib.parse import quote

from minio import Minio

from config import ddir, enable_db, s3_access_key, s3_secret_key, upload_by, s3_server
from tools import get_logger, ABSPATH, Database, bot


class Upload(metaclass=ABCMeta):
    @abstractmethod
    def upload_item(self, item_path, item_name):
        pass


class S3Upload(Upload):
    def __init__(self):
        self.logger = get_logger('S3Upload')
        self.minio = Minio(s3_server,
                           access_key=s3_access_key,
                           secret_key=s3_secret_key,
                           secure=True)

    def upload_item(self, item_path, item_name):
        self.minio.fput_object('matsuri', item_name, item_path)


class BDUpload(Upload):
    def __init__(self):
        self.logger = get_logger('BDUpload')

    def upload_item(self, item_path: str, item_name: str) -> None:
        if 'nt' in name:
            command = [f"{ABSPATH}\\BaiduPCS-Go\\BaiduPCS-Go.exe", "upload", "--nofix"]
        else:
            command = [f"{ABSPATH}/BaiduPCS-Go/BaiduPCS-Go", "upload", "--nofix"]
        command.append(item_path)
        command.append("/")
        subprocess.run(command)

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
        except AttributeError:
            self.logger.exception('get share link error')
            raise RuntimeError('get share link error')
        return link


def upload_video(video_dict):
    upload_way_dict = {'bd': BDUpload,
                       's3': S3Upload}
    upload_way = upload_way_dict.get(upload_by)
    uploader = upload_way()
    uploader.upload_item(f"{ddir}/{video_dict['Title']}", video_dict['Title'])
    if upload_by == 'bd':
        share_url = uploader.share_item(video_dict['Title'])
        if enable_db:
            db = Database('Video')
            db.insert(video_dict['Title'], share_url, video_dict['Date'])
    elif upload_by == 's3':
        if enable_db:
            db = Database('Video')
            db.insert(video_dict['Title'],
                      f"gets3/{quote(video_dict['Title'])}",
                      video_dict['Date'])
    else:
        raise RuntimeError(f'Upload {video_dict["Title"]} failed')
    bot(f"[下载提示] {video_dict['Title']} 已上传, 请查看页面")
