#!/usr/bin/env python3
"""
CLI handler
16.11.2023 - @github.com/motebaya
"""
from main import Main
from typing import Dict, Any
from lib.Helper import Helper
from ssl import SSLWantReadError
from lib.logger import logger
from argparse import ArgumentParser, RawTextHelpFormatter, FileType
import asyncio, os, json

class CLI:

    @staticmethod
    async def _main(**kwargs: Dict[str, Any]) -> None:
        if kwargs.get('verbose'):
            Helper.setVerbose(True)

        # default output
        userPath = os.path.realpath("./Users")
        if not os.path.exists(userPath):
            os.mkdir(userPath)
            logger.info(f"Default output at: {userPath}")
        
        """download from media id by suplied file.
        by default `download_post` suplied as `json file` from `<current>/Users/<username>/mediaID.json`.
        no need input username.

        :prog cli -D/--download-post Users/<username>/mediaID.json -t images
        """
        download_post = kwargs.get('download_post')
        mediaType = kwargs.get('type')
        if (download_post):
            if (mediaType):
                download_post = json.loads(download_post.read())
                Helper.show_table(download_post.copy())
                logger.info(f"{len(download_post.get('mediaID'))} media id loaded..")
                await Main.downloadMediaContent(
                    download_post, mediaType
                )
            else:
                logger.error("Media type required for download, `--type`")
                exit(1)
            return
        
        """profile and media id grabber
        :grabber str profile/post.
        :prog cli -u <username> -d profile/post [optional] -l 12
        """
        grabber = kwargs.get('dump')
        if (grabber):
            if (grabber == "profile"):
                webpage, profile = await Main.getProfileInfo(
                    kwargs.get('username'), savelog=True
                )
                Helper.show_table(profile)

            if grabber == "post":
                limit = kwargs.get('limit', 12)
                mediaID = await Main.getMediaId(
                    kwargs.get('username'), limit
                )
                Helper.show_table(
                    mediaID, title=repr("media id report")
                )
            return
        
        """no grabber, no dumper, no limit, direct execute by suplied username.
        :prog cli -u <username> -t images/thumbnails/videos
        """
        if (kwargs.get('username') and mediaType):
            await Main.execute(
                kwargs.get('username'),
                mediaType
            )
        else:
            logger.warning(f"\n{json.dumps(kwargs, indent=1)}")
                

if __name__ == "__main__":
    parser = ArgumentParser(
        description="\t\tPicuki.com\n    Instagram Scrapper bulk media downloader\n\t @github.com/motebaya - © 2023", 
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument(
        "-u",
        "--username",
        help="spesific instagram username",
        metavar="",
        type=Helper.clear_username # validate username
    )
    parser.add_argument(
        "-d",
        "--dump",
        help="dumper option, [profile, post]",
        choices=["profile", "post"],
        metavar=""
    )
    parser.add_argument(
        "-D",
        "--download-post",
        help="get and download content from `media id` by suplied `--dump post` json output file.",
        type=FileType('r'),
        metavar=""
    )
    parser.add_argument(
        "-l",
        "--limit",
        help="set limit: download/grabber. [default: 50, min:12, max:??]",
        type=int,
        metavar=""
    )
    parser.add_argument(
        "-t",
        "--type",
        help="choose single mediaType: [images, videos, thumbnails]",
        type=str,
        choices=["images", "videos", "thumbnails"],
        metavar=""
    )
    opt = parser.add_argument_group("Optional")
    opt.add_argument(
        "-E",
        "--example",
        help="show example command",
        action="store_true"
    )
    opt.add_argument(
        "-V",
        "--verbose",
        help="enable logger debug mode",
        action="store_true"
    )
    args = parser.parse_args()
    if any(vars(args).values()):
        try:
            asyncio.run(CLI._main(**vars(args)))
        except (asyncio.exceptions.CancelledError, SSLWantReadError) as e:
            logger.error(f"Exception: {str(e)}")
    else:
        parser.print_help()