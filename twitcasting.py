import time
from multiprocessing import Process

from lxml.html import etree

from config import sec
from daemon import VideoDaemon
from queues import twitcasting_queue
from tools import get_logger, get_json, get


class Twitcasting(VideoDaemon):
    def __init__(self):
        super().__init__(twitcasting_queue)
        self.logger = get_logger('Twitcasting')

    @staticmethod
    def live_info(twitcasting_id):
        live_js = get_json(
            f"https://twitcasting.tv/streamserver.php?target={twitcasting_id}&mode=client")
        is_live = live_js['movie']['live']
        vid = str(live_js['movie']['id'])
        live_info = {"Is_live": is_live,
                     "Vid": vid}
        return live_info

    @staticmethod
    def get_hsl(twitcasting_id, live_info):
        html = get(f"https://twitcasting.tv/{twitcasting_id}")
        dom = etree.HTML(html)
        title = dom.xpath('/html/body/div[3]/div[2]/div/div[2]/h2/span[3]/a/text()')[0]
        title += '|' + live_info.get('Vid')
        ref = f"https://twitcasting.tv/{twitcasting_id}/metastream.m3u8"
        target = f"https://twitcasting.tv/{twitcasting_id}"
        date = time.strftime("%Y-%m-%d", time.localtime())
        return {'Title': title,
                'Ref': ref,
                'Target': target,
                'Date': date}

    def check(self, twitcasting_id):
        live_info = self.live_info(twitcasting_id)
        if live_info.get('Is_live'):
            result = self.get_hsl(twitcasting_id, live_info)
            self.put_download([result, {'Module': 'Twitcasting', 'Target': twitcasting_id}])
        else:
            self.logger.info(f'Not found Live, after {sec}s checking')
            self.return_and_sleep(twitcasting_id, 'Twitcasting')

    def actor(self, twitcasting_id):
        proc = Process(target=self.check, args=(twitcasting_id,))
        proc.start()
