from multiprocessing import Process
from time import sleep

from bilibili import Bilibili
from config import enable_youtube, enable_twitcasting, enable_openrec, enable_mirrativ, enable_bilibili, \
    enable_youtube_temp, channel_id, userid, oprec_id, twitcasting_ld, bilibili_id, sec
from daemon import VideoUpload
from mirrativ import Mirrativ
from openrec import Openrec
from tools import get_logger
from twitcasting import Twitcasting
from youtube import Youtube, start_temp_daemon


class Event:
    def __init__(self):
        self.logger = get_logger('Event')
        self.events_no_need_while = []
        self.events_need_while = []
        if enable_youtube:
            self.events_need_while.append(self.start_youtube)
        if enable_youtube_temp:
            self.events_no_need_while.append(Process(target=self.start_youtube_temp))
        if enable_twitcasting:
            self.events_need_while.append(self.start_twitcasting)
        if enable_openrec:
            self.events_need_while.append(self.start_openrec)
        if enable_mirrativ:
            self.events_need_while.append(self.start_mirrativ)
        if enable_bilibili:
            self.events_no_need_while.append(Process(target=self.start_bilibili))

    def start(self):
        self.start_no_need_while()
        while True:
            self.start_need_while()
            self.logger.info(f'Next Check: {sec}')
            sleep(sec)

    def start_no_need_while(self):
        for proc in self.events_no_need_while:
            proc.start()

    def start_need_while(self):
        for proc in self.events_need_while:
            proc()

    @staticmethod
    def start_youtube():
        for target_id in channel_id:
            y = Youtube(target_id)
            y.start()

    @staticmethod
    def start_youtube_temp():
        start_temp_daemon()

    @staticmethod
    def start_mirrativ():
        for target_id in userid:
            m = Mirrativ(target_id)
            m.start()

    @staticmethod
    def start_openrec():
        for target_id in oprec_id:
            o = Openrec(target_id)
            o.start()

    @staticmethod
    def start_twitcasting():
        for target_id in twitcasting_ld:
            t = Twitcasting(target_id)
            t.start()

    @staticmethod
    def start_bilibili():
        for b_id in bilibili_id:
            b = Bilibili()
            b.actor(b_id)


if __name__ == '__main__':
    uploader = VideoUpload()
    uploader.start()
    e = Event()
    e.start()
