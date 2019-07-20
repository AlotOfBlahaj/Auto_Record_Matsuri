from abc import ABCMeta, abstractmethod
from multiprocessing import Process

from tools import get_logger
from upload import upload_video


class VideoUpload(Process):
    def __init__(self, video_dict):
        super().__init__()
        self.logger = get_logger('VideoUpload')
        self.video_dict = video_dict

    def run(self) -> None:
        try:
            self.start_daemon()
        except KeyboardInterrupt:
            exit(0)

    def start_daemon(self):
        upload_video(self.video_dict)


class VideoDaemon(Process, metaclass=ABCMeta):
    def __init__(self, target_id):
        super().__init__()
        self.target_id = target_id

    def run(self) -> None:
        try:
            self.check()
        except KeyboardInterrupt:
            exit(0)

    @abstractmethod
    def check(self):
        pass
