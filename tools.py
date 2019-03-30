import asyncio
import json
import re
import sqlite3
import subprocess
from os import mkdir, name
from time import strftime, localtime, time, sleep

import aiohttp

from config import ddir, sec_error, enable_bot, enable_upload, host, group_id, quality, proxy, enable_proxy


class Aio:
    def __init__(self):
        pass

    async def main(self, url, method, **kw):
        async with aiohttp.ClientSession() as session:
            if method == "get":
                return await self.fetch_html(session, url)
            elif method == "post":

                return await self.post(session, url, kw['msg'], kw['headers'])

    async def fetch_html(self, session, url):
        fake_headers = {
            'Accept-Language': 'en-US,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
        }
        if enable_proxy:
            async with session.get(url, proxy=f'http://{proxy}', headers=fake_headers) as response:
                return await response.text(encoding='utf-8')
        else:
            async with session.get(url, headers=fake_headers) as response:
                return await response.text()

    async def post(self, session, url, _json, headers):
        async with session.post(url, data=_json, headers=headers):
            pass
    # if enable_proxy == 1:
    #     proxy_support = request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    #     opener = request.build_opener(proxy_support)
    #     request.install_opener(opener)
    # # 此处一定要注明Language, 见commit cda7031
    # fake_headers = {
    #     'Accept-Language': 'en-US,en;q=0.8',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
    # }
    # req = request.Request(url, headers=fake_headers)
    # response = request.urlopen(req)
    # html = response.read()
    # html = html.decode('utf-8', 'ignore')
    # return html


def m_error(msg):
    echo_log(f'{msg}. After {sec_error}s retrying')
    sleep(sec_error)


def echo_log(log):
    today = strftime('%m-%d', localtime(time()))
    print(log)
    while True:
        try:
            with open(rf"./log/log-{today}.log", 'a') as logs:
                logs.write(log + "\n")
            break
        # 没有log文件夹的话就新建一个
        except FileNotFoundError:
            mkdir("log")


# 关于机器人HTTP API https://cqhttp.cc/docs/4.7/#/API
async def bot(message):
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
                'group_id': _group_id,
                'message': message
            }
            msg = json.dumps(_msg).encode('utf-8')
            net = Aio()
            await net.main(f'http://{host}/send_group_msg', method='post', headers=headers, msg=msg)
        # req = (f'http://{host}/send_group_msg', headers=headers, data=msg)
        # request.urlopen(req)


async def bd_upload(file):
    if enable_upload:
        if 'nt' in name:
            command = [".\\BaiduPCS-Go\\BaiduPCS-Go.exe", "upload"]
            command2 = ['.\\BaiduPCS-GO\\BaiduPCS-Go.exe', "share", "set"]
        else:
            command = ["./BaiduPCS-Go/BaiduPCS-Go", "upload"]
            command2 = ["./BaiduPCS-Go/BaiduPCS-Go", "share", "set"]
            # 此处一定要注明encoding

        command.append(f"{ddir}/{file}")
        command.append("/")
        command2.append(file)
        s1 = subprocess.Popen(command)
        while True:
            s1_code = s1.poll()
            if s1_code is not None:
                break
            else:
                await asyncio.sleep(10)
        s2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding='utf-8')
        # while True:
        #     s2_code = s2.poll()
        #     if s2_code:
        #         break
        #     else:
        #         echo_log('Uploading...')
        #         await asyncio.sleep(30)
        line = s2.stdout.readline().replace('\n', '')
        return line


async def downloader(link, title, enable_proxy, dl_proxy, quality='best'):
    co = ["streamlink", "--hls-live-restart", "--loglevel", "trace", "--force"]
    if enable_proxy:
        co.append('--http-proxy')
        co.append(f'http://{dl_proxy}')
        co.append('--https-proxy')
        co.append(f'https://{dl_proxy}')
    co.append("-o")
    co.append(f"{ddir}/{title}.ts")
    co.append(link)
    co.append(quality)
    s = subprocess.Popen(co)
    while True:
        s_code = s.poll()
        if s_code is not None:
            break
        else:
            echo_log('Downloading...')
            await asyncio.sleep(15)
    # subprocess.run(co)
    # 不应该使用os.system


async def process_video(is_live, model):
    await bot(f"[直播提示] [{model}]{is_live.get('Title')} 正在直播 链接: https://www.youtube.com/watch?v={is_live['Ref']}")
    echo_log(model + strftime('|%m-%d %H:%M:%S|', localtime(time())) +
             'Found A Live, starting downloader')
    if model == 'Youtube':
        await downloader(r"https://www.youtube.com/watch?v=" + is_live['Ref'], is_live['Title'],
                         enable_proxy, proxy, quality)
    else:
        await downloader(is_live['Ref'], is_live['Title'], enable_proxy, proxy)
    echo_log(model + strftime("|%m-%d %H:%M:%S|", localtime(time())) +
             f"{is_live['Title']} was already downloaded")
    await bot(f"[下载提示] {is_live['Title']} 已下载完成，等待上传")
    share = await bd_upload(f"{is_live['Title']}.ts")
    reg = r'https://pan.baidu.com/s/([A-Za-z0-9_-]{23})'
    linkre = re.compile(reg)
    link = re.search(linkre, share)
    if link:
        link = link.group(1)
    else:
        raise IOError
    database = Database()
    database.insert(is_live['Title'], 'https://pan.baidu.com/s/' + link, is_live['Date'])
    echo_log(share)
    await bot(f"[下载提示] {is_live['Title']} 已上传" + share)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('ref.db')
        self.cursor = self.conn.cursor()

    def select(self):
        self.cursor.execute('SELECT ID,REF FROM Youtube')
        values = self.cursor.fetchall()
        return values

    def delete(self, _id):
        self.cursor.execute(f'DELETE FROM Youtube WHERE ID = {_id};')
        self.conn.commit()
        echo_log(f"ID: {_id} has been deleted")

    def insert(self, _title, _link, _date):
        self.cursor.execute(
            f"INSERT INTO StreamLink (ID, Title, Link, Date) VALUES (NULL, '{_title}', '{_link}', '{_date}');")
        self.conn.commit()
        echo_log(f"Link: {_link} has been inserted")
