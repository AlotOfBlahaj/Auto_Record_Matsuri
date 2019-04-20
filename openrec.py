import time

from lxml.html import etree

from config import sec
from queues_process import queue_map, add_queue
from tools import Aio, get_logger


class Openrec:
    def __init__(self):
        self.Aio = Aio()
        self.logger = get_logger(__name__)

    async def is_live(self, oprec_id):
        html = await self.Aio.main(f'https://www.openrec.tv/user/{oprec_id}', "get")
        dom = etree.HTML(html)
        is_live = dom.xpath('/html/body/div[1]/div[2]/div[18]/div[2]/div/div[3]/ul/li[1]/div/text()')[0]
        if 'Live' in is_live:
            info = dom.xpath('/html/body/div[1]/div[2]/div[18]/div[2]/div/div[3]/ul/li[1]/ul/li/a[2]')[0]
            ref = info.xpath('@href')[0]
            title = dom.xpath('/html/body/div[1]/div[2]/div[18]/div[2]/div/div[3]/ul/li[1]/ul/li/a[2]/text()')[0]
            target = ref
            date = time.strftime("%Y-%m-%d", time.localtime())
            return {'Title': title,
                    'Ref': ref,
                    'Target': target,
                    'Date': date}

    async def check(self, oprec_id):
        is_live = await self.is_live(oprec_id)
        if is_live:
            return is_live, {'Module': 'Openrec', 'Target': oprec_id}
        else:
            queue = queue_map('Openrec')
            add_queue(queue, oprec_id)
            self.logger.info(f'Not found Live, after {sec}s checking')
