from config import twitcasting_ld, enable_twitcasting, oprec_id, enable_openrec, userid, enable_mirrativ, channel_id, \
    enable_youtube
from queues import twitcasting_queue, openrec_queue, mirrativ_queue, youtube_queue


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
    if module == 'Youtube':
        return youtube_queue
    elif module == 'Mirrativ':
        return mirrativ_queue
    elif module == 'Twitcasting':
        return twitcasting_queue
    elif module == 'Openrec':
        return openrec_queue
    else:
        raise RuntimeError


def add_queue(queue, data):
    queue.put_nowait(data)
