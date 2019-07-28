from multiprocessing import Process

from bilibili import Bilibili
from config import config
from mirrativ import Mirrativ
from openrec import Openrec
from tools import check_ddir_is_exist, get_logger
from twitcasting import Twitcasting
from youtube import Youtube, start_temp_daemon


logger = get_logger()


class Event:
    def __init__(self):
        self.events_multi = []
        self.gen_process()
        logger.info(self.events_multi)

    def start(self):
        self.start_multi_task()
        if config['youtube']['enable_temp']:
            temp = Process(target=start_temp_daemon)
            temp.run()
        for event in self.events_multi:
            event.join()

    def gen_process(self):
        if config['youtube']['enable']:
            for user_config in config['youtube']['users']:
                y = Youtube(user_config)
                self.events_multi.append(y)
        if config['twitcasting']['enable']:
            for user_config in config['twitcasting']['users']:
                t = Twitcasting(user_config)
                self.events_multi.append(t)
        if config['openrec']['enable']:
            for user_config in config['openrec']['users']:
                o = Openrec(user_config)
                self.events_multi.append(o)
        if config['mirrativ']['enable']:
            for user_config in config['mirrativ']['users']:
                m = Mirrativ(user_config)
                self.events_multi.append(m)
        if config['bilibili']['enable']:
            for user_config in config['bilibili']['users']:
                b = Bilibili(user_config)
                self.events_multi.append(b)

    def start_multi_task(self):
        for proc in self.events_multi:
            proc.start()


if __name__ == '__main__':
    check_ddir_is_exist()
    e = Event()
    e.start()
