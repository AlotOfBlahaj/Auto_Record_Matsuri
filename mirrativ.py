import json
import time

from config import sec
from tools import fetch_html, echo_log, process_video


class Mirrativ:

    def __init__(self, userid):
        self.id = userid

    def live_info(self):
        l_info = json.loads(fetch_html(f'https://www.mirrativ.com/api/user/profile?user_id={self.id}'))
        nowlive = l_info['onlive']
        if nowlive:
            return nowlive['live_id']

    def get_hsl(self):
        live_id = self.live_info()
        hsl_info = json.loads(fetch_html(f'https://www.mirrativ.com/api/live/live?live_id={live_id}'))
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        return {'Title': title,
                'Ref': steaming_url}

    def check(self):
        is_live = self.live_info()
        if is_live:
            is_live = self.get_hsl()
            process_video(is_live, 'Mirrativ')
        else:
            echo_log('Mirrativ' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Not found Live, after {sec}s checking')
