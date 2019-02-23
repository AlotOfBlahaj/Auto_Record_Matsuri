import asyncio
import time

from config import (
    sec, enable_mirrativ, enable_youtube, enable_proxy,
    userid, ddir, proxy, channel_id, api_key, quality, download_in_live)
from mirrativ import Mirrativ
from youtube import Youtube
from tools import echo_log


# 定时器，以后考虑用scheduler代替？
class Localtimer:

    def __init__(self):
        self.y = Youtube(channel_id, enable_proxy, proxy, ddir, api_key, quality, download_in_live)
        self.m = Mirrativ(userid, enable_proxy, proxy, ddir)

    async def youtube_timer(self):
        self.y.check()
        await asyncio.sleep(sec)

    async def mirrativ_timer(self):
        self.m.check()
        await asyncio.sleep(sec)


# 这个异步功能有限，考虑在每个模块请求IO时也加入异步处理
async def main():
    t = Localtimer()
    tasks = asyncio.gather(t.youtube_timer(), t.mirrativ_timer())
    await tasks
    del t


if __name__ == '__main__':
    if enable_mirrativ and enable_youtube:
        while True:
            asyncio.run(main())
    elif enable_youtube and enable_mirrativ == 0:
        while True:
            y = Youtube(channel_id, enable_proxy, proxy, ddir, api_key, quality, download_in_live)
            y.check()
            del y
            time.sleep(sec)

    elif enable_mirrativ and enable_youtube == 0:
        while True:
            m = Mirrativ(userid, enable_proxy, proxy, ddir)
            m.check()
            del m
            time.sleep(sec)
    else:
        echo_log('You should enable a module')
        exit(-1)
