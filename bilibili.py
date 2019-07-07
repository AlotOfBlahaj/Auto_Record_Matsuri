from multiprocessing import Process
from time import sleep

from bilibili_api.bilibili_api import BilibiliAPI
from config import sec
from tools import get_logger, bot


class Bilibili(Process):
    def __init__(self, mid):
        super().__init__()
        self.mid = mid
        self.API = BilibiliAPI()
        self.logger = get_logger('Bilibili')
        self.old_video_num = None

    def check(self):
        self.old_video_num = self.API.get_video_num(self.mid)
        while True:
            video_num = self.API.get_video_num(self.mid)
            if video_num > self.old_video_num:
                self.logger.info('Found A new video')
                sleep(10)  # 需要增加延迟，反正B站API未即时更新，防止返回上一个视频
                video_info = self.API.get_video(self.mid)
                bot(f'[烤肉提示] [Bilibili]{video_info.get("Title")} 链接: {video_info.get("Ref")}')
                self.old_video_num = video_num
            else:
                self.logger.info(f'{self.mid}:{video_num} Not found new videos')
            sleep(sec)

    def run(self) -> None:
        self.check()
