import asyncio
import re
import subprocess
from os import name
from time import strftime, localtime, time

from config import enable_upload, ddir, enable_proxy, proxy, quality
from tools import ABSPATH
from tools import get_logger, bot, file_exist, Database


async def bd_upload(file):
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
                            encoding='utf-8')
        line = s2.stdout
        line = line[0].replace('\n', '')
        if 'https' in line:
            logger.info('Share success')
        else:
            logger.error('Share failed')
        return line


async def downloader(link, title, enable_proxy, dl_proxy, quality='best'):
    co = ["streamlink", "--hls-live-restart", "--loglevel", "trace", "--force"]
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
    # 不应该使用os.system


async def process_video(data, call_back):
    await bot(f"[直播提示] [module['Module']]{data.get('Title')} 正在直播 链接: {data['Target']}")
    logger = get_logger('Process Video')
    logger.info(call_back['Module'] + strftime('|%m-%d %H:%M:%S|', localtime(time())) +
                'Found A Live, starting downloader')
    replace_list = ['|', '/', '\\']
    for x in replace_list:
        data['Title'] = data['Title'].replace(x, '#')
    # issue #37
    data['Title'] = file_exist(data['Title'])
    if call_back['Module'] == 'Youtube':
        await downloader(r"https://www.youtube.com/watch?v=" + data['Ref'], data['Title'],
                         enable_proxy, proxy, quality)
    else:
        await downloader(data['Ref'], data['Title'], enable_proxy, proxy)
    logger.info(call_back['Module'] + strftime("|%m-%d %H:%M:%S|", localtime(time())) +
                f"{data['Title']} was already downloaded")
    await bot(f"[下载提示] {data['Title']} 已下载完成，等待上传")
    share = await bd_upload(f"{data['Title']}")
    reg = r'https://pan.baidu.com/s/([A-Za-z0-9_-]{23})'
    linkre = re.compile(reg)
    link = re.search(linkre, share)
    if link:
        link = link.group(1)
        database = Database()
        if not call_back['Module'] == 'Mirrativ':
            database.insert(data['Title'], 'https://pan.baidu.com/s/' + link, data['Date'])
            get_logger(share)
            await bot(f"[下载提示] {data['Title']} 已上传, 请查看页面")
        else:
            await bot(f"[下载提示] {data['Title']} 已上传" + share)
    else:
        logger.error('Uploading Failed')


def inner(data, call_back):
    asyncio.run(process_video(data, call_back))
