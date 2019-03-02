import json
import time
from config import sec, host, group_id
from tools import gethtml, echo_log, bot, bd_upload, downloader


class Youtube:

    def __init__(self, channel_id, enable_proxy, proxy, ddir, api_key, quality):
        self.channel_id = channel_id
        self.api_key = api_key
        self.ddir = ddir
        self.enable_proxy = enable_proxy
        # 代理设置
        if self.enable_proxy == 1:
            self.proxy = proxy
            self.dl_proxy = '--https-proxy ' + f'"http://{proxy}"'
        else:
            self.proxy = ''
            self.dl_proxy = ''
        # 品质设置
        self.quality = quality
        self.html = gethtml(f'https://www.youtube.com/channel/{self.channel_id}/featured',
                            self.enable_proxy, self.proxy)

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    def get_videoid_by_channel_id(self):
        channel_info = json.loads(gethtml(rf'https://www.googleapis.com/youtube/v3/search?key={self.api_key}'
                                          rf'&channelId={self.channel_id}&part=snippet,id&order=date&maxResults=5',
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
                return {'Title': info_dict['Title'],
                        'Ref': x}
            else:
                echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         f'{info_dict["Title"]} is not a live video')

    def judge(self):
        if 'LIVE NOW' in self.html:
            is_live = self.getlive_vid()
            bot(host, group_id,
                f"A live, {is_live.get('Title')}, is streaming. url:  https://www.youtube.com/watch?v={is_live['Ref']}")
            echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     'Found A Live, starting downloader')
            downloader(r"https://www.youtube.com/watch?v=" + is_live['Ref'], is_live['Title'],
                       self.dl_proxy, self.quality)
            echo_log("Youtube" + time.strftime("|%m-%d %H:%M:%S|", time.localtime(time.time())) +
                     f"{is_live['Title']} was already downloaded")
            bot(host, group_id,
                f"{is_live['Title']} is already downloaded")
            share = bd_upload(f"{is_live['Title']}.ts")
            bot(host, group_id, share)
        elif 'Upcoming live streams' in self.html:
            echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Found A Live Upcoming, after {sec}s checking')
        else:
            echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Not found Live, after {sec}s checking')

    def check(self):
        self.judge()
