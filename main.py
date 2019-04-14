import asyncio
from time import sleep

from config import (
    sec, enable_mirrativ, enable_youtube, enable_openrec, oprec_id,
    userid, channel_id, api_key, quality, enable_twitcasting, twitcasting_ld)
from mirrativ import Mirrativ
from openrec import Openrec
from twitcasting import Twitcasting
from youtube import Youtube


# 定时器，以后考虑用scheduler代替？
class Localtimer:

    def __init__(self):
        if enable_youtube:
            self.y = Youtube(api_key, quality)
        if enable_mirrativ:
            self.m = Mirrativ()
        if enable_openrec:
            self.o = Openrec()
        if enable_twitcasting:
            self.t = Twitcasting()

    async def check_main(self):
        task = []
        if enable_youtube:
            for x in channel_id:
                task_y = asyncio.create_task(self.y.check(x))
                task.append(task_y)
            task_y_temp = asyncio.create_task(self.y.check_temp())
            task.append(task_y_temp)
        if enable_mirrativ:
            for x in userid:
                task_m = asyncio.create_task(self.m.check(x))
                task.append(task_m)
        if enable_openrec:
            for x in oprec_id:
                task_o = asyncio.create_task(self.o.check(x))
                task.append(task_o)
        if enable_twitcasting:
            for x in twitcasting_ld:
                task_t = asyncio.create_task(self.t.check(x))
                task.append(task_t)
        await asyncio.wait(task)


async def main():
    t = Localtimer()
    await t.check_main()


if __name__ == '__main__':
    while True:
        asyncio.run(main())
        sleep(sec)
