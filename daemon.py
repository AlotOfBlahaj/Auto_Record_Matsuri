from multiprocessing import Process
from time import sleep

from config import sec
from queues import download_queue
from queues_process import Queue, queue_map
from tools import get_logger
from video_process import process_video


class VideoDownload:
    def __init__(self):
        self.queue = Queue(download_queue)
        self.logger = get_logger('VideoDownload')
        self.daemon()

    @staticmethod
    def download(video_info):
        proc = Process(target=process_video, args=video_info)
        proc.start()

    def daemon(self):
        while True:
            self.logger.info('Waiting for tasks')
            video_info = self.queue.get()
            self.download(video_info)


class VideoDaemon:
    def __init__(self, queue):
        self.queue = Queue(queue)
        self.download_queue = Queue(download_queue)

    def put_download(self, video):
        self.download_queue.put_nowait(video)

    def daemon(self):
        while True:
            live_info = self.queue.get()
            self.actor(live_info)

    def actor(self, live_info):
        pass
        # proc = Process(target=self.check, args=(,))
        # proc.start()

    def check(self, live_info):
        pass

    @staticmethod
    def return_and_sleep(item, module):
        sleep(sec)
        q = Queue(queue_map(module))
        q.put_nowait(item)
