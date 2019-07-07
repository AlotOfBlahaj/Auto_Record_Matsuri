from multiprocessing import Process
from os import mkdir
from os.path import isdir

from bilibili import Bilibili
from config import (enable_youtube, enable_twitcasting, enable_openrec, enable_mirrativ, enable_bilibili,
                    enable_youtube_temp, channel_id, userid, oprec_id, twitcasting_ld, bilibili_id, ddir, enable_upload)
from daemon import VideoUpload
from mirrativ import Mirrativ
from openrec import Openrec
from tools import get_logger
from twitcasting import Twitcasting
from youtube import Youtube, start_temp_daemon


class Event:
    def __init__(self):
        self.events_multi = []
        self.gen_process()

    def start(self):
        self.start_multi_task()
        if enable_youtube_temp:
            temp = Process(target=start_temp_daemon)
            temp.run()
        for event in self.events_multi:
            event.join()

    def gen_process(self):
        if enable_youtube:
            for target_id in channel_id:
                y = Youtube(target_id)
                self.events_multi.append(y)
        if enable_twitcasting:
            for target_id in twitcasting_ld:
                t = Twitcasting(target_id)
                self.events_multi.append(t)
        if enable_openrec:
            for target_id in oprec_id:
                o = Openrec(target_id)
                self.events_multi.append(o)
        if enable_mirrativ:
            for target_id in userid:
                m = Mirrativ(target_id)
                self.events_multi.append(m)
        if enable_bilibili:
            for target_id in bilibili_id:
                b = Bilibili(target_id)
                self.events_multi.append(b)

    def start_multi_task(self):
        for proc in self.events_multi:
            proc.daemon = True
            proc.start()


def check_ddir_is_exist():
    if not isdir(ddir):
        try:
            mkdir(ddir)
        except FileNotFoundError:
            logger = get_logger('Main')
            logger.exception('下载目录（ddir）配置错误，请选择可用的目录')
            exit(-1)


if __name__ == '__main__':
    check_ddir_is_exist()
    if enable_upload:
        uploader = VideoUpload()
        uploader.start()
    e = Event()
    e.start()
