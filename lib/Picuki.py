#!/usr/bin/env python3
"""
picuki.com instagram downloader scrapper
merge dgzr/in-picuki -> motebaya/picuki
18.06.20223 - 4:58 PM
"""
from httpx import AsyncClient
from .logger import logger
from .Helper import Helper
from typing import List, Optional, Union, Dict, Tuple, Any
import re

class Picuki(AsyncClient):
    def __init__(self) -> None:
        super().__init__()
        self.base_url = "https://www.picuki.com"
        self.headers.update({
            "Host": "www.picuki.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
        })

    async def get_profile(self, username: str) -> Union[Tuple[str, Dict[str, str]], None]:
        page = await self.get("/profile/{}".format(
            Helper.clear_username(username)
        ), timeout=10)

        """
        return if matched with regex
        """
        if (info := re.search(
            r"(?<=name-top\">)(?P<username>[^>].*?)(?=</h1>)[\s\S]*?(?<=name-bottom\">)(?P<full_name>[^>].*?)(?=</h2>)[\s\S]*?(?<=description\">)\s+(?P<bio>[^>].*?)\s+(?=</div>)[\s\S]*?(?<=total_posts\">)(?P<total_posts>[\d+].*?)(?=</)[\s\S]*?(?<=followed_by\">)(?P<followers>[^>].*?)(?=</)[\s\S]*?(?<=follows\">)(?P<following>[^>].*?)(?=</)", page.text
        )):
            return (
                page.text,
                info.groupdict()
            )

        soup = Helper.parse(page.text)
        """
        do with bs4 if regex can't find it
        """
        if soup.find('div', class_='profile-info'):
            return (page.text, dict(zip(
                ('username', 'full_name',
                 'bio', 'total_posts',
                 'followers', 'following'),
                    (soup.find(class_=i).text.strip() for i in (
                        "profile-name-top", "profile-name-bottom",
                        "profile-description", "total_posts",
                        "followed_by", "follows"))
                    )
                ))

        """
        return nothing if profile not found
        """
        return None

    async def get_media_id(
        self,
        page: str,
        limit: int,
        result: Optional[List[str]] = []
    ) -> List[str]:
        """
        grab media id from user profile.

        :param str page: webpage output from this.get_profile
        :param int limit: media id grabbed limit.
        :param List[str] result: media id result, defaults to []
        """
        soup = Helper.parse(page)
        if (media_id := re.findall(r"https?:\/\/(?:www\.)?picuki\.com\/media\/(\d+)", page)):
            result.extend(
                media_id
            )
        else:
            """
            do with bs4 if regex can't find it and return None if both can't find it.
            """
            if (media_id := soup.find_all('div', class_="photo")):
                result.extend(list(map(
                    lambda x: x.attrs.get('href').split(
                        '/'
                    )[-1], media_id
                )))
            else:
                return result # because nothing media id.
        """
        limit reached? break.
        """
        if result:
            if (len(result) >= limit):
                return result

        """
        check next page: next if media_id not empty & stop if empty.
        """
        logger.info(f"media ID collected: {len(result)}")
        if (next_page := soup.find('div', class_='load-more-wrapper') or \
            soup.find('input', class_="pagination-next-page-input")
            ):
            logger.info("loading more page....")
            page = await self.get("{}".format(
                next_page.attrs.get('data-next') or \
                    next_page.attrs.get('value')
            ), timeout=10)
            """
            avoid exception: ssl.SSLWantReadError.
            it could be help it for adding delay before continue to next request.
            default: int: 3.
            """
            await Helper.delay(3)
            await self.get_media_id(
                page.text, limit, result
            )
        return result

    async def get_media_content(self, media_id: str) -> Union[Dict[str, Any], None]:
        """
        grab media content: e.g video, photos, .etc
        using regex at first bcs i think it more faster than bs4.

        :param str media_id: single media id from this.get_media_id
        :return Union[Dict[Any], None]: None | {}
        """        
        data: Dict[str, Any] = {'media': {}}
        page = await self.get("/media/{}".format(
            media_id
        ), timeout=10)
        page = page.text
        soup = Helper.parse(page)
        """
        search: [username, time, caption, tags]
        """
        if (media_info := re.search(
            r"(?<=photo-nickname\">).*?\">(?P<name>[^>].*?)(?=</)[\s\S]*?(?<=photo-time\">)(?P<time>[^>].*?)(?=</)[\s\S]*?(?<=photo-description\">)(?P<caption>[\s\S]*?)(?=\s+(<a|</div>))", page
        )):
            media_info = media_info.groupdict()
            if (tag := re.findall(
                r"href=\"https?:\/\/(?:www\.)?picuki\.com\/tag\/([^>]*)\"", page
            )):
                media_info.update({
                    "tags": ', '.join(tag)
                })
            
            if (like := re.search(
                r"(?<=icon-thumbs-up-alt\">)(?P<likes_count>[^\"].*?)(?=\<\/span>)[\s\S]*(?<=commentsCount\">)(?P<comments_count>[^\<].*?)(?=\<\/span>)", page
            )):
                data.update(
                    like.groupdict()
                )
            data.update(media_info)
        else:
            """
            do with bs4 if nothing
            """
            if (media_info := soup.find('div', class_='single-profile-info')):
                data.update(
                    dict(zip(
                        ('username', 'time', 'caption', 'like_count', 'comments_count'),
                        (media_info.find(class_=i).text.strip() for \
                            i in (
                                'single-photo-nickname', 
                                'single-photo-time', 
                                'single-photo-description',
                                'icon-thumbs-up-alt',
                                'icon-chat'
                            ))
                        )
                    )
                )

        """
        search media: Dict[thumbnail, url]
        @grab video list url
        """
        videos_list, images_list = [], []
        if (html_video := re.findall(
            r"(\<video[\s\S]*?\<\/video)", page
        )):
            for vid in html_video:
                if (video := re.search(
                    r"(?:\<video[^>]+?poster\=\"(?P<thumbnail>[^<]*?)\"[\s\S]*src\=\"(?P<url>[^<]*?))\"", vid
                )):
                    videos_list.append(
                        video.groupdict()
                    )
        else:
            """
            and again, do with bs4 if regex can't find it.
            """
            if (html_video := soup.find_all('video')):
                for vid in html_video:
                    video_data = {
                        "thumbnail": vid.attrs.get('poster'),
                        "url": vid.find('source').attrs.get('src')
                    }
                    if video_data not in videos_list:
                        videos_list.append(
                            video_data
                        )

        """
        image: List[str, str]
        @grab images/thumbnail url
        """
        if (html_image := re.findall(
            r"<img[^\"]src\=\"([^<]*?)\"", page
        )):
            images_list.extend(
                list(filter(
                    None,
                    html_image
                ))
            )
        else:
            if (html_image := soup.find_all('img')):
                images_list.extend(
                    list(filter(
                        None,
                        map(
                            lambda x: x.attrs.get('src'),
                            html_image
                        )
                    ))
                )
        data['media'].update({
            'videos': videos_list,
            'images': images_list
        })
            
        if len(data) > 1:
            return data
        return None