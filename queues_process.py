from config import twitcasting_ld, enable_twitcasting, oprec_id, enable_openrec, userid, enable_mirrativ, channel_id, \
    enable_youtube
from queues import twitcasting_queue, openrec_queue, mirrativ_queue, youtube_queue


class Queue:
    def __init__(self, queue):
        self.queue = queue

    def get(self):
        return self.queue.get()

    def get_nowait(self):
        return self.queue.get_nowait()

    def put_nowait(self, item):
        self.queue.put_nowait(item)


def queue_init():
    if enable_youtube:
        for x in channel_id:
            youtube_queue.put_nowait(x)
    if enable_mirrativ:
        for x in userid:
            mirrativ_queue.put_nowait(x)
    if enable_openrec:
        for x in oprec_id:
            openrec_queue.put_nowait(x)
    if enable_twitcasting:
        for x in twitcasting_ld:
            twitcasting_queue.put_nowait(x)


def queue_map(module):
    queue = {'Youtube': youtube_queue,
             'Mirrativ': mirrativ_queue,
             'Twitcasting': twitcasting_queue,
             'Openrec': openrec_queue}
    return queue.get(module)
