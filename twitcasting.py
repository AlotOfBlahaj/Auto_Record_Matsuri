import time

from daemon import VideoDaemon
from tools import get_logger, get_json, while_warp
from video_process import process_video


class Twitcasting(VideoDaemon):
    def __init__(self, target_id):
        super().__init__(target_id)
        self.logger = get_logger('Twitcasting')
        self.module = 'Twitcasting'

    def live_info(self):
        live_js = get_json(
            f"https://twitcasting.tv/streamserver.php?target={self.target_id}&mode=client")
        is_live = live_js['movie']['live']
        vid = str(live_js['movie']['id'])
        live_info = {"Is_live": is_live,
                     "Vid": vid}
        return live_info

    def get_hsl(self, live_info):
        # html = get(f"https://twitcasting.tv/{twitcasting_id}")
        # dom = etree.HTML(html)
        # title = dom.xpath('/html/body/div[3]/div[2]/div/div[2]/h2/span[3]/a/text()')[0]
        title = f"{self.target_id}#{live_info.get('Vid')}"
        ref = f"https://twitcasting.tv/{self.target_id}/metastream.m3u8"
        target = f"https://twitcasting.tv/{self.target_id}"
        date = time.strftime("%Y-%m-%d", time.localtime())
        return {'Title': title,
                'Ref': ref,
                'Target': target,
                'Date': date,
                'User': self.target_id}

    @while_warp
    def check(self):
        try:
            live_info = self.live_info()
            if live_info.get('Is_live'):
                video_dict = self.get_hsl(live_info)
                video_dict['Provide'] = self.module
                process_video(video_dict)
            else:
                self.logger.info(f'{self.target_id}: Not found Live')
        except Exception:
            self.logger.exception('Check Failed')
