import time

from lxml.html import etree

from daemon import VideoDaemon
from tools import get_logger, get, while_warp
from video_process import process_video


class Openrec(VideoDaemon):
    def __init__(self, target_id):
        super().__init__(target_id)
        self.logger = get_logger('Openrec')
        self.module = 'Openrec'

    def is_live(self):
        html = get(f'https://www.openrec.tv/user/{self.target_id}')
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

    @while_warp
    def check(self):
        is_live = self.is_live()
        if is_live:
            video_dict = is_live
            video_dict['Provide'] = self.module
            process_video(video_dict)
        else:
            self.logger.info(f'{self.target_id}: Not found Live')

    def run(self) -> None:
        self.check()
