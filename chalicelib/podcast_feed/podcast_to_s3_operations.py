import yt_dlp
from smart_open import open

from chalicelib.utils import util
from chalicelib.myconstants import PODCAST_ID
from chalicelib.rss_feed.parser import read_feed_xml_from_online
from datetime import datetime


def download_locally(entry):
    ydl_opts = {"format": "bestaudio", "outtmpl": "/tmp/" + entry.find("title").text + ".%(ext)s"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(entry.find("media:content")["url"])


def read_video_from_local(entry):
    with open("/tmp/" + entry.find("title").text + ".webm", "rb") as v:
        return v.read()


def write_video_to_s3(entry, podcast_id, start_time, video):
    with open(
        util.bucket_path(podcast_id, start_time) + "/" + entry.find("title").text + ".webm",
        "wb",
    ) as s3:
        s3.write(video)


def download_podcast(entry, podcast_id, start_time):
    download_locally(entry)
    video = read_video_from_local(entry)
    write_video_to_s3(entry, podcast_id, start_time, video)


def download_podcasts(podcast_url, podcast_id, date1, date2, start_time):
    feed = read_feed_xml_from_online(podcast_url)
    for entry in feed.find_all("entry"):
        date_str = entry.find("published").get_text()[0:-6]
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        if date1 <= date <= date2:
            download_podcast(entry, podcast_id, start_time)
