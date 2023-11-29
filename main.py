#!/usr/bin/env python3
"""
main.py MODULE - Handler
@github.com/motebaya
update: 17.11.2023 - 8:00 PM 
"""

from lib.logger import logger, col
from typing import List, Dict, Optional, Union, Any, Tuple
from lib.Helper import Helper
from lib.Picuki import Picuki
import random

class Main:
    Instance = Picuki()

    @staticmethod
    async def getProfileInfo(
        username: str,
        savelog: Optional[bool] = True
    ) -> Union[Tuple[str ,Dict[str, Any]], None]:
        """get user short info by suplied username.

        :param str username: username target.
        :param bool savelog: save result info to filename, defaults to False
        :return Dict[str, str]:return result profile info.
        """
        username = Helper.clear_username(username)
        logger.info(f"Getting profile: @{username}")
        if (profileInfo := await Main.Instance.get_profile(username)):
            webpage, profileInfo = profileInfo
            if savelog:
                await Helper.saveLog(
                    username,
                    profileInfo,
                    "profile.json"
                )
            return (webpage, profileInfo)
        logger.error(f"Failed get info from: {col.GREEN}{username!r}{col.RESET}, make sure username is correct!")
        exit(1)
    
    @staticmethod
    async def getMediaId(
        target: str,
        limit: Optional[int] = 50,
        shuffle: Optional[bool] = False,
        saveLog: Optional[bool] = True
    ) -> Dict[str, List[str]]:
        """
        get media id by suplied webpage from this.getProfileInfo (save your time) or username.
        username IG no more than 30 length, so it will get page if suplied username.

        :param str target: username/webpage.
        :param int limit: set, how much you want to get bulk media id post from any profile.
            _default: 50. max: ??, min: 12 (1 page).
        :param bool shuffle: by default media id grabbed by latest to old, set `True` if want to shuffle it!.
        :param bool saveLog: save result grabbed media id to file or not. recomended to save it for download later.
        :return Dict[str, List[str]]: result from media id.
        """
        profileInfo = None
        if len(target) < 30:
            target, profileInfo = await Main.Instance.get_profile(
                Helper.clear_username(
                    target
                )
            )
            Helper.show_table(profileInfo)

        logger.info(f"grabbing media id with limit set: {limit}")
        mediaID = await Main.Instance.get_media_id(target, limit)
        if (len(mediaID) != 0):
            if shuffle:
                random.shuffle(mediaID)
                logger.warning("media id has shuffled!")

            logger.info(f"Total media ID grabbed: {str(len(mediaID))}")
            mediaID = {"mediaID": mediaID, "username": Helper.clear_username(
                profileInfo.get('username') if profileInfo else \
                    Helper.parse(
                        target
                    ).find(class_="profile-name-top").text.strip()
            )}
            if saveLog:
                logger.info(f"Saving result..")
                await Helper.saveLog(
                    mediaID.get('username'), mediaID, "mediaID.json"
                )
                return mediaID
            return mediaID
        logger.error(f"Failed when get media ID from target, make sure the target is public profile!")
        return

    async def downloadMediaContent(mediaID: Dict[str, List[str]], mediaType: str) -> None:
        """
        get content by media id list, then download it to local file.

        :param Dict[str, List[str]] mediaID: this should from result this.getMediaId!.
        :param str mediaType: type media want to download, e.g: [images, thumbnails, videos].
            leave it blank if you want to download all media type.
        """
        username = mediaID.get('username')
        mediaID = mediaID.get('mediaID')
        if not mediaID or len(mediaID) == 0:
            logger.error("ValueError: Invalid Suplied Data!")
            exit(0)
        
        selected: List[str] = ['images', 'videos', 'thumbnails']
        if bool(mediaType):
            for select in selected:
                if select != mediaType:
                    selected.remove(
                        select
                    )
        try:
            logger.info(f"Starting download: {str(len(mediaID))} Items.")
            for index, mediaid in enumerate(mediaID, 1):
                logger.info(f"Processing: {mediaid}->{index} of {str(len(mediaID))}")
                if (content := await Main.Instance.get_media_content(mediaid)):
                    mediaContent = content.pop('media')
                    Helper.show_table(content)
                    targetContent = mediaContent.get(selected[0] if selected[0] != "thumbnails" else "images")
                    if len(targetContent) != 0:
                        logger.info(f"Downloading: {str(len(targetContent))} {selected[0]} from ID:{mediaid}")
                        for i, cont in enumerate(targetContent, 1):
                            logger.info(f"Downloading {selected[0]}: {i} of {str(len(targetContent))}")
                            await Helper._downloadContent(
                                url=cont if isinstance(cont, str) \
                                    else cont.get('url') if mediaType == "videos" \
                                        else cont.get('thumbnail'),
                                username=username,
                                type=mediaType
                            )
                            await Helper.delay(2)
                    else:
                        logger.warning(f"There's no {mediaType!r} to download from: {mediaid}")
                    """
                    did you think this to slow? but, the important it's working as well.
                    """
                    await Helper.delay(3)
                else:
                    logger.error(f"Failed get media content from ID: {mediaid}, skipped!")
                    await Helper.delay(1)
                    continue
        except EOFError:
            pass
    
    async def execute(username: str, mediaType: str) -> None:
        """execute bulk download directly.

        :param str username: username target.
        :param str mediaType: typemedia.
        """
        try:
            # dump profile info
            webpage, profileInfo = await Main.getProfileInfo(username)
            Helper.show_table(profileInfo, title=f"{username!r}")
            # dump media id
            contentMediaID = await Main.getMediaId(webpage, int(profileInfo.get('total_posts')))
            Helper.show_table(contentMediaID.copy())
            mediaID = contentMediaID.get('mediaID')
            print(mediaID, len(mediaID))
            logger.info(f"media id retrevied: {len(mediaID)}")
            # start download
            await Main.downloadMediaContent(contentMediaID, mediaType)
        except Exception as e:
            raise Exception(str(e))