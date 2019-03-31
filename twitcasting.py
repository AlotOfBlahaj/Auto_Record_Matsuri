import json
import time

from lxml.html import etree

from config import sec
from tools import Aio, process_video, echo_log


class Twitcasting:
    def __init__(self):
        self.aio = Aio()

    async def live_info(self, twitcasting_id):
        live_js = json.loads(await self.aio.main(
            f"https://twitcasting.tv/streamserver.php?target={twitcasting_id}&mode=client", 'get'))
        nowlive = live_js['movie']['live']
        return nowlive

    async def get_hsl(self, twitcasting_id):
        html = await self.aio.main(f"https://twitcasting.tv/{twitcasting_id}", "get")
        dom = etree.HTML(html)
        title = dom.xpath('/html/body/div[3]/div[2]/div/div[2]/h2/span[3]/a/text()')[0]
        ref = f"https://twitcasting.tv/{twitcasting_id}/metastream.m3u8"
        target = f"https://twitcasting.tv/{twitcasting_id}"
        date = time.strftime("%Y-%m-%d", time.localtime())
        return {'Title': title,
                'Ref': ref,
                'Target': target,
                'Date': date}

    async def check(self, twitcasting_id):
        is_live = await self.live_info(twitcasting_id)
        if is_live:
            result = await self.get_hsl(twitcasting_id)
            await process_video(result, "Twitcasting")
        else:
            echo_log('Twitcasting' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Not found Live, after {sec}s checking')
