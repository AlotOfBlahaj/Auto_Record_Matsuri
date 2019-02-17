import json
import os
import time
from tools import gethtml
from config import *


class Youtube(object):
    def __init__(self):
        self.ChannelID = ChannelID

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    def get_videoid_by_channelid(self):
        channel_info = json.loads(gethtml(r'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}'
                                          r'&part=snippet,id&order=date&maxResults=3'.format(ApiKey, self.ChannelID)))
        # 判断获取的数据是否正确
        if channel_info['items']:
            vid = []
            item = channel_info['items']
            for x in item:
                vid.append(x['id']['videoId'])
            return vid

    def getlive_vid(self):
        vid = self.get_videoid_by_channelid()
        for x in vid:
            live_info = json.loads(gethtml(r'https://www.googleapis.com/youtube/v3/videos?id={}&key={}&'
                                           r'part=liveStreamingDetails,snippet'.format(x, ApiKey)))
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
                print('Youtube|' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      '{} is not a live video'.format(info_dict['Title']))
                return None

    def judge(self):
            if 'LIVE NOW' in self.html:
                vid = self.getlive_vid()
                if vid:
                    self.downloader(r"https://www.youtube.com/watch?v=" + vid)
            elif 'Upcoming live streams' in self.html:
                print('Youtube|' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Found A Live Upcoming, after {}s checking'.format(sec))
            else:
                print('Youtube|' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Not found Live, after {}s checking'.format(sec))

    def downloader(self,link):
        while True:
            os.system(r"youtube-dl --proxy http://{} -o {}/%(title)s.%(ext)s {}".format(proxy, ddir, link))
            print('Youtube|' + 'Download is broken. Retring \n If the notice always happend, '
                               'please delete the dir ".part" file')
            if '.part' not in os.listdir(ddir):
                break

    def check(self):
        try:
            self.html = gethtml('https://www.youtube.com/channel/{}/featured'.format(ChannelID))
            self.judge()
            time.sleep(sec)
        except:
            print('Youtube|' + 'Something wrong. Retrying')
            time.sleep(sec_error)
