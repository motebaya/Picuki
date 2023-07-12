#!/usr/bin/env python3
"""
picuki.com instagram downloader scrapper
merge dgzr/in-picuki -> motebaya/picuki
18.06.20223 - 4:58 PM
"""

from httpx import AsyncClient
from bs4 import BeautifulSoup
from typing import List, Union, Dict, Tuple, Optional
import re

class Picuki(AsyncClient):
    def __init__(self) -> None:
        super().__init__()
        self.base_url = "https://www.picuki.com"
        self.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0"
        })
        self.media_id: List[str] = []

    def parse(self, string: str) -> BeautifulSoup:
        return BeautifulSoup(
            string, 'html.parser'
        )

    def clear_username(self, username: str) -> str:
        """
        sanitize instagram username:
            length[30, lettes, dot, underscore, digits]
        """
        if not re.match(r"^[a-zA-Z0-9._]{1,30}$", username):
            return re.sub(
                r"[^a-zA-Z0-9_.]", "", username)
        return username

    async def get_profile(self, username: str) -> Union[Tuple[str, Dict[str, str]], None]:
        page = await self.get("/profile/{}".format(
            self.clear_username(username)
        ))

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

        soup = self.parse(page.text)
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

    async def get_media_id(self, page: str, logger = None) -> None:
        soup = self.parse(page)
        """
        search all: [<scheme>://<host>/media/<id>]
        """
        if (media_id := re.findall(r"https?:\/\/(?:www\.)?picuki\.com\/media\/(\d+)", page)):
            self.media_id.extend(
                media_id
            )

        """
        do with bs4 if regex can't find it
        """
        if not bool(self.media_id):
            if (media_id := soup.find_all('div', class_="photo")):
                self.media_id.extend(list(map(
                    lambda x: x.attrs.get('href').split(
                        '/'
                    )[-1], media_id
                )))
            return

        """
        check next page: next if media_id not empty & stop if empty
        """
        logger.info(f"media ID collected: {len(self.media_id)}")
        if (next_page := soup.find('div', class_='load-more-wrapper')):
            logger.warning("loading more page....")
            if bool(self.media_id):
                page = await self.get("{}".format(
                    next_page.attrs.get('data-next')
                ))

                await self.get_media_id(
                    page.text, logger
                )
            return
        return

    async def get_media_content(self, media_id: str) -> Optional[Dict[str, List[str]]]:
        data: Dict[str, Dict[str, str]] = {
            'media': {}
        }
        page = await self.get("/media/{}".format(
            media_id
        ))
        page = page.text
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

        """
        do with bs4 if nothing
        """
        soup = self.parse(page)
        if (info := soup.find('div', class_='single-profile-info')):
            data.update(
                dict(zip(
                    ('username', 'time', 'caption', 'like_count', 'comments_count'),
                    (info.find(class_=i).text.strip() for \
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
        """
        video_list, image_list = [], []
        if (html_video := re.findall(
            r"(\<video[\s\S]*?\<\/video)", page
        )):
            for vid in html_video:
                if (video := re.search(
                    r"(?:\<video[^>]+?poster\=\"(?P<thumbnail>[^<]*?)\"[\s\S]*src\=\"(?P<url>[^<]*?))\"", vid
                )):
                    video_list.append(
                        video.groupdict()
                    )
            
        """
        image: List[str, str]
        """
        if (html_image := re.findall(
            r"<img[^\"]src\=\"([^<]*?)\"", page
        )):
            image_list.extend(
                list(filter(
                    None,
                    html_image
                ))
            )
        else:
            if (html_image := soup.find_all('img')):
                image_list.extend(
                    list(filter(
                        None,
                        map(
                            lambda x: x.attrs.get('src'),
                            html_image
                        )
                    ))
                )

        """
        and again, do with bs4 if regex can't find it.
        """
        if not bool(video_list):
            
            if (html_video := soup.find_all('video')):
                for vid in html_video:
                    video_data = {
                        "thumbnail": vid.attrs.get('poster'),
                        "url": vid.find('source').attrs.get('src')
                    }
                    if video_data not in video_list:
                        video_list.append(
                            video_data
                        )

        data['media'].update({
            'videos': video_list,
            'images': image_list
        })
            
        if len(data) > 1:
            return data
        return None
            
            
        
            
             
             
             