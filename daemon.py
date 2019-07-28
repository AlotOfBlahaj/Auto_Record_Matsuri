from abc import ABCMeta, abstractmethod
from multiprocessing import Process
from threading import Thread

from tools import get_logger
from upload import upload_video


class VideoUpload(Process):
    def __init__(self, video_dict, user_config):
        super().__init__()
        self.video_dict = video_dict
        self.user_config = user_config

    def run(self) -> None:
        try:
            self.start_daemon()
        except KeyboardInterrupt:
            exit(0)

    def start_daemon(self):
        upload_video(self.video_dict, self.user_config)


class VideoDaemon(Thread, metaclass=ABCMeta):
    def __init__(self, user_config):
        super().__init__()
        self.user_config = user_config
        self.target_id = user_config['target_id']

    def run(self) -> None:
        try:
            self.check()
        except KeyboardInterrupt:
            exit(0)

    @abstractmethod
    def check(self):
        pass
