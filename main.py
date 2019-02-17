import time
from config import sec, sec_error
from youtube import Youtube
from mirrativ import Mirrativ
import multiprocessing

class Localtimer(object):

    def __init__(self):
        while True:
            try:
                multiprocessing.Process(target=self.youtube_timer()).start()
                multiprocessing.Process(target=self.mirrativ_timer()).start()
            except:
                time.sleep(sec_error)

    def youtube_timer(self):
        y = Youtube()
        y.check()
        time.sleep(sec)

    def mirrativ_timer(self):
        m = Mirrativ()
        m.check()
        time.sleep(sec)


Localtimer()
