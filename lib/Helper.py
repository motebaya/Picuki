#!/usr/bin/env python3

"""
Helper Utilities.
i just make it for easier maintained.
@github.com/motebaya at 16.11.2023 - 12.12PM
"""
from rich.panel import Panel
from bs4 import BeautifulSoup
from rich.console import Console
from aiohttp import ClientSession
from lib.logger import logger, col
from pathlib import Path as PosixPath
from typing import Dict, Union, Optional, Any
import asyncio, random, re, aiofiles, json, os, logging
from humanize import naturalsize as get_natural_sizes
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    BarColumn, 
    TextColumn, 
    DownloadColumn, 
    TransferSpeedColumn, 
    TimeRemainingColumn
)

class Helper:

    @staticmethod
    def parse(string: str) -> BeautifulSoup:
        return BeautifulSoup(
            string, 'html.parser'
        )

    @staticmethod
    async def saveLog(
        username: str,
        content: Union[Dict[str, Any], str],
        fname: Optional[str] = ""
    ):
        """just for save any content.

        :param str username: username to create/check folder.
        :param Union[Dict[str, Any], str] content: content to write.
        :param Optional[str] fname: _description_, defaults to ""
        """        
        fpath = os.path.realpath(f"./Users/{username}")
        if not os.path.exists(fpath):
            os.mkdir(fpath)
            logger.info(f"Creating new folder at: {fpath}")

        fname = os.path.join(fpath, fname)
        async with aiofiles.open(fname, "w", encoding="utf-8") as f:
            await f.write(
                content if not isinstance(
                    content, dict
                ) else json.dumps(
                    content, indent=2
                )
            )
            await f.close()
        logger.info(f"Log saved into: {fname}")
    
    @staticmethod    
    def clear_username(
        username: str,
        validate: Optional[bool] = False
    ) -> Union[str, bool]:
        """sanitize instagram username:
            length[30, lettes, dot, underscore, digits]
        
        :param str username: username.
        :param bool validate: used for validate username.
        :return str|bool
        """
        if not re.match(r"^[a-zA-Z0-9._]{1,30}$", username):
            if not validate:
                return re.sub(
                    r"[^a-zA-Z0-9_.]", "", username)
            return True
        
        if not validate:
            return username
        return True

    @staticmethod
    async def delay(sec: int) -> None:
        """just cooldown

        :param int sec: int
        """
        for i in range(sec, 0, -1):
            print(f" [{col.YELLOW}Delay{col.RESET}] Avoid Request Spam For: {col.GREEN}{i}{col.RESET}\r", end="", flush=True)
            await asyncio.sleep(1)
        return

    @staticmethod
    def setVerbose(verbose: bool) -> None:
        """set level to `debug` instead default is `info` for verbose.
        :return _type_: void.
        """
        if verbose:
            return logging.getLogger().setLevel(
                logging.DEBUG
            )
        return verbose
    
    @staticmethod
    def get_valid_filename(url: str) -> Union[None, str]:
        """noway for getting pretty filename, bcs one post have multiple media.
        it's skipped if url doesn't match.

        :param str url: raw content url.
        :return str: _description_
        """        
        if (basename := re.search(r"^https?\:\/\/[^<]+\/q\/(?P<filename>[^\"].*?)\|\|", url)):
            basename = list(basename.groupdict().get('filename')[:25])
            random.shuffle(basename)
            return "".join(basename)

        logger.error(f"ValueError: Cannot find spesific name from url: {url}, skipped!")
        return None
    
    @staticmethod
    def show_table(data: Dict[str, str], title: str = None) -> None:
        """table for profile data.

        :param Dict[str, str] data: data table.
        :param str title: title table, defaults to None
        """
        for k, v in data.items():
            if isinstance(v, list):
                data[k] = f"[..{len(v)} of data..]"
            else:
                continue
        del k, v

        Console().print(
            Panel.fit(
                '\n'.join(map(
                    lambda x: f"[bold]{x[0]}:[/bold] {x[1]}",
                    dict(sorted(
                        data.items()
                    )).items()
                )), 
                title="information" if not title else title,
                border_style="blue"
            )
        )

    @staticmethod
    async def _downloadContent(**kwargs: Dict[str, str]) -> None:
        """content downloader -
        it will create new folder based suplied username or as default `picuki_media`.

        :kwrags.url: str: target url.
        :kwargs.username: str/optional: username for create new folder.
        :kwargs.type: str: the type media want to downloaded.
        """        
        urlContent = kwargs.get('url')
        username = kwargs.get('username')
        assert urlContent is not None, "stopped, nothing url to download!"

        media_type = kwargs.get('type')
        output = os.path.realpath(f"Users/{username}")

        """
        create new folder based media type.
        """
        if not os.path.exists(output):
            os.mkdir(output)
            logger.info(f"New folder created in: {output}")
        for folder in ('images', 'videos', 'thumbnails'):
            folder_path = os.path.join(output, folder)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

        filename = os.path.join(
            f"{output}/{media_type}", Helper.get_valid_filename(
                urlContent
            )
        )
        if not filename:
            return filename

        """there's no best way to check file alredy downloaded or not, 
        cause filename always generated randomly. 
        """        
        async with ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }) as session:
            async with session.get(urlContent) as response:
                """
                no extname in url, stoped if cannot find it on headers.
                """
                extension = response.headers.get('Content-Type')
                if not extension:
                    logger.error(f"ValueError: Cannot get mimetype of content: {urlContent}")
                    return

                filename = "{}.{}".format(filename, extension.split('/')[-1])
                if not os.path.exists(filename):
                    async with aiofiles.open(filename, "wb") as f:
                        with Progress(
                            SpinnerColumn(speed=1.5),
                            TextColumn("[green] Downloading..", justify="right"),
                            BarColumn(),
                            "[progress.percentage]{task.percentage:>3.0f}%",
                            DownloadColumn(
                                binary_units=False
                            ),
                            TransferSpeedColumn(),
                            TimeRemainingColumn(),
                            console=Console(),
                            transient=True
                        ) as progress:
                            task = progress.add_task(
                                "[green] Downloading..", total=int(response.headers.get('content-length', 0))
                            )
                            async for content in response.content.iter_chunks():
                                await f.write(
                                    content[0]
                                )
                                progress.update(
                                    task, advance=len(content[0])
                                )
                            await f.close()
                            progress.stop()
                    Console().print(f"[green] Completed..saved as: [blue]{filename}")
                else:
                    Console().print(f"[green] SKipping.. [blue]{filename} [green] file exist!")


