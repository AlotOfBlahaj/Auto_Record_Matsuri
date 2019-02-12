from you_get.extractors import *
from you_get.extractors.youtube import YouTube


url = "https://www.youtube.com/channel/UCKMYISTJAQ8xTplUPHiABlA/videos"
# 代理地址，应使用http代理
proxy = '127.0.0.1:10800'
# 保存位置
ddir = 'D:/matsuri'
set_socks_proxy(proxy)

def getHtml(url):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/71.0.3578.53 Safari/537.36'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    html = response.read()
    html = html.decode('utf-8')
    # 防止网络问题导致抓取错误
    if html == None:
        getHtml(url)
    else:
        return html


def getLink(html):
    global urllist
    reg = r"watch\?v=([A-Za-z0-9_-]{11})"
    urlre = re.compile(reg)
    urllist = re.findall(urlre, html)
    link = r"https://www.youtube.com/watch?v=" + urllist[0]
    return link


def downloader(link):
    os.system(r"youtube-dl --proxy http://{} -o {}/%(title)s.%(ext)s {}".format(proxy, ddir, link))
    monitors1(getLink(getHtml(url)))


def monitors1(link):
    '''
   * Licensed same as jquery - MIT License
   * http://www.opensource.org/licenses/mit-license.php
    '''

    vid = urllist[0]
    try:
        video_info = parse.parse_qs(get_content(r'https://www.youtube.com/get_video_info?video_id={}'.format(vid)))
    except:
        log.w("Network is disconnected retrying")
        time.sleep(5)
        monitors1(link)

    ytplayer_config = None
    if video_info['status'] == ['ok']:
        if 'use_cipher_signature' not in video_info or video_info['use_cipher_signature'] == ['False']:
            YouTube.title = parse.unquote_plus(video_info['title'][0])
            # Parse video page (for DASH)
            video_page = get_content('https://www.youtube.com/watch?v=%s' % vid)
            try:
                ytplayer_config = json.loads(re.search(r'ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))
                YouTube.html5player = 'https://www.youtube.com' + ytplayer_config['assets']['js']
                # Workaround: get_video_info returns bad s. Why?
            except:
                YouTube.html5player = None
        else:
            # Parse video page instead
            video_page = get_content('https://www.youtube.com/watch?v=%s' % vid)
            ytplayer_config = json.loads(re.search(r'ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))
            YouTube.title = ytplayer_config['args']['title']
            YouTube.html5player = 'https://www.youtube.com' + ytplayer_config['assets']['js']
    # 判断是否正在直播
    if ytplayer_config and (ytplayer_config['args'].get('livestream') == '1'):
        downloader(link)
    else:
        log.i('Now is not streaming')
        time.sleep(15)
        monitors1(getLink(getHtml(url)))



monitors1(getLink(getHtml(url)))
