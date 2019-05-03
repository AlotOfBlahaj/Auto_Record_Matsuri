import sys

import pytest

from video_process import title_block

sys.path.insert(0, '..')


def test_title_block():
    replace_list = ['|', '/', '\\']
    title = '夏まつch|542038802.ts'
    result = title_block(title)
    print(result)
    for x in replace_list:
        assert x not in result




if __name__ == '__main__':
    pytest.main('test.py')
