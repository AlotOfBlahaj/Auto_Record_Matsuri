from urllib import request
import json
import os
import time

# 代理地址，应使用http代理
proxy = '127.0.0.1:10800'
# 保存位置
ddir = 'D:/matsuri'
# YoutubeAPI3Key 申请地址：https://console.developers.google.com/apis/library/youtube.googleapis.com?q=Youtube&id=125bab65-cfb6-4f25-9826-4dcc309bc508&project=youtube-streaming-231512
ApiKey = ''
# 监测频道ID
ChannelID = 'UCQ0UDLQCjY0rmuxCDE38FGg'
# 检测间隔时间（s）
sec = 120
# 无预定时间隔时间（s）
sec1 = 120


def gethtml(url):
    proxy_support = request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)
    fake_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'UTF-8,*;q=0.5',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
    }
    req = request.Request(url, headers=fake_headers)
    response = request.urlopen(req)
    html = response.read()
    html = html.decode('utf-8', 'ignore')
    # 防止网络问题导致抓取错误
    return html


def downloader(link):
    while True:
        os.system(r"youtube-dl --proxy http://{} -o {}/%(title)s.%(ext)s {}".format(proxy, ddir, link))
        print('Download is broken. Retring \n If the notice always happend, please delete the dir ".part" file')
        if '.part' not in os.listdir(ddir):
            break


class Check(object):
    def __init__(self):
        self.ChannelID = ChannelID
        # Caches
        self.caches_livestatus = {'Live': [], 'Upcoming': []}
        while True:
            if not self.caches_livestatus['Upcoming']:
                self.html = gethtml('https://www.youtube.com/channel/{}/featured'.format(ChannelID))
            try:
                self.live_check_timer()
                time.sleep(sec1)
            except:
                print('Something wrong. Retrying')
                time.sleep(5)

# TODO:添加提示文本
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

    def getlive_info(self):
        vid = self.get_videoid_by_channelid()
        vid1 = []
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
                vid1.append(vid[vid.index(x)])
            elif info_dict.get('Islive') == 'upcoming':
                vid1.append(vid[vid.index(x)])
            else:
                print(time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      '{} is not a live video'.format(info_dict['Title']))
        return vid1

    def getlive_info_by_caches(self):
        vid = self.caches_livestatus['Upcoming']
        while True:
            for x in vid:
                live_info = json.loads(gethtml(r'https://www.googleapis.com/youtube/v3/videos?id={}&key={}'
                                               r'&part=liveStreamingDetails,snippet'.format(x, ApiKey)))
                if live_info['pageInfo']['totalResults'] != 1:
                    raise ValueError
                item = live_info['items'][0]
                snippet = item['snippet']
                info_dict = {'Title': snippet['title'],
                             'Islive': snippet['liveBroadcastContent']}
                if info_dict.get('Islive') == 'live':
                    return vid[vid.index(x)]
                elif info_dict.get('Islive') == 'none':
                    break
            print(time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                  '{} is not streaming now'.format(info_dict['Title']))
            time.sleep(sec)

    def live_check_timer(self):
            if 'LIVE NOW' in self.html:
                vid = self.getlive_info()
                for x in vid:
                    if x in self.caches_livestatus['Upcoming']:
                        del self.caches_livestatus['Upcoming'][self.caches_livestatus['Upcoming'].index(x)]
                    downloader(r"https://www.youtube.com/watch?v=" + x)
            elif 'Upcoming live streams' in self.html:
                vid = self.getlive_info()
                for x in vid:
                    if vid not in self.caches_livestatus['Upcoming']:
                        self.caches_livestatus['Upcoming'].append(x)
                    vid = self.getlive_info_by_caches()
                    self.caches_livestatus['Live'].append(vid)
                    downloader(r"https://www.youtube.com/watch?v=" + vid)
                    del self.caches_livestatus['Upcoming'][self.caches_livestatus['Upcoming'].index(x)]
            else:
                print(time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      'Not found Live Upcoming, after {}s checking'.format(sec1))


if __name__ == '__main__':
    Check()
