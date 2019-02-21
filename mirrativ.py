import json
import time

import ffmpy

from config import *
from tools import gethtml


# from subprocess import PIPE, Popen, STDOUT


class Mirrativ:

    def __init__(self):
        self.id = userid

    @staticmethod
    def live_info():
        l_info = json.loads(gethtml('https://www.mirrativ.com/api/user/profile?user_id={}'.format(userid)))
        nowlive = l_info['onlive']
        if nowlive:
            return nowlive['live_id']

    def get_hsl(self):
        live_id = self.live_info()
        hsl_info = json.loads(gethtml(f'https://www.mirrativ.com/api/live/live?live_id={live_id}'))
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        self.downloader(steaming_url, title)

    @staticmethod
    def downloader(url, title):
        ff = ffmpy.FFmpeg(inputs={f'{url}': None}, outputs={f'{ddir}/{title}.ts': '-c:v copy -c:a copy'})
        ff.run()
        # p = Popen(['ffmpeg', '-i', f'{url}', f"{ddir}/{title}.ts", '-c:v', 'copy',
        #            '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        # try:
        #     p.communicate()
        # except KeyboardInterrupt:
        #     p.stdin.write('q'.encode('utf-8'))

    def check(self):
        is_live = self.live_info()
        if is_live:
            self.get_hsl()
        else:
            print('Mirrativ' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                  'Not found Live, after {}s checking'.format(sec))
