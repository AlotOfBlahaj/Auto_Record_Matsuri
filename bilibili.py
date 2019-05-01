from multiprocessing import Process
from time import sleep

from bilibili_api.bilibili_api import BilibiliAPI
from config import bilibili_id, sec
from tools import get_logger, bot


class Bilibili:
    def __init__(self):
        self.API = BilibiliAPI()
        self.logger = get_logger('Bilibili')
        self.old_video_num = None

    def check(self, mid):
        self.old_video_num = self.API.get_video_num(mid)
        while True:
            video_num = self.API.get_video_num(mid)
            if video_num > self.old_video_num:
                self.logger.info('Found A new video')
                video_info = self.API.get_video(mid)
                bot(f'[烤肉提示] [Bilibili]{video_info.get("Title")} 链接: {video_info.get("Ref")}')
                self.old_video_num = video_num
            else:
                self.logger.info(f'Not found new videos, {mid}:{video_num}')
            sleep(sec)

    def actor(self, b_id):
        proc = Process(target=self.check, args=(b_id,))
        proc.start()

    def manager(self):
        for b_id in bilibili_id:
            self.actor(b_id)
