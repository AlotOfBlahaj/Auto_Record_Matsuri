import json
from time import sleep, strftime, localtime, time

import re

from config import config
from daemon import VideoDaemon
from tools import get, get_json, get_logger, Database, while_warp
from video_process import process_video


class Youtube(VideoDaemon):

    def __init__(self, user_config):
        super().__init__(user_config)
        self.module = 'Youtube'
        self.api_key = config['youtube']['api_key']
        self.logger = get_logger('Youtube')

    def get_video_info_by_html(self):
        """
        The method is using yfconfig to get information of video including title, video_id, data and thumbnail
        :rtype: dict
        """
        video_page = get(f'https://www.youtube.com/channel/{self.target_id}/live')
        try:
            ytplayer_config = json.loads(re.search(r'ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))
            player_response = json.loads(ytplayer_config['args']['player_response'])
            video_details = player_response['videoDetails']
            # assert to verity live status
            if 'isLive' not in video_details:
                return False
            title = video_details['title']
            vid = video_details['videoId']
            target = f"https://www.youtube.com/watch?v={vid}"
            thumbnails = video_details['thumbnail']['thumbnails'][-1]['url']
            return {'Title': title,
                    'Ref': vid,
                    'Date': strftime("%Y-%m-%d", localtime(time())),
                    'Target': target,
                    'Thumbnails': thumbnails,
                    'User': self.target_id}
        except KeyError:
            self.logger.exception('Get keys error')
            return False

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
                'Date': date,
                'User': self.target_id}

    @while_warp
    def check(self):
        try:
            video_dict = self.get_video_info_by_html()
            if video_dict:
                video_dict['Provide'] = self.module
                process_video(video_dict, self.user_config)
            else:
                self.logger.info(f'{self.target_id}: Not found Live')
        except Exception:
            self.logger.exception('Check Failed')


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
            video_dict['Provide'] = self.module
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
            p.daemon = True
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
        sleep(config['sec'])
