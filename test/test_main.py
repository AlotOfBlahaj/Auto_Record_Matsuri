import pytest
import sys

from mirrativ import Mirrativ
from youtube import Youtube
from os import getcwd

sys.path.insert(0, '..')


def test_mirrativ():
    userid = '3264432'
    ddir = getcwd()
    enable_proxy = 0
    proxy = ''
    m = Mirrativ(userid, enable_proxy, proxy, ddir)
    m.check()


def test_youtube():
    apikey = ''
    channel_id = 'UCQ0UDLQCjY0rmuxCDE38FGg'
    enable_proxy = 0
    proxy = ''
    ddir = getcwd()
    quality = '720p'
    download_in_live = 1
    y = Youtube(channel_id, enable_proxy, proxy, ddir, apikey, quality, download_in_live)
    y.check()


if __name__ == '__main__':
    pytest.main('test.py')
