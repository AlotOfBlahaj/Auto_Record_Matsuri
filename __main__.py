from urllib import request
import json
import os
import time
from retry import retry

url = "https://www.youtube.com/channel/UCQ0UDLQCjY0rmuxCDE38FGg/videos"
# 代理地址，应使用http代理
proxy = '127.0.0.1:10800'
# 保存位置
ddir = 'D:/matsuri'
# YoutubeAPI3Key 申请地址：https://console.developers.google.com/apis/library/youtube.googleapis.com?q=Youtube&id=125bab65-cfb6-4f25-9826-4dcc309bc508&project=youtube-streaming-231512
ApiKey = ''
# 监测频道ID
ChannelID = 'UCQ0UDLQCjY0rmuxCDE38FGg'
# 检测间隔时间（s）
sec = 15

@retry(delay=5)
def getHtml(url):
    proxy_support = request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/71.0.3578.53 Safari/537.36'
    req = request.Request(url, headers={'User-Agent': user_agent})
    try:
        response = request.urlopen(req)
    except:
        error()
    html = response.read()
    html = html.decode('utf-8', 'ignore')
    # 防止网络问题导致抓取错误
    if html:
        return html
    else:
        return getHtml(url)


# 应某超绝要求，此处应该有retry
@retry()
def downloader(link):
    try:
        os.system(r"youtube-dl --proxy http://{} -o {}/%(title)s.%(ext)s {}".format(proxy, ddir, link))
    except:
        error()


# 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
def GetVedioIDByChannelID(ChannelID):
    Channel_Info = json.loads(getHtml(r'https://www.googleapis.com/youtube/v3/search?key={}&channelId={}'
                                      r'&part=snippet,id&order=date&maxResults=5'.format(ApiKey, ChannelID)))
    # 判断获取的数据是否正确
    if Channel_Info['items']:
        vid = []
        item = Channel_Info['items']
        for x in item:
            vid.append(x['id']['videoId'])
        return vid
    error()


def GetLive_info(vid):
    for x in vid:
        live_info = json.loads(getHtml(r'https://www.googleapis.com/youtube/v3/videos?id={}&key={}&'
                                       r'part=liveStreamingDetails,snippet'.format(x, ApiKey)))
        # 判断视频是否正确
        if live_info['pageInfo']['totalResults'] != 1:
            error()
        # JSON中的数组将被转换为列表，此处使用[0]获得其中的数据
        item = live_info['items'][0]
        snippet = item['snippet']
        info_dict = {'Title': snippet['title'],
                     'Islive': snippet['liveBroadcastContent']}
        # 判断是否正在直播
        if info_dict.get('Islive') == 'live':
            vid = vid[vid.index(x)]
            link = r"https://www.youtube.com/watch?v=" + vid
            downloader(link)
        else:
            print(time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                  '{} is not living now or not a live video'.format(info_dict['Title'], info_dict['Title']))


def main():
    GetLive_info(GetVedioIDByChannelID(ChannelID))
    print('Now Channel is not streaming, program will sleep {}s to retry'.format(sec))
    time.sleep(sec)

def error():
    print("Something Wrong")
    #此处raise一个错误使得能够retry
    raise ValueError

if __name__ == '__main__':
    while True:
        main()
