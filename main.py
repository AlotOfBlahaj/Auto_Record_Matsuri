import time
from config import sec, sec_error
from youtube import Youtube
from mirrativ import Mirrativ
import asyncio


class Localtimer(object):

    async def youtube_timer(self):
        y = Youtube()
        y.check()
        await asyncio.sleep(sec)

    async def mirrativ_timer(self):
        m = Mirrativ()
        m.check()
        await asyncio.sleep(sec)


async def main():
    t = Localtimer()
    tasks = asyncio.gather(t.youtube_timer(), t.mirrativ_timer())
    await tasks

if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except:
            time.sleep(sec_error)

