import re
import subprocess
from os import name
from os.path import isfile
from time import strftime, localtime, time

from config import enable_upload, ddir, enable_proxy, proxy
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
        if 's' not in share_info:
            return None
        while True:
            if 'https' in share_info:
                share_info = share_info.replace('\n', '')
                logger.info('Share success')
                break
            else:
                share_info = s2.stdout
                logger.error('Share failed')
        reg = r'https://pan.baidu.com/s/([A-Za-z0-9_-]{23})'
        linkre = re.compile(reg)
        link = re.search(linkre, share_info)
        try:
            link = 'https://pan.baidu.com/s/' + link.group(1)
        except AttributeError:
            raise RuntimeError('Error')
        return link


def downloader(link, title, dl_proxy):
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
    co.append("best")
    subprocess.run(co)
    # 不应该使用os.system


def title_block(title):
    replace_list = ['|', '/', '\\']
    for x in replace_list:
        title.replace(x, '#')
    return title


def file_exist(filename: str) -> str:
    paths = f'{ddir}/{filename}.ts'
    if isfile(paths):
        n = 0
        while True:
            new_filename = filename + f'_{n}.ts'
            if not isfile(f'{ddir}/{new_filename}'):
                return new_filename
            n += 1
    else:
        return filename + '.ts'


def process_video(data, call_back):
    bot(f"[直播提示] {call_back['Module']}{data.get('Title')} 正在直播 链接: {data['Target']}")

    logger = get_logger('Process Video')
    logger.info(call_back['Module'] + strftime('|%m-%d %H:%M:%S|', localtime(time())) +
                'Found A Live, starting downloader')

    data['Title'] = title_block(data['Title'])
    # issue #37
    data['Title'] = file_exist(data['Title'])

    if call_back['Module'] == 'Youtube':
        downloader(r"https://www.youtube.com/watch?v=" + data['Ref'], data['Title'], proxy)
    else:
        downloader(data['Ref'], data['Title'], proxy)

    logger.info(call_back['Module'] + strftime("|%m-%d %H:%M:%S|", localtime(time())) +
                f"{data['Title']} was already downloaded")

    bot(f"[下载提示] {data['Title']} 已下载完成，等待上传")

    link = bd_upload(f"{data['Title']}")
    database = Database()
    if not call_back['Module'] == 'Mirrativ':
        if link:
            database.insert(data['Title'], link, data['Date'])
        bot(f"[下载提示] {data['Title']} 已上传, 请查看页面")
    else:
        bot(f"[下载提示] {data['Title']} 已上传" + link)

    return_queue(call_back)


def return_queue(call_back):
    if call_back['Target']:
        q = Queue(queue_map(call_back['Module']))
        q.put_nowait(call_back['Target'])
