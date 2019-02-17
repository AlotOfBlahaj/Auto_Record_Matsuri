import threading
import time
from config import sec
from youtube import Youtube
from mirrativ import Mirrativ


class Localtimer(object):

    def __init__(self):
        thread_y = threading.Thread(target=self.youtube_timer())
        thread_m = threading.Thread(target=self.mirrativ_timer())
        while True:
            if thread_y.is_alive() is False:
                thread_y = threading.Thread(target=self.youtube_timer())
                thread_y.start()
            if thread_m.is_alive() is False:
                thread_m = threading.Thread(target=self.mirrativ_timer())
                thread_m.start()
            time.sleep(sec)

    def youtube_timer(self):
        y = Youtube()
        y.check()

    def mirrativ_timer(self):
        m = Mirrativ()
        m.check()


Localtimer()
