import asyncio
import time

from config import (
    sec, sec_error, enable_mirrativ, enable_youtube, enable_proxy,
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


def error():
    echo_log(f'Something wrong. After {sec_error}s retrying')
    time.sleep(sec_error)


if __name__ == '__main__':
    if enable_mirrativ and enable_youtube:
        while True:
            try:
                asyncio.run(main())
            except:
                error()
    elif enable_youtube and enable_mirrativ == 0:
        while True:
            try:
                y = Youtube(channel_id, enable_proxy, proxy, ddir, api_key, quality, download_in_live)
                y.check()
                del y
                time.sleep(sec)
            except KeyboardInterrupt:
                pass
            except:
                error()
    elif enable_mirrativ and enable_youtube == 0:
        while True:
            try:
                m = Mirrativ(userid, enable_proxy, proxy, ddir)
                m.check()
                del m
                time.sleep(sec)
            except KeyboardInterrupt:
                pass
            except:
                error()
    else:
        echo_log('You should enable a module')
        exit(-1)
