from abc import ABCMeta, abstractmethod
from multiprocessing import Process

from queues import upload_queue
from tools import get_logger
from upload import upload_video


class VideoUpload(Process):
    def __init__(self):
        super().__init__()
        self.queue = upload_queue
        self.logger = get_logger('VideoUpload')
        self.video_info = None

    def run(self) -> None:
        self.start_daemon()

    def start_daemon(self):
        self.logger.info('Waiting for tasks')
        while True:
            video_info = self.queue.get()
            self.video_info = video_info
            upload_video(self.video_info)


class VideoDaemon(Process, metaclass=ABCMeta):
    def __init__(self, target_id):
        super().__init__()
        self.target_id = target_id

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def check(self):
        pass
