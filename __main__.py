from urllib import request
import json
import os
import time
# TODO: 夜间停止监控
# 代理地址，应使用http代理
proxy = '127.0.0.1:10800'
# 保存位置
ddir = 'D:/matsuri'
# YoutubeAPI3Key 申请地址：https://console.developers.google.com/apis/library/youtube.googleapis.com?q=Youtube&id=125bab65-cfb6-4f25-9826-4dcc309bc508&project=youtube-streaming-231512
ApiKey = ''
# 监测频道ID
ChannelID = 'UCQ0UDLQCjY0rmuxCDE38FGg'
# 检测间隔时间（s）
sec = 30


def gethtml(url):
    proxy_support = request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/71.0.3578.53 Safari/537.36'
    req = request.Request(url, headers={'User-Agent': user_agent})
    response = request.urlopen(req)
    html = response.read()
    html = html.decode('utf-8', 'ignore')
    # 防止网络问题导致抓取错误
    if html:
        return html
    else:
        return gethtml(url)


def downloader(link):
    while True:
        os.system(r"youtube-dl --proxy http://{} -o {}/%(title)s.%(ext)s {}".format(proxy, ddir, link))
        print('Download is broken. Retring \n If the notice always happend, please delete the dir ".part" file')
        if '.part' not in os.listdir(ddir):
            break


class Check(object):

    def __init__(self):
        # Caches
        self.caches_livestatus = {'Live': [], 'Upcoming': []}
        if not self.caches_livestatus['Upcoming']:
            self.html = gethtml('https://www.youtube.com/channel/{}/featured'.format(ChannelID))
        self.ChannelID = ChannelID
        while True:
            try:
                self.live_check_timer()
                time.sleep(sec)
            except:
                print('Something wrong. Retrying')
                time.sleep(5)

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    def get_videoid_by_channelid(self):
        channel_info = json.loads(gethtml(r'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}'
                                          r'&part=snippet,id&order=date&maxResults=5'.format(ApiKey, self.ChannelID)))
        # 判断获取的数据是否正确
        if channel_info['items']:
            vid = []
            item = channel_info['items']
            for x in item:
                vid.append(x['id']['videoId'])
            return vid

    def getlive_info(self):
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
                return vid[vid.index(x)]
            elif info_dict.get('Islive') == 'upcoming':
                return vid[vid.index(x)]
            else:
                print(time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                      '{} is not a live video'.format(info_dict['Title']))

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
            else:
                break

    def live_check_timer(self):
        if not self.caches_livestatus['Upcoming']:
            if 'LIVE NOW' in self.html:
                vid = self.getlive_info()
                if vid in self.caches_livestatus['Upcoming']:
                    del self.caches_livestatus['Upcoming'][self.caches_livestatus['Upcoming'].index(vid)]
                downloader(r"https://www.youtube.com/watch?v=" + vid)
            elif 'Upcoming live streams' in self.html:
                vid = self.getlive_info()
                if vid not in self.caches_livestatus['Upcoming']:
                    self.caches_livestatus['Upcoming'].append(vid)
                self.getlive_info_by_caches()
                self.caches_livestatus['Live'].append(vid)
                downloader(r"https://www.youtube.com/watch?v=" + vid)
                del self.caches_livestatus['Upcoming'][self.caches_livestatus['Upcoming'].index(vid)]
        else:
            raise IOError



if __name__ == '__main__':
    Check()
