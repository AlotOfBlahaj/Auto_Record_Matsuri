from bilibili_api.bilibili_api import *
from tools import get_logger, bot


class Bilibili:
    def __init__(self):
        self.API = BilibiliAPI()
        self.mid = None
        self.logger = get_logger(__name__)
        self.old_video_num = None

    async def check(self, mid):
        self.mid = mid
        self.old_video_num = await self.API.get_video_num(self.mid)
        video_num = await self.API.get_video_num(self.mid)
        if video_num > self.old_video_num:
            self.logger.info('Found A new video')
            video_info = await self.API.get_video(self.mid)
            await bot(f'[烤肉提示] [Bilibili]{video_info.get("Title")} 链接: {video_info.get("Ref")}')
            self.old_video_num = video_num
        else:
            self.logger.info(f'Not found new videos, {mid}:{video_num}')
