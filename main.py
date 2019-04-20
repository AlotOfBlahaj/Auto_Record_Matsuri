import asyncio
import multiprocessing
from time import sleep

from bilibili import Bilibili
from config import sec, quality, api_key, enable_youtube, enable_twitcasting, enable_openrec, enable_mirrativ, \
    enable_bilibili, bilibili_id
from mirrativ import Mirrativ
from openrec import Openrec
from queues import youtube_queue, twitcasting_queue, openrec_queue, mirrativ_queue
from queues_process import queue_init, queue_map, add_queue
from twitcasting import Twitcasting
from video_process import inner
from youtube import Youtube


class Main:
    def __init__(self):
        if enable_youtube:
            self.y = Youtube(api_key, quality)
        if enable_twitcasting:
            self.t = Twitcasting()
        if enable_openrec:
            self.o = Openrec()
        if enable_mirrativ:
            self.m = Mirrativ()
        if enable_bilibili:
            self.b = Bilibili()

    def create_task_list(self):
        task = []
        if enable_youtube:
            while youtube_queue.qsize():
                task.append(asyncio.create_task(self.y.check(youtube_queue.get_nowait())))
        if enable_twitcasting:
            while twitcasting_queue.qsize():
                task.append(asyncio.create_task(self.t.check(twitcasting_queue.get_nowait())))
        if enable_openrec:
            while openrec_queue.qsize():
                task.append(asyncio.create_task(self.o.check(openrec_queue.get_nowait())))
        if enable_mirrativ:
            while mirrativ_queue.qsize():
                task.append(asyncio.create_task(self.m.check(mirrativ_queue.get_nowait())))
        if enable_bilibili:
            for x in bilibili_id:
                task.append(asyncio.create_task(self.b.check(x)))
        return task

    async def main(self):
        queue_init()
        sleep(0.5)
        while True:
            tasks = self.create_task_list()
            result = [await run for run in tasks]
            for data in result:
                if data:
                    video_info = data[0]
                    module = data[1]
                    p = multiprocessing.Process(target=self.proc, args=(video_info, module))
                    p.start()
            sleep(sec)

    def proc(self, video_info, call_back):
        inner(video_info, call_back)
        queue = queue_map(call_back['Module'])
        if call_back['Target']:
            add_queue(queue, call_back['Target'])


if __name__ == '__main__':
    MAIN = Main()
    asyncio.run(MAIN.main())
