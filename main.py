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
            self.y = Youtube(api_key, quality)
            self.y_t = Youtube(api_key, quality)
        if enable_mirrativ:
            self.m = Mirrativ()
        if enable_openrec:
            self.o = Openrec()

    async def check_main(self):
        task = []
        if enable_youtube:
            for x in channel_id:
                task_y = asyncio.create_task(self.y.check(x))
                task.append(task_y)
            task_y_temp = asyncio.create_task(self.y_t.check_temp())
            task.append(task_y_temp)
        if enable_mirrativ:
            for x in userid:
                task_m = asyncio.create_task(self.m.check(x))
                task.append(task_m)
        if enable_openrec:
            for x in oprec_id:
                task_o = asyncio.create_task(self.o.check(x))
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
