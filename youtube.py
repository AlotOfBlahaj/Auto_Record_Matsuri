import re
from multiprocessing import Process
from time import sleep

from config import sec, api_key
from daemon import VideoDaemon
from queues import youtube_queue
from tools import get, get_json, get_logger, Database


class Youtube(VideoDaemon):

    def __init__(self):
        super().__init__(youtube_queue)
        # self.channel_id = channel_id
        self.api_key = api_key
        # 品质设置
        self.database = Database()
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
            self.logger.error('Get vid error')
            raise RuntimeError('Get vid error')
        title = item['snippet']['title']
        title = title.replace("/", " ")
        vid = item['id']['videoId']
        date = item['snippet']['publishedAt']
        date = date[0:10]
        target = f"https://www.youtube.com/watch?v={vid}"
        return {'Title': title,
                'Ref': vid,
                'Date': date,
                'Target': target}

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

    def check(self, channel_id):
        html = get(f'https://www.youtube.com/channel/{channel_id}/featured')
        if '"label":"LIVE NOW"' in html:
            # vid = self.get_videoid_by_channel_id()
            # get_live_info = self.getlive_vid(vid)
            try:
                live_info = self.get_videoid_by_channel_id(channel_id)
                video = [live_info, {'Module': 'Youtube', 'Target': channel_id}]
                self.put_download(video)
            except RuntimeError:
                self.logger.error('Getting Live Failed, waiting 5s to retry')
            # await process_video(get_live_info, 'Youtube')
        else:
            if 'Upcoming live streams' in html:
                self.logger.info(f'Found A Live Upcoming, after {sec}s checking')
            else:
                self.logger.info(f'Not found Live, after {sec}s checking')
            self.return_and_sleep(channel_id, 'Youtube')

    def actor(self, channel_id):
        proc = Process(target=self.check, args=(channel_id,))
        proc.start()


class YoutubeTemp(Youtube):
    def __init__(self):
        super().__init__()
        self.vinfo = None
        self.vid = None
        self.db = Database()
        self.logger = get_logger('YoutubeTemp')

    @staticmethod
    def get_temp_vid(vlink):
        reg = r"watch\?v=([A-Za-z0-9_-]{11})"
        idre = re.compile(reg)
        _id, vid = vlink
        vid = re.search(idre, vid).group(1)
        return {'Vid': vid,
                'Id': _id}

    def check(self, vlink):
        self.vinfo = self.get_temp_vid(vlink)
        self.vid = self.vinfo['Vid']
        html = get("https://www.youtube.com/watch?v=" f"{self.vid}")
        if r'"isLive\":true' in html:
            live_info = self.getlive_title(self.vid)
            video = [live_info, {'Module': 'Youtube', 'Target': None}]
            self.db.delete(self.vinfo['Id'])
            self.put_download(video)
        else:
            self.logger.info(f'Not found Live, after {sec}s checking')
            sleep(sec)

    def actor(self, vlink):
        proc = Process(target=self.check, args=(vlink,))
        proc.start()

    def daemon(self):
        db = Database()
        while True:
            for vlink in db.select():
                if vlink:
                    self.actor(vlink)
