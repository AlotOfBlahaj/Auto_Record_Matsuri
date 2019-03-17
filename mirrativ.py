import json
import time

from config import sec
from tools import Aio, echo_log, process_video


class Mirrativ:

    def __init__(self, userid):
        self.id = userid
        self.Aio = Aio()

    async def live_info(self):
        l_info = json.loads(await self.Aio.fetch_html(f'https://www.mirrativ.com/api/user/profile?user_id={self.id}'))
        nowlive = l_info['onlive']
        if nowlive:
            return nowlive['live_id']

    async def get_hsl(self):
        live_id = self.live_info()
        hsl_info = json.loads(await self.Aio.fetch_html(f'https://www.mirrativ.com/api/live/live?live_id={live_id}'))
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        return {'Title': title,
                'Ref': steaming_url}

    async def check(self):
        is_live = await self.live_info()
        if is_live:
            is_live = await self.get_hsl()
            await process_video(is_live, 'Mirrativ')
        else:
            echo_log('Mirrativ' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Not found Live, after {sec}s checking')
