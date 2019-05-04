from multiprocessing import Process
from time import sleep

from bilibili import Bilibili
from config import enable_youtube, enable_twitcasting, enable_openrec, enable_mirrativ, enable_bilibili, \
    enable_youtube_temp
from daemon import VideoDownload
from mirrativ import Mirrativ
from openrec import Openrec
from queues_process import queue_init
from twitcasting import Twitcasting
from youtube import Youtube, YoutubeTemp


class Event:
    def __init__(self):
        self.events = [Process(target=self.start_downloader)]
        if enable_youtube:
            self.events.append(Process(target=self.start_youtube))
            if enable_youtube_temp:
                self.events.append(Process(target=self.start_youtube_temp))
        if enable_twitcasting:
            self.events.append(Process(target=self.start_twitcasting))
        if enable_openrec:
            self.events.append(Process(target=self.start_openrec))
        if enable_mirrativ:
            self.events.append(Process(target=self.start_mirrativ))
        if enable_bilibili:
            self.events.append(Process(target=self.start_bilibili))
        self.running = False

    def start(self):
        for proc in self.events:
            proc.start()
        self.running = True

    @staticmethod
    def start_youtube():
        y = Youtube()
        y.daemon()

    @staticmethod
    def start_youtube_temp():
        y_temp = YoutubeTemp()
        y_temp.daemon()

    @staticmethod
    def start_mirrativ():
        m = Mirrativ()
        m.daemon()

    @staticmethod
    def start_openrec():
        o = Openrec()
        o.daemon()

    @staticmethod
    def start_twitcasting():
        t = Twitcasting()
        t.daemon()

    @staticmethod
    def start_downloader():
        d = VideoDownload()
        d.daemon()

    @staticmethod
    def start_bilibili():
        b = Bilibili()
        b.manager()

    def check(self):
        while self.running:
            for proc in self.events:
                if not proc.is_alive():
                    print('End')
            sleep(5)


if __name__ == '__main__':
    queue_init()
    e = Event()
    e.start()
    e.check()
