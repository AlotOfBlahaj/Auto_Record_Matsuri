import re
from time import sleep

from config import sec, api_key
from daemon import VideoDaemon
from tools import get, get_json, get_logger, Database
from video_process import process_video


class Youtube(VideoDaemon):

    def __init__(self, target_id):
        super().__init__(target_id)
        self.module = 'Youtube'
        self.api_key = api_key
        # 品质设置
        self.database = Database('Queues')
        self.logger = get_logger('Youtube')

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    def get_videoid_by_channel_id(self, channel_id):
        channel_info = get_json(rf'https://www.googleapis.com/youtube/v3/search?part=snippet&'
                                rf'channelId={channel_id}&eventType=live&maxResults=1&type=video&'
                                rf'key={self.api_key}')
        # 判断获取的数据是否正确
        try:
            item = channel_info['items'][0]
        except KeyError:
            self.logger.exception('Get vid error')
            raise RuntimeError
        title = item['snippet']['title']
        title = title.replace("/", " ")
        vid = item['id']['videoId']
        date = item['snippet']['publishedAt']
        date = date[0:10]
        target = f"https://www.youtube.com/watch?v={vid}"
        thumbnails = item['snippet']['thumbnails']['high']['url']
        return {'Title': title,
                'Ref': vid,
                'Date': date,
                'Target': target,
                'Thumbnails': thumbnails}

    def getlive_title(self, vid):
        live_info = get_json(rf'https://www.googleapis.com/youtube/v3/videos?id={vid}&key={self.api_key}&'
                             r'part=liveStreamingDetails,snippet')
        # 判断视频是否正确
        if live_info['pageInfo']['totalResults'] != 1:
            self.logger.error('Getting title Failed')
            raise RuntimeError
        # JSON中的数组将被转换为列表，此处使用[0]获得其中的数据
        item = live_info['items'][0]
        title = item['snippet']['title']
        date = item['snippet']['publishedAt']
        date = date[0:10]
        target = f"https://www.youtube.com/watch?v={vid}"
        return {'Title': title,
                'Ref': vid,
                'Target': target,
                'Date': date}

    def check(self):
        html = get(f'https://www.youtube.com/channel/{self.target_id}/featured')
        if '"label":"LIVE NOW"' in html:
            # vid = self.get_videoid_by_channel_id()
            # get_live_info = self.getlive_vid(vid)
            video_dict = self.get_videoid_by_channel_id(self.target_id)
            video_dict['Provide'] = self.module
            process_video(video_dict)
            self.logger.error('Getting Live Failed, waiting 5s to retry')
            # await process_video(get_live_info, 'Youtube')
        else:
            if 'Upcoming live streams' in html:
                self.logger.info(f'{self.target_id}: Found A Live Upcoming')
            else:
                self.logger.info(f'{self.target_id}: Not found Live')

    def run(self) -> None:
        self.check()


class YoutubeTemp(Youtube):
    def __init__(self, vinfo):
        super().__init__(None)
        self.vinfo = vinfo
        self.vid = None
        self.db = Database('Queues')
        self.logger = get_logger('YoutubeTemp')

    @staticmethod
    def get_temp_vid(vlink):
        reg = r"watch\?v=([A-Za-z0-9_-]{11})"
        idre = re.compile(reg)
        _id = vlink["_id"]
        vid = vlink["Link"]
        vid = re.search(idre, vid).group(1)
        return {'Vid': vid,
                'Id': _id}

    def check(self):
        self.vinfo = self.get_temp_vid(self.vinfo)
        self.vid = self.vinfo['Vid']
        html = get("https://www.youtube.com/watch?v=" f"{self.vid}")
        if r'"isLive\":true' in html:
            video_dict = self.getlive_title(self.vid)
            process_video(video_dict)
            self.db.delete(self.vinfo)
        else:
            self.logger.info(f'Not found Live')

    def run(self) -> None:
        self.check()


def start_temp_daemon():
    db = Database('Queues')
    while True:
        event = []
        for target_url in db.select():
            p = YoutubeTemp(target_url)
            event.append(p)
            p.start()
        is_running = True
        while is_running:
            has_running = False
            for p in event:
                if p.is_alive():
                    has_running = True
            if not has_running:
                is_running = False
        logger = get_logger('YoutubeTemp')
        logger.info('A check has finished.')
        sleep(sec)
