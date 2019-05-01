import time
from multiprocessing import Process

from config import sec
from daemon import VideoDaemon
from queues import mirrativ_queue
from tools import get_json, get_logger


class Mirrativ(VideoDaemon):

    def __init__(self):
        super().__init__(mirrativ_queue)
        self.logger = get_logger('Mirrativ')

    @staticmethod
    def get_live_info(userid):
        live_info = get_json(f'https://www.mirrativ.com/api/user/profile?user_id={userid}')
        nowlive = live_info['onlive']
        if nowlive:
            return nowlive['live_id']

    @staticmethod
    def get_hsl(is_live):
        hsl_info = get_json(f'https://www.mirrativ.com/api/live/live?live_id={is_live}')
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        target = hsl_info['share_url']
        date = time.strftime("%Y-%m-%d", time.localtime())
        return {'Title': title,
                'Ref': steaming_url,
                'Target': target,
                'Date': date}

    def check(self, userid):
        is_live = self.get_live_info(userid)
        if is_live:
            is_live = self.get_hsl(is_live)
            return is_live, {'Module': 'Mirrativ', 'Target': userid}
        self.logger.info(f'Not found Live, after {sec}s checking')
        self.return_and_sleep(userid, 'Mirrativ')

    def actor(self, userid):
        proc = Process(target=self.check, args=(userid,))
        proc.start()
