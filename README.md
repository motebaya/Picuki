<div align="center">
    <h2>Picuki</h2>

---

Instagram bulk profile media downloader

[![python](https://img.shields.io/badge/python-3.10.6-green?logo=python&logoColor=yellow)](https://www.python.org/downloads/release/python-3100/)
[![Scraper](https://img.shields.io/badge/page-scrapper-blue?logo=strapi&logoColor=blue)](https://example.com)
[![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.12.2-red?logo=python&logoColor=yellow)](https://pypi.org/project/beautifulsoup4/)
[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg?logo=github)](https://opensource.org/licenses/MIT)
[![total stars](https://img.shields.io/github/stars/motebaya/Picuki.svg?style=social)](https://github.com/motebaya/Picuki/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/motebaya/Picuki.svg?style=social)](https://github.com/motebaya/Picuki/network/members)

</div>

### Features

- [x] save log output to file
- [x] Asynchronous requests
- [x] dump media id by username
- [x] get short info by username
- [x] bulk download images, thumbnails, videos by username

### Install

```
git clone https://github.com/motebaya/Picuki --depth=1
cd Picuki
python -m pip install requirements.txt
python cli.py
```

- **note**: recommended using `python3.10`

### CLI usage

- `-u`, `--username`: **str** spesific instagram username
- `-d`, `--dump`: **str** dumper options, [profile, post]
- `l`, `--limit`: **int** set limit for dump media id/post, `_default`: 50.
- `-D`, `--download-post`: **File** get and download content by suplied media id json file.
- `-t`, `--type`: **str** set media type to download. [images, videos, thumbnails].
- `-V`, `--verbose`: enable debug mode, `default`: off

default output downloaded media in `./<currentDir>/Users/<username>/<mediaType>`.

<details>
<summary> - Tree view </summary>
<br>
<pre>
Users
└── johnSmith
    ├── images
    │   ├── 5eLIdnNxZHGmuN02jNDWB9YIh.jpeg
    │   ├── hNBuNDHm02I59jWxLGNdnIZYe.jpeg
    │   ├── INDImedW0G9hZn2BNxHNu5jYL.jpeg
    │   ├── NajxY8BNSxec3fdYu0jKnSfhx.jpeg
    │   └── NBNILYhZGjd5Wnu0mHeNI9x2D.jpeg
    ├── mediaID.json
    ├── profile.json
    ├── thumbnails
    └── videos
4 directories, 7 files
</pre>
</details>

### Example Usage:

<details>
<summary>
- Dump media id by username.
</summary>
<pre>
❯ python cli.py -u username -d post -l 12
 00:18:52 Info:HTTP Request: GET https://www.picuki.com/profile/username "HTTP/1.1 200 OK" 
╭──────── information ────────╮
│ bio: this biography         │
│ followers: 4,755            │
│ following: 2,177            │
│ full_name: Im Instagram User│
│ total_posts: 45             │
│ username: @username         │
╰─────────────────────────────╯
 00:18:52 Info:grabbing media id with limit set: 12 
 00:18:52 Info:Total media ID grabbed: 12 
 00:18:52 Info:Saving result.. 
 00:18:52 Info:Log saved into: /dir/Users/username/mediaID.json 
╭──── 'media id report' ────╮
│ mediaID: [..12 of data..] │
│ username: username        │
╰───────────────────────────╯
</pre>
</details>

<details>
<summary>
- Download post by media id file.
</summary>
<pre>
❯ python cli.py -D Users/username/mediaID.json -t images
╭─────── information ───────╮
│ mediaID: [..24 of data..] │
│ username: username        │
╰───────────────────────────╯
 23:37:26 Info:24 media id loaded.. 
 23:37:26 Info:Starting download: 24 Items. 
 23:37:26 Info:Processing: 3188...->1 of 24 
 23:37:28 Info:HTTP Request: GET https://www.picuki.com/media/3188... "HTTP/1.1 200 OK" 
╭──────── information ────────╮
│ caption: here caption       │
│ comments_count: 0           │
│ likes_count: 1 likes        │
│ name: @username             │
│ time: 2 months ago          │
╰─────────────────────────────╯
 23:37:28 Info:Downloading: 4 images from ID:3188...
 23:37:28 Info:Downloading images: 1 of 4 
 Completed..saved as: /dir/Picuki/Users/username/images/FDfada...jpeg
 --- sniff ---
 23:37:41 Info:Processing: 3189...->2 of 24 
 23:37:44 Info:HTTP Request: GET https://www.picuki.com/media/3189... "HTTP/1.1 200 OK"
--- sniff ---
</pre>
</details>

<details>
<summary>
- Direct bulk download by username.
</summary>
<pre>
python cli.py -u username -t images
</pre>
</details>

### Disclaimer

This project doesn't use my own site for scraping, and it doesn't use the official Instagram API or any external API's from service providers, etc.

It only use one website: [Picuki.com](https://picuki.com). this site registered since 2019 according to [who.is](https://who.is/whois/picuki.com) and still alive and normal until now.

There's no limit how many website can handle your requests normally unless you test it directly.

I tested it by downloading 500 posts, and it worked without any issues at all. so, i suggest not changing the cooldown/delay in the code to avoid spam due to continuous consecutive requests!

## License

This project is licensed under the [MIT License](LICENSE).
