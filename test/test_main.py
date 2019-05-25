import sys

import pytest

from daemon import VideoUpload
from mirrativ import Mirrativ
from openrec import Openrec
from twitcasting import Twitcasting
from video_process import AdjustFileName, process_video
from youtube import Youtube, start_temp_daemon

sys.path.insert(0, '..')


def test_adjust_title():
    replace_list = ['|', '/', '\\']
    title = '夏まつch|542038802|saddddddddddddddddasdaaaaaaaaaaaddddddjhjhjhj😠'
    result = AdjustFileName(title).adjust()
    print(result)
    for x in replace_list:
        assert x not in result


def test_process_video():
    v = VideoUpload()
    v.start()
    live_dict = {'Title': '【歌ってみた】スイートマジック 【夏色まつり×紫咲シオン】',
                 'Ref': '97lcMrPqzHg',
                 'Date': '2019-05-12',
                 'Target': 'https://www.youtube.com/watch?v=97lcMrPqzHg',
                 'Provide': 'Youtube'}
    process_video(live_dict)
    v.join()


def test_youtube():
    y = Youtube('UCcnoKv531otgPrd3NcR0mag')
    y.check()


def test_youtube_temp():
    start_temp_daemon()


def test_mirrativ():
    m = Mirrativ('3264432')
    m.run()


def test_twitcasting():
    t = Twitcasting('natsuiromatsuri')
    t.start()
    t.join()


def test_openrec():
    o = Openrec('natsuiromatsuri')
    o.start()
    o.join()

if __name__ == '__main__':
    pytest.main('test.py')
