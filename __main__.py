from urllib import request
from urllib import parse
import json
import re
import os
import time
from retry import retry

url = "https://www.youtube.com/channel/UCQ0UDLQCjY0rmuxCDE38FGg/videos"
# 代理地址，应使用http代理
proxy = '127.0.0.1:10800'
# 保存位置
ddir = 'D:/matsuri'


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

@retry(delay=5)
def getvideo_id(html):
    global vid
    reg = r"watch\?v=([A-Za-z0-9_-]{11})"
    idre = re.compile(reg)
    try:
        vid = re.search(idre, html).group(1)
    except:
        error()


def getLink():
    link = r"https://www.youtube.com/watch?v=" + vid
    return link

# 应某超绝要求，此处应该有retry
@retry()
def downloader(link):
    try:
        os.system(r"youtube-dl --proxy http://{} -o {}/%(title)s.%(ext)s {}".format(proxy, ddir, link))
    except:
        error()
    #main()

@retry(delay=5)
def monitors1(link):
    '''
   * Licensed same as jquery - MIT License
   * http://www.opensource.org/licenses/mit-license.php
   * Copyright (c) 2012-2019 Mort Yao <mort.yao@gmail.com>
   * Copyright (c) 2012 Boyu Guo <iambus@gmail.com>
    '''
    try:
        video_info = parse.parse_qs(getHtml(r'https://www.youtube.com/get_video_info?video_id={}'.format(vid)))
    except:
        error()
    ytplayer_config = None
    if video_info['status'] == ['ok']:
        if 'use_cipher_signature' not in video_info or video_info['use_cipher_signature'] == ['False']:
            # Parse video page (for DASH)
            try:
                video_page = getHtml('https://www.youtube.com/watch?v=%s' % vid)
            except:
                error()
            try:
                ytplayer_config = json.loads(re.search(r'ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))
                # Workaround: get_video_info returns bad s. Why?
            except:
                error()
        else:
            # Parse video page instead
            try:
                video_page = getHtml('https://www.youtube.com/watch?v=%s' % vid)
            except:
                error()
            ytplayer_config = json.loads(re.search(r'ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))

    # 判断是否正在直播
    if ytplayer_config and (ytplayer_config['args'].get('livestream') == '1'):
        downloader(link)
    else:
        print('Now is not streaming')
        time.sleep(15)
        #main()


def main():
    getvideo_id(getHtml(url))
    monitors1(getLink())


def error():
    print("Something Wrong Retrying")
    raise ValueError

if __name__ == '__main__':
    while True:
        main()
