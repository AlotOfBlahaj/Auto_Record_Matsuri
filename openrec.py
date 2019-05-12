import time
from multiprocessing import Process

from lxml.html import etree

from config import sec
from daemon import VideoDaemon
from queues import openrec_queue
from tools import get_logger, get


class Openrec(VideoDaemon):
    def __init__(self):
        super().__init__(openrec_queue)
        self.logger = get_logger('Openrec')
        self.module = 'Openrec'

    @staticmethod
    def is_live(oprec_id):
        html = get(f'https://www.openrec.tv/user/{oprec_id}')
        dom = etree.HTML(html)
        try:
            is_live = dom.xpath('/html/body/div[1]/div[2]/div[18]/div[2]/div/div[3]/ul/li[1]/div/text()')[0]
        except IndexError:
            return None
        if 'Live' in is_live:
            info = dom.xpath('/html/body/div[1]/div[2]/div[18]/div[2]/div/div[3]/ul/li[1]/ul/li/a[2]')[0]
            ref = info.xpath('@href')[0]
            title = dom.xpath('/html/body/div[1]/div[2]/div[18]/div[2]/div/div[3]/ul/li[1]/ul/li/a[2]/text()')[0]
            target = ref
            date = time.strftime("%Y-%m-%d", time.localtime())
            live_dict = {'Title': title,
                         'Ref': ref,
                         'Target': target,
                         'Date': date}
            return live_dict
        return None

    def check(self, oprec_id):
        is_live = self.is_live(oprec_id)
        if is_live:
            self.put_download([is_live, {'Module': 'Openrec', 'Target': oprec_id}])
        else:
            self.logger.info(f'{oprec_id}: Not found Live, after {sec}s checking')
            self.return_and_sleep(oprec_id, self.module)

    def actor(self, oprec_id):
        proc = Process(target=self.check, args=(oprec_id,))
        proc.start()
