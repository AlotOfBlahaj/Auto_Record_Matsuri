import sys

import pytest

from mirrativ import Mirrativ
from openrec import Openrec
from youtube import Youtube

sys.path.insert(0, '..')


def test_mirrativ():
    userid = ['3264432']
    m = Mirrativ()
    for x in userid:
        m.check(x)


def test_youtube():
    apikey = ''
    channel_id = ['UCQ0UDLQCjY0rmuxCDE38FGg']
    quality = '720p'
    y = Youtube(apikey, quality)
    for x in channel_id:
        y.check(x)


def test_openrec():
    oprec_id = ['natsuiromatsuri']
    o = Openrec()
    for x in oprec_id:
        o.check(x)


if __name__ == '__main__':
    pytest.main('test.py')
