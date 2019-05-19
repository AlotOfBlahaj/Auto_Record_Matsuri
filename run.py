from multiprocessing import Process

from bilibili import Bilibili
from config import (enable_youtube, enable_twitcasting, enable_openrec, enable_mirrativ, enable_bilibili,
                    enable_youtube_temp, channel_id, userid, oprec_id, twitcasting_ld, bilibili_id)
from daemon import VideoUpload
from mirrativ import Mirrativ
from openrec import Openrec
from twitcasting import Twitcasting
from youtube import Youtube, start_temp_daemon


class Event:
    def __init__(self):
        self.events_multi = []
        self.events_normal = []
        if enable_youtube:
            self.events_normal.append(self.start_youtube)
        if enable_youtube_temp:
            self.events_multi.append(Process(target=self.start_youtube_temp))
        if enable_twitcasting:
            self.events_normal.append(self.start_twitcasting)
        if enable_openrec:
            self.events_normal.append(self.start_openrec)
        if enable_mirrativ:
            self.events_normal.append(self.start_mirrativ)
        if enable_bilibili:
            self.events_multi.append(Process(target=self.start_bilibili))

    def start(self):
        self.start_multi_task()
        self.start_normal_task()

    def start_multi_task(self):
        for proc in self.events_multi:
            proc.start()

    def start_normal_task(self):
        for proc in self.events_normal:
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
