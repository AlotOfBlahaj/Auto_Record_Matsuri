import asyncio
import time

from config import sec, sec_error
from mirrativ import Mirrativ
from youtube import Youtube


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
            print('Something wrong. After {}s retrying'.format(sec_error))
            time.sleep(sec_error)

