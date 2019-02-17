from config import *
from tools import gethtml
import time
import json
import asyncio

class Mirrativ(object):

    def __init__(self):
        self.id = userid

    def live_info(self, id):
        l_info = json.loads(gethtml('https://www.mirrativ.com/api/user/profile?user_id={}'.format(id)))
        nowlive = l_info['onlive']
        if nowlive != None:
            return 'https://www.mirrativ.com/live/' + nowlive['live_id']
        else:
            print('Mirrativ|' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                  'Not found Live, after {}s checking'.format(sec))

    def check(self):
        self.live_info(self.id)
