import json
import time
import subprocess
from config import sec
from tools import gethtml, echo_log


class Mirrativ:

    def __init__(self, userid, enable_proxy, proxy, ddir):
        self.ddir = ddir
        self.id = userid
        self.enable_proxy = enable_proxy
        if enable_proxy == 1:
            self.dl_proxy = '--https-proxy ' + f'"http://{proxy}"'
            self.proxy = proxy
        else:
            self.proxy = ''

    def live_info(self):
        l_info = json.loads(gethtml(f'https://www.mirrativ.com/api/user/profile?user_id={self.id}',
                                    self.enable_proxy, self.proxy))
        nowlive = l_info['onlive']
        if nowlive:
            return nowlive['live_id']

    def get_hsl(self):
        live_id = self.live_info()
        hsl_info = json.loads(gethtml(f'https://www.mirrativ.com/api/live/live?live_id={live_id}',
                                      self.enable_proxy, self.proxy))
        title = hsl_info['shares']['twitter']['card']['title']
        steaming_url = hsl_info['streaming_url_hls']
        self.downloader(steaming_url, title)

    def downloader(self, url, title):
        # ff = ffmpy.FFmpeg(inputs={f'{url}': None}, outputs={f'{ddir}/{title}.ts': '-c:v copy -c:a copy'})
        # ff.run()
        subprocess.run(
            "streamlink --hls-live-restart --loglevel trace "
            f"{self.proxy} -o {self.ddir}/{title}.ts {url} best")
        echo_log('Mirrativ' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                 f'{title} was already downloaded')

    def check(self):
        is_live = self.live_info()
        if is_live:
            self.get_hsl()
        else:
            echo_log('Mirrativ' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Not found Live, after {sec}s checking')
