import json
from time import sleep, strftime, localtime, time
import logging
import re

from config import config
from daemon import VideoDaemon
from tools import get, Database, while_warp
from video_process import process_video

logger = logging.getLogger('run.youtube')


class Youtube(VideoDaemon):

    def __init__(self, user_config):
        super().__init__(user_config)
        self.module = 'Youtube'
        self.api_key = config['youtube']['api_key']

    @staticmethod
    def get_video_info_by_html(url):
        """
        The method is using yfconfig to get information of video including title, video_id, data and thumbnail
        :rtype: dict
        """
        video_page = get(url)
        try:
            ytplayer_config = json.loads(re.search(r'ytplayer.config\s*=\s*([^\n]+?});', video_page).group(1))
            player_response = json.loads(ytplayer_config['args']['player_response'])
            video_details = player_response['videoDetails']
            # assert to verity live status
            if 'isLive' not in video_details:
                is_live = False
            else:
                is_live = True
            title = video_details['title']
            vid = video_details['videoId']
            target = f"https://www.youtube.com/watch?v={vid}"
            thumbnails = video_details['thumbnail']['thumbnails'][-1]['url']
            return {'Title': title,
                    'Ref': vid,
                    'Date': strftime("%Y-%m-%d", localtime(time())),
                    'Target': target,
                    'Thumbnails': thumbnails,
                    'User': video_details['channelId'],
                    'Is_live': is_live}
        except KeyError:
            logger.exception('Get keys error')
            return False

    @while_warp
    def check(self):
        try:
            video_dict = self.get_video_info_by_html(f'https://www.youtube.com/channel/{self.target_id}/live')
            if video_dict['Is_live']:
                video_dict['Provide'] = self.module
                process_video(video_dict, self.user_config)
            else:
                logger.info(f'{self.target_id}: Not found Live')
        except Exception:
            logger.exception('Check Failed')


class YoutubeTemp(Youtube):
    def __init__(self, vinfo):
        super().__init__(None)
        self.vinfo = vinfo
        self.db = Database('Queues')

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
        vid = self.vinfo['Vid']
        _id = self.vinfo['Id']
        video_dict = self.get_video_info_by_html(f"https://www.youtube.com/watch?v={vid}")
        if video_dict['Is_live']:
            video_dict['Provide'] = self.module
            user_config = {
                'bot_notice': config['youtube']['enable_temp_bot_notice'],
                'download': config['youtube']['enable_temp_download']
            }
            process_video(video_dict, user_config)
            self.db.delete(_id)
        else:
            logger.info(f'Not found Live')

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
        logger.info('A check has finished.')
        sleep(config['sec'])
