import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import datetime as dt
import urllib.request as urllib2
from smart_open import open
import shutil
import os

URL = "https://www.buzzfeed.com/world.xml"

BUCKET_PATH = "s3://aws-lambda-juniors"

image_extensions = [".jpg", ".jpeg", ".png", ".gif"]


def write_html(content, path, key):
    with open(
        BUCKET_PATH + "/Paul/" + str(date.today() + dt.timedelta(days=0)) + "/" + path + "/" + key + ".html",
        "wb",
    ) as fid:
        fid.write(content)


def write_image(image, path, key):
    with open(
        BUCKET_PATH + "/Paul/" + str(date.today() + dt.timedelta(days=0)) + "/" + path + "/" + key,
        "wb",
    ) as fid:
        shutil.copyfileobj(image.raw, fid)


def parse_images(page):
    images = {}
    for img_tag in page.find_all("img"):
        for attr, value in img_tag.attrs.items():
            if str(value).startswith("https"):
                images[str(value)] = requests.get(str(value), stream=True)
    return images


def convert_url_to_bs(url):
    html_text = requests.get(url).text
    rss_feed = BeautifulSoup(html_text, "html.parser")
    return rss_feed


def get_item_title(item_url):
    return item_url.split("/")[-1]


def get_articles_from_rss(rss_feed_url, d1, d2):
    rss_feed = convert_url_to_bs(rss_feed_url)
    for article in rss_feed.find_all("item"):
        pub_date_str = article.find("pubdate").get_text()[0:16]
        pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y")
        if d1 < pub_date < d2:
            article_url = article.find("guid").get_text()
            yield article_url


def download_html(article_url, path):
    page = urllib2.urlopen(article_url)
    page_content = page.read()
    # local_path = get_local_path(path, get_item_title(article_url) + ".html")
    # bucket_path = get_bucket_path(path, get_item_title(article_url), get_item_title(article_url) + ".html")
    with open(
        get_bucket_path(path, get_item_title(article_url), get_item_title(article_url) + ".html"),
        "wb",
    ) as fid:
        fid.write(page_content)


def get_local_path(path, item):
    local_path = os.path.join(path, item)
    return local_path


def get_bucket_path(path, article, item):
    bucket_path = path + "/Paul/" + str(date.today() + dt.timedelta(days=0)) + "/" + article + "/" + item + ".html"
    return bucket_path


def download_assets(article_url, path):
    article = convert_url_to_bs(article_url)
    images = parse_images(article)
    count = 0
    # bucket_path = get_bucket_path(path, get_item_title(article_url), get_item_title(image_url) + ".html")

    for image_url, image_file in images.items():
        count += 1
        with open(
            # get_local_path(path, get_item_title(image_url) + ".html"),
            get_bucket_path(path, get_item_title(article_url), get_item_title(image_url) + ".html"),
            "wb",
        ) as fid:
            shutil.copyfileobj(image_file.raw, fid)
    return count
