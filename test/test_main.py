import sys

import pytest

from video_process import AdjustFileName, process_video

sys.path.insert(0, '..')


def test_adjust_title():
    replace_list = ['|', '/', '\\']
    title = '夏まつch|542038802'
    result = AdjustFileName(title).adjust()
    print(result)
    for x in replace_list:
        assert x not in result


def test_process_video():
    live_dict = {'Title': '【歌ってみた】スイートマジック 【夏色まつり×紫咲シオン】',
                 'Ref': '97lcMrPqzHg',
                 'Date': '2019-05-12',
                 'Target': 'https://www.youtube.com/watch?v=97lcMrPqzHg'}
    call_back = {'Module': 'Youtube', 'Target': 'UCQ0UDLQCjY0rmuxCDE38FGg'}
    process_video(live_dict, call_back)


if __name__ == '__main__':
    pytest.main('test.py')
