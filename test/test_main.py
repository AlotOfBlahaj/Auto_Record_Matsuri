import sys

import pytest

from mirrativ import Mirrativ
from youtube import Youtube

sys.path.insert(0, '..')


def test_mirrativ():
    userid = '3264432'
    m = Mirrativ(userid)
    m.check()


def test_youtube():
    apikey = ''
    channel_id = 'UCQ0UDLQCjY0rmuxCDE38FGg'
    quality = '720p'
    y = Youtube(channel_id, apikey, quality)
    y.check()


if __name__ == '__main__':
    pytest.main('test.py')
