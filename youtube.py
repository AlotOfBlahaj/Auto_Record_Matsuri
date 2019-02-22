import json
import os
import time
import subprocess
from config import sec, host, group_id
from tools import gethtml, echo_log

is_live = False


class Youtube:
    # ydl品质表
    _ydl_quality = {'720p': '22', '1080p': '137+141'}

    def __init__(self, channel_id, enable_proxy, proxy, ddir, api_key, quality, download_in_live):
        self.channel_id = channel_id
        self.api_key = api_key
        self.ddir = ddir
        self.download_in_live = download_in_live
        self.enable_proxy = enable_proxy
        # 代理设置
        if self.enable_proxy == 1:
            self.proxy = proxy
            if self.download_in_live == 0:
                self.dl_proxy = f'--proxy http://{proxy}'
            else:
                # 此处最外层应为" 内层为'
                self.dl_proxy = '--https-proxy ' + f'"http://{proxy}"'
        else:
            self.proxy = ''
        # 品质设置
        if self.download_in_live == 0:
            self.quality = f'-f {Youtube._ydl_quality[quality]}'
        else:
            self.quality = quality
        self.html = gethtml(f'https://www.youtube.com/channel/{self.channel_id}/featured',
                            self.enable_proxy, self.proxy)

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    def get_videoid_by_channel_id(self):
        channel_info = json.loads(gethtml(rf'https://www.googleapis.com/youtube/v3/search?key={self.api_key}'
                                          rf'&channel_id={self.channel_id}&part=snippet,id&order=date&maxResults=5',
                                          self.enable_proxy, self.proxy))
        # 判断获取的数据是否正确
        if channel_info['items']:
            item = channel_info['items']
            vid = [x['id']['videoId'] for x in item]
            return vid

    def getlive_vid(self):
        vid = self.get_videoid_by_channel_id()
        for x in vid:
            live_info = json.loads(gethtml(rf'https://www.googleapis.com/youtube/v3/videos?id={x}&key={self.api_key}&'
                                           r'part=liveStreamingDetails,snippet', self.enable_proxy, self.proxy))
            # 判断视频是否正确
            if live_info['pageInfo']['totalResults'] != 1:
                raise ValueError
            # JSON中的数组将被转换为列表，此处使用[0]获得其中的数据
            item = live_info['items'][0]
            snippet = item['snippet']
            info_dict = {'Title': snippet['title'],
                         'Islive': snippet['liveBroadcastContent']}
            if info_dict.get('Islive') == 'live':
                return [x, info_dict['Title']]
            else:
                echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         f'{info_dict["Title"]} is not a live video')

    def judge(self):
        global is_live
        if not is_live:
            if 'LIVE NOW' in self.html:
                is_live = self.getlive_vid()
                bot(host, group_id, f'A live, {is_live[1]}, is streaming. url:  https://www.youtube.com/watch?v={is_live[0]}')         
                if self.download_in_live == 1:
                    echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                             'Found A Live, starting downloader')
                    self.downloader_live(r"https://www.youtube.com/watch?v=" + is_live[0], is_live[1])
                    is_live = False
                else:
                    echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                             'Found A Live, waiting for it to close')
            elif 'Upcoming live streams' in self.html:
                echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         f'Found A Live Upcoming, after {sec}s checking')
            else:
                echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         f'Not found Live, after {sec}s checking')
        else:
            if 'LIVE NOW' not in self.html:
                self.downloader(r"https://www.youtube.com/watch?v=" + is_live[0])
                echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         f'{is_live[1]} already downloaded')
            else:
                echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         'Found A Live, waiting for it to close')

    def downloader(self, link):
        while True:
            is_break = 0
            subprocess.run(rf"youtube-dl {self.quality} {self.dl_proxy} -o {self.ddir}/%(title)s.%(ext)s {link}")
            # os.system(rf"youtube-dl {self.quality} {self.proxy} -o {ddir}/%(title)s.%(ext)s {link}")
            for x in os.listdir(self.ddir):
                if '.part' in os.path.splitext(x):
                    is_break = 0
                else:
                    is_break = 1
            if is_break == 1:
                break
            else:
                echo_log('Youtube' + 'Download is broken. Retrying \n If the notice always happen, '
                                     'please delete the dir ".part" file')
            break
        global is_live
        is_live = False

    def downloader_live(self, link, title):
        while True:
            try:
                subprocess.run(
                    "streamlink --hls-live-restart --loglevel trace "
                    f"{self.dl_proxy} -o {self.ddir}/{title}.ts {link} {self.quality}")
                # 不应该使用os.system
                # os.system(f"streamlink --hls-live-restart {self.proxy} -o '{title}.ts' {link} {self.quality}")
                break
            except:
                echo_log('Youtube| Download is broken. Retrying')

    def check(self):
        self.judge()
