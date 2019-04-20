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


def create_task_list():
    y = Youtube(api_key, quality)
    t = Twitcasting()
    o = Openrec()
    m = Mirrativ()
    b = Bilibili()
    task = []
    if enable_youtube:
        while youtube_queue.qsize():
            task.append(asyncio.create_task(y.check(youtube_queue.get_nowait())))
    if enable_twitcasting:
        while twitcasting_queue.qsize():
            task.append(asyncio.create_task(t.check(twitcasting_queue.get_nowait())))
    if enable_openrec:
        while openrec_queue.qsize():
            task.append(asyncio.create_task(o.check(openrec_queue.get_nowait())))
    if enable_mirrativ:
        while mirrativ_queue.qsize():
            task.append(asyncio.create_task(m.check(mirrativ_queue.get_nowait())))
    if enable_bilibili:
        for x in bilibili_id:
            task.append(asyncio.create_task(b.check(x)))
    return task


async def main():
    queue_init()
    while True:
        tasks = create_task_list()
        result = [await run for run in tasks]
        for data in result:
            if data:
                video_info = data[0]
                module = data[1]
                p = multiprocessing.Process(target=proc, args=(video_info, module))
                p.start()
        sleep(sec)


def proc(video_info, call_back):
    inner(video_info, call_back)
    queue = queue_map(call_back['Module'])
    if call_back['Target']:
        add_queue(queue, call_back['Target'])


if __name__ == '__main__':
    asyncio.run(main())
