from urllib import request
from config import proxy, enable_proxy
from time import strftime, localtime, time
from os import getcwd

def gethtml(url):
    if enable_proxy == 1:
        proxy_support = request.ProxyHandler({'http': '%s' % proxy, 'https': '%s' % proxy})
        opener = request.build_opener(proxy_support)
        request.install_opener(opener)
    fake_headers = {
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
    }
    req = request.Request(url, headers=fake_headers)
    response = request.urlopen(req)
    html = response.read()
    html = html.decode('utf-8', 'ignore')
    return html


def echo_log(log):
    today = strftime('%m-%d', localtime(time()))
    print(log)
    with open(getcwd() + rf"\log\log-{today}.log", 'a') as logs:
        logs.write(log + "\n")
