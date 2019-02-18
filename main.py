import asyncio
import time

from config import sec, sec_error, enable_mirrativ, enable_youtube
from mirrativ import Mirrativ
from youtube import Youtube


class Localtimer:

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


def error():
    print('Something wrong. After {}s retrying'.format(sec_error))
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
                y = Youtube()
                y.check()
                time.sleep(sec)
            except:
                error()
    elif enable_mirrativ and enable_youtube == 0:
        while True:
            try:
                m = Mirrativ()
                m.check()
                time.sleep(sec)
            except:
                error()
    else:
        print('You should enable a module')
        exit(-1)
