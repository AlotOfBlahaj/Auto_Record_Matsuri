import re
import subprocess
from os import name
from os.path import isfile

from config import enable_upload, ddir, enable_proxy, proxy, enable_db
from queues import upload_queue
from tools import ABSPATH
from tools import get_logger, bot, Database


def bd_upload(file):
    logger = get_logger('bd_upload')
    if enable_upload:
        if 'nt' in name:
            command = [f"{ABSPATH}\\BaiduPCS-Go\\BaiduPCS-Go.exe", "upload", "--nofix"]
            command2 = [f'{ABSPATH}\\BaiduPCS-GO\\BaiduPCS-Go.exe', "share", "set"]
        else:
            command = [f"{ABSPATH}/BaiduPCS-Go/BaiduPCS-Go", "upload", "--nofix"]
            command2 = [f"{ABSPATH}/BaiduPCS-Go/BaiduPCS-Go", "share", "set"]
        command.append(f"{ddir}/{file}")
        command.append("/")
        command2.append(file)
        subprocess.run(command)
        s2 = subprocess.run(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding='utf-8', universal_newlines=True)
        share_info = s2.stdout
        if 'https' in share_info:
            share_info = share_info.replace('\n', '')
            logger.info(f'{file}: Share successful {share_info}')
        else:
            logger.error('Share failed')
            raise RuntimeError(f'{file} share failed')
        reg = r'https://pan.baidu.com/s/([A-Za-z0-9_-]{23})'
        linkre = re.compile(reg)
        link = re.search(linkre, share_info)
        try:
            link = 'https://pan.baidu.com/s/' + link.group(1)
            return link
        except AttributeError:
            logger.exception('get share link error')
            raise RuntimeError('get share link error')
    return None


def downloader(link, title, dl_proxy, quality='best'):
    logger = get_logger('Downloader')
    # co = ["streamlink", "--hls-live-restart", "--loglevel", "trace", "--force"]
    co = ["streamlink", "--hls-live-restart", "--force"]
    if enable_proxy:
        co.append('--http-proxy')
        co.append(f'http://{dl_proxy}')
        co.append('--https-proxy')
        co.append(f'https://{dl_proxy}')
    co.append("-o")
    co.append(f"{ddir}/{title}")
    co.append(link)
    co.append(quality)
    subprocess.run(co)
    paths = f'{ddir}/{title}'
    if isfile(paths):
        logger.info(f'{title} has been downloaded.')
        bot(f"[下载提示] {title} 已下载完成，等待上传")
    else:
        logger.error(f'{title} Download error, link: {link}')
        raise RuntimeError(f'{title} Download error, link: {link}')
    # 不应该使用os.system


class AdjustFileName:

    def __init__(self, filename):
        self.filename = filename

    def title_block(self):
        replace_list = ['|', '/', '\\']
        for x in replace_list:
            self.filename = self.filename.replace(x, '#')

    def file_exist(self):
        paths = f'{ddir}/{self.filename}.ts'
        if isfile(paths):
            n = 0
            while True:
                new_filename = self.filename + f'_{n}.ts'
                if not isfile(f'{ddir}/{new_filename}'):
                    self.filename = new_filename
                    break
                n += 1
        else:
            self.filename = self.filename + '.ts'

    def filename_length_limit(self):
        lens = len(self.filename)
        if lens > 80:
            self.filename = self.filename[:80]

    def remove_emoji(self):
        emoji_pattern = re.compile(
            u'(\U0001F1F2\U0001F1F4)|'  # Macau flag
            u'([\U0001F1E6-\U0001F1FF]{2})|'  # flags
            u'([\U0001F600-\U0001F64F])'  # emoticons
            "+", flags=re.UNICODE)
        self.filename = emoji_pattern.sub('', self.filename)

    def adjust(self):
        self.remove_emoji()
        self.title_block()
        self.filename_length_limit()
        self.file_exist()
        return self.filename


def upload_video(video_dict):
    share_url = bd_upload(video_dict['Title'])
    if share_url:
        if enable_db:
            db = Database('Video')
            db.insert(video_dict['Title'], share_url, video_dict['Date'])
        bot(f"[下载提示] {video_dict['Title']} 已上传, 请查看页面")
    else:
        raise RuntimeError(f'Upload {video_dict["Title"]} failed')


def process_video(video_dict):
    """
    处理直播视频，包含bot的发送，视频下载，视频上传和存入数据库
    :param video_dict: 含有直播视频数据的dict
    :param call_back: 用于标识传入来源
    :return: None
    """
    bot(f"[直播提示] {video_dict['Provide']}{video_dict.get('Title')} 正在直播 链接: {video_dict['Target']}")

    logger = get_logger('Process Video')
    logger.info(f'{video_dict["Provide"]} Found A Live, starting downloader')

    video_dict['Title'] = AdjustFileName(video_dict['Title']).adjust()
    if video_dict["Provide"] == 'Youtube':
        downloader(r"https://www.youtube.com/watch?v=" + video_dict['Ref'], video_dict['Title'], proxy, '720p')
    else:
        downloader(video_dict['Ref'], video_dict['Title'], proxy)
    upload_queue.put_nowait(video_dict)
    # link = bd_upload(f"{video_dict['Title']}")
    # if link:
    #     if enable_db:
    #         db = Database('Video')
    #         db.insert(video_dict['Title'], link, video_dict['Date'])
    #     bot(f"[下载提示] {video_dict['Title']} 已上传, 请查看页面")
