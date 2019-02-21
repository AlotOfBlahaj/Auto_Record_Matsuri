import json
import os
import time

from config import *
from tools import gethtml

is_live = False


class Youtube:

    def __init__(self):
        self.ChannelID = ChannelID
        self.html = gethtml('https://www.youtube.com/channel/{}/featured'.format(ChannelID))

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    def get_videoid_by_channelid(self):
        channel_info = json.loads(gethtml(rf'https://www.googleapis.com/youtube/v3/search?key={ApiKey}'
                                          rf'&channelId={self.ChannelID}&part=snippet,id&order=date&maxResults=5'))
        # 判断获取的数据是否正确
        if channel_info['items']:
            item = channel_info['items']
            vid = [x['id']['videoId'] for x in item]
            return vid

    def getlive_vid(self):
        vid = self.get_videoid_by_channelid()
        for x in vid:
            live_info = json.loads(gethtml(rf'https://www.googleapis.com/youtube/v3/videos?id={x}&key={ApiKey}&'
                                           r'part=liveStreamingDetails,snippet'))
            # 判断视频是否正确
            if live_info['pageInfo']['totalResults'] != 1:
                raise ValueError
            # JSON中的数组将被转换为列表，此处使用[0]获得其中的数据
            item = live_info['items'][0]
            snippet = item['snippet']
            info_dict = {'Title': snippet['title'],
                         'Islive': snippet['liveBroadcastContent']}
            if info_dict.get('Islive') == 'live':
                return x
            else:
                print('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      f'{info_dict["Title"]} is not a live video')

    def judge(self):
        global is_live
        if not is_live:
            if 'LIVE NOW' in self.html:
                is_live = self.getlive_vid()
                print('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Found A Live, waiting for it to close'.format(sec))
            elif 'Upcoming live streams' in self.html:
                print('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Found A Live Upcoming, after {}s checking'.format(sec))
            else:
                print('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Not found Live, after {}s checking'.format(sec))
        else:
            if 'LIVE NOW' not in self.html:
                self.downloader(r"https://www.youtube.com/watch?v=" + is_live)
            else:
                print('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Found A Live, waiting for it to close'.format(sec))

    @staticmethod
    def downloader(link):
        while True:
            if ydl == 1:
                is_break = 0
                os.system(rf"youtube-dl -f 22 --proxy http://{proxy} -o {ddir}/%(title)s.%(ext)s {link}")
                for x in os.listdir(ddir):
                    if '.part' in os.path.splitext(x):
                        is_break = 0
                    else:
                        is_break = 1
                if is_break == 1:
                    break
                else:
                    print('Youtube' + 'Download is broken. Retring \n If the notice always happend, '
                                      'please delete the dir ".part" file')
            if yget == 1:
                os.system(rf"you-get -x {proxy} --itag=22 -o {ddir} {link}")
                break
        global is_live
        is_live = False

    def check(self):
        self.judge()
