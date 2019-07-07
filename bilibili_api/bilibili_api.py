from tools import get_json


class BilibiliAPI:
    @staticmethod
    def get_video_num(mid: int) -> int:
        nav_info = get_json(f'https://api.bilibili.com/x/space/navnum?mid={mid}&jsonp=jsonp')
        video_num = nav_info['data']['video']
        return video_num

    @staticmethod
    def get_video(mid: int) -> dict:
        video_info = get_json(
            f'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={mid}&pagesize=1&tid=0&page=1&keyword=&order=pubdate')
        video = video_info['data']['vlist'][0]
        title = video['title']
        ref = f"https://www.bilibili.com/video/av{video['aid']}"
        return {'Title': title,
                'Ref': ref}
