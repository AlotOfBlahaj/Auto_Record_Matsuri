import subprocess
from time import time

import re
from os.path import isfile

from config import config
from daemon import VideoUpload
from tools import get_logger, bot, check_ddir_is_exist, get_ddir


def downloader(link, title, dl_proxy, ddir, user_config, quality='best'):
    try:
        is_download = user_config['download']
    except KeyError:
        is_download = True
    if is_download:
        logger = get_logger('Downloader')
        # co = ["streamlink", "--hls-live-restart", "--loglevel", "trace", "--force"]
        co = ["streamlink", "--hls-live-restart", "--force"]
        if config['enable_proxy']:
            co.append('--http-proxy')
            co.append(f'http://{dl_proxy}')
            co.append('--https-proxy')
            co.append(f'https://{dl_proxy}')
        co.append("-o")
        co.append(f"{ddir}/{title}")
        co.append(link)
        co.append(quality)
        subprocess.run(co)
        paths = f'{ddir}/{title}'
        if isfile(paths):
            logger.info(f'{title} has been downloaded.')
            bot(f"[下载提示] {title} 已下载完成，等待上传", user_config)
        else:
            logger.error(f'{title} Download error, link: {link}')
            raise RuntimeError(f'{title} Download error, link: {link}')
        # 不应该使用os.system


class AdjustFileName:

    def __init__(self, filename):
        self.filename = filename

    def title_block(self):
        replace_list = ['|', '/', '\\', ':']
        for x in replace_list:
            self.filename = self.filename.replace(x, '#')

    def file_exist(self, ddir):
        paths = f'{ddir}/{self.filename}.ts'
        if isfile(paths):
            self.filename = self.filename + f'_{time()}.ts'
        else:
            self.filename = self.filename + '.ts'

    def filename_length_limit(self):
        lens = len(self.filename)
        if lens > 80:
            self.filename = self.filename[:80]

    def remove_emoji(self):
        emoji_pattern = re.compile(
            u'(\U0001F1F2\U0001F1F4)|'  # Macau flag
            u'([\U0001F1E6-\U0001F1FF]{2})|'  # flags
            u'([\U0001F600-\U0001F64F])'  # emoticons
            "+", flags=re.UNICODE)
        self.filename = emoji_pattern.sub('', self.filename)

    def adjust(self, ddir):
        self.remove_emoji()
        self.title_block()
        self.filename_length_limit()
        self.file_exist(ddir)
        return self.filename


def process_video(video_dict, user_config=config):
    """
    处理直播视频，包含bot的发送，视频下载，视频上传和存入数据库
    :param video_dict: 含有直播视频数据的dict
    :return: None
    """
    bot(f"[直播提示] {video_dict['Provide']}{video_dict.get('Title')} 正在直播 链接: {video_dict['Target']} [CQ:at,qq=all]", user_config)
    ddir = get_ddir(user_config)
    check_ddir_is_exist(ddir)
    logger = get_logger('Process Video')
    logger.info(f'{video_dict["Provide"]} Found A Live, starting downloader')
    video_dict['Title'] = AdjustFileName(video_dict['Title']).adjust(ddir)
    if video_dict["Provide"] == 'Youtube':
        downloader(r"https://www.youtube.com/watch?v=" + video_dict['Ref'], video_dict['Title'], config['proxy'], ddir, user_config,config['youtube']['quality'])
    else:
        downloader(video_dict['Ref'], video_dict['Title'], ddir, user_config, config['proxy'])
    if config['enable_upload']:
        v = VideoUpload(video_dict, user_config)
        v.start()
