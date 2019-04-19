import json

from tools import Aio


class BilibiliAPI:
    def __init__(self):
        self.aio = Aio()

    async def get_video_num(self, mid: int) -> int:
        nav_info = json.loads(
            await self.aio.main(f'https://api.bilibili.com/x/space/navnum?mid={mid}&jsonp=jsonp', 'get'))
        video_num = nav_info['data']['video']
        return video_num

    async def get_video(self, mid: int) -> dict:
        video_info = json.loads(await self.aio.main(
            f'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=1&tid=0&page=1&keyword=&order=pubdate',
            'get'))
        video = video_info['data']['vlist'][0]
        title = video['title']
        ref = f"https://www.bilibili.com/video/av{video['aid']}"
        return {'Title': title,
                'Ref': ref}
