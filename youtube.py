import json
import re
import time

from config import sec
from tools import Aio, echo_log, process_video, Database


class Youtube:

    def __init__(self, api_key, quality):
        # self.channel_id = channel_id
        self.api_key = api_key
        # 品质设置
        self.quality = quality
        self.database = Database()
        self.Aio = Aio()

    # 关于SearchAPI的文档 https://developers.google.com/youtube/v3/docs/search/list
    async def get_videoid_by_channel_id(self, channel_id):
        channel_info = json.loads(
            await self.Aio.main(rf'https://www.googleapis.com/youtube/v3/search?part=snippet&'
                                rf'channelId={channel_id}&eventType=live&maxResults=1&type=video&'
                                rf'key={self.api_key}', "get"))
        # 判断获取的数据是否正确
        if channel_info['items']:
            item = channel_info['items'][0]
            title = item['snippet']['title']
            title = title.replace("/", " ")
            vid = item['id']['videoId']
            date = item['snippet']['publishedAt']
            date = date[0:10]
            return {'Title': title,
                    'Ref': vid,
                    'Date': date}
        else:
            raise ValueError

    async def get_temp_refvid(self, temp_ref):
        reg = r"watch\?v=([A-Za-z0-9_-]{11})"
        idre = re.compile(reg)
        for _id, _ref in temp_ref:
            vid = re.search(idre, _ref).group(1)
            html = await self.Aio.main("https://www.youtube.com/watch?v=" f"{vid}", "get")
            if r'"isLive\":true' in html:
                is_live = await self.getlive_title([vid])
                # is_live = self.getlive_vid(vid)
                if is_live:
                    self.database.delete(_id)
                    return is_live
            else:
                echo_log('Youtube|temp' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                         f'Not found Live, after {sec}s checking')

    async def getlive_title(self, vid):
        for x in vid:
            live_info = json.loads(
                await self.Aio.main(rf'https://www.googleapis.com/youtube/v3/videos?id={x}&key={self.api_key}&'
                                    r'part=liveStreamingDetails,snippet', "get"))
            # 判断视频是否正确
            if live_info['pageInfo']['totalResults'] != 1:
                raise ValueError
            # JSON中的数组将被转换为列表，此处使用[0]获得其中的数据
            item = live_info['items'][0]
            title = item['snippet']['title']
            title = title.replace('/', '|')
            return {'Title': title,
                    'Ref': x}

    async def check(self, channel_id):
        html = await self.Aio.main(f'https://www.youtube.com/channel/{channel_id}/featured', "get")
        if '"label":"LIVE NOW"' in html:
            # vid = self.get_videoid_by_channel_id()
            # is_live = self.getlive_vid(vid)
            is_live = await self.get_videoid_by_channel_id(channel_id)
            await process_video(is_live, 'Youtube')
        elif 'Upcoming live streams' in html:
            echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Found A Live Upcoming, after {sec}s checking')
        else:
            echo_log('Youtube' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Not found Live, after {sec}s checking')

    async def check_temp(self):
        temp_ref = self.database.select()
        if temp_ref:
            temp_refvid = await self.get_temp_refvid(temp_ref)
            is_live = temp_refvid
            if is_live:
                await process_video(is_live, 'Youtube')
        else:
            echo_log('Youtube|temp' + time.strftime('|%m-%d %H:%M:%S|', time.localtime(time.time())) +
                     f'Queue is empty, after {sec}s checking')
