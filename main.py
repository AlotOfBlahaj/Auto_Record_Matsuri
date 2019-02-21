import asyncio
import time

from config import sec, sec_error, enable_mirrativ, enable_youtube
from mirrativ import Mirrativ
from youtube import Youtube


class Localtimer:

    def __init__(self):
        self.y = Youtube()
        self.m = Mirrativ()

    async def youtube_timer(self):
        self.y.check()
        await asyncio.sleep(sec)

    async def mirrativ_timer(self):
        self.m.check()
        await asyncio.sleep(sec)


async def main():
    t = Localtimer()
    tasks = asyncio.gather(t.youtube_timer(), t.mirrativ_timer())
    await tasks
    del t


def error():
    print(f'Something wrong. After {sec_error}s retrying')
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
                del y
                time.sleep(sec)
            except KeyboardInterrupt:
                pass
            except:
                error()
    elif enable_mirrativ and enable_youtube == 0:
        while True:
            try:
                m = Mirrativ()
                m.check()
                del m
                time.sleep(sec)
            except KeyboardInterrupt:
                pass
            except:
                error()
    else:
        print('You should enable a module')
        exit(-1)
