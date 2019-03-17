import asyncio
from urllib import error

from config import (
    sec, enable_mirrativ, enable_youtube, enable_openrec, oprec_id,
    userid, channel_id, api_key, quality)
from mirrativ import Mirrativ
from openrec import Openrec
from tools import m_error
from youtube import Youtube


# 定时器，以后考虑用scheduler代替？
class Localtimer:

    def __init__(self):
        if enable_youtube:
            self.y = Youtube(channel_id, api_key, quality)
        if enable_mirrativ:
            self.m = Mirrativ(userid)
        if enable_openrec:
            self.o = Openrec(oprec_id)

    async def check_main(self):
        task = []
        if enable_youtube:
            task_y = asyncio.create_task(self.y.check())
            task_y_temp = asyncio.create_task(self.y.check_temp())
            task.append(task_y)
            task.append(task_y_temp)
        if enable_mirrativ:
            task_m = asyncio.create_task(self.m.check())
            task.append(task_m)
        if enable_openrec:
            task_o = asyncio.create_task(self.o.check())
            task.append(task_o)
        await asyncio.wait(task)


# 这个异步功能有限，考虑在每个模块请求IO时也加入异步处理
async def main():
    t = Localtimer()
    await t.check_main()
    await asyncio.sleep(sec)


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except error.URLError:
            m_error('URL error!')
