import time

from daemon import VideoDaemon
from tools import get_json, get_logger, while_warp
from video_process import process_video


class Mirrativ(VideoDaemon):

    def __init__(self, target_id):
        super().__init__(target_id)
        self.logger = get_logger('Mirrativ')
        self.module = 'Mirrativ'

    def get_live_info(self):
        live_info = get_json(f'https://www.mirrativ.com/api/user/profile?user_id={self.target_id}')
        nowlive = live_info['onlive']
        try:
            if nowlive:
                live_id = nowlive['live_id']
                return live_id
            return None
        except KeyError:
            self.logger.exception('Get live info error')

    @staticmethod
    def get_hsl(is_live):
        hsl_info = get_json(f'https://www.mirrativ.com/api/live/live?live_id={is_live}')
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        target = hsl_info['share_url']
        date = time.strftime("%Y-%m-%d", time.localtime())
        live_dict = {'Title': title,
                     'Ref': steaming_url,
                     'Target': target,
                     'Date': date}
        return live_dict

    @while_warp
    def check(self):
        is_live = self.get_live_info()
        if is_live:
            video_dict = self.get_hsl(is_live)
            video_dict['Provide'] = self.module
            process_video(video_dict)
        self.logger.info(f'{self.target_id}: Not found Live')
