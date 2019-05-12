import re
import subprocess
from os import name
from os.path import isfile
from time import sleep

from config import enable_upload, ddir, enable_proxy, proxy, enable_db
from queues_process import queue_map, Queue
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
            # 此处一定要注明encoding

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

    def adjust(self):
        self.title_block()
        self.filename_length_limit()
        self.file_exist()
        return self.filename


def process_video(data, call_back):
    bot(f"[直播提示] {call_back['Module']}{data.get('Title')} 正在直播 链接: {data['Target']}")

    logger = get_logger('Process Video')
    logger.info(f'{call_back["Module"]} Found A Live, starting downloader')

    data['Title'] = AdjustFileName(data['Title']).adjust()
    try:
        if call_back['Module'] == 'Youtube':
            downloader(r"https://www.youtube.com/watch?v=" + data['Ref'], data['Title'], proxy, '720p')
        else:
            downloader(data['Ref'], data['Title'], proxy)
        link = bd_upload(f"{data['Title']}")
        if link:
            if enable_db:
                db = Database('Video')
                db.insert(data['Title'], link, data['Date'])
            bot(f"[下载提示] {data['Title']} 已上传, 请查看页面")
    except RuntimeError:
        return None
    finally:
        sleep(1)
        return_queue(call_back)


def return_queue(call_back):
    if call_back['Target']:
        q = Queue(queue_map(call_back['Module']))
        q.put_nowait(call_back['Target'])
