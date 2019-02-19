import json
import time
from subprocess import PIPE, Popen

from config import *
from tools import gethtml


class Mirrativ:

    def __init__(self):
        self.id = userid

    def live_info(self):
        l_info = json.loads(gethtml('https://www.mirrativ.com/api/user/profile?user_id={}'.format(userid)))
        nowlive = l_info['onlive']
        if nowlive != None:
            return nowlive['live_id']
        else:
            print('Mirrativ' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                  'Not found Live, after {}s checking'.format(sec))
            return None

    def get_hsl(self):
        live_id = self.live_info()
        hsl_info = json.loads(gethtml(f'https://www.mirrativ.com/api/live/live?live_id={live_id}'))
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        self.downloader(steaming_url, title)

    def downloader(self, url, title):
        try:
            p = Popen(['ffmpeg', '-i', f'{url}', f"{ddir}/{title}.ts", '-c:v', 'copy',
                       '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc'], stdin=PIPE)
        except KeyboardInterrupt:
            p.stdin.write('q'.encode('utf-8'))
    def check(self):
        is_live = self.live_info()
        if is_live:
            self.get_hsl()
