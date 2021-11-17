import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import datetime as dt
import urllib.request as urllib2
from smart_open import open
import shutil

URL = "https://www.buzzfeed.com/world.xml"
html_text = requests.get(URL).text
rss_feed = BeautifulSoup(html_text, "html.parser")

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


def get_item_title(item_url):
    return item_url.split("/")[-1]


def download_all_between(d1, d2):
    for item in rss_feed.find_all("item"):
        pub_date_str = item.find("pubdate").get_text()[0:16]
        pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y")

        if d1 < pub_date < d2:
            item_url = item.find("guid").get_text()
            image_url = item.find("media:thumbnail")["url"]
            print(item_url)
            page = urllib2.urlopen(item_url)
            file = requests.get(image_url, stream=True)
            page_content = page.read()
            images = parse_images(BeautifulSoup(requests.get(item_url).text, "html.parser"))
            images[item_url] = file
            write_html(page_content, get_item_title(item_url), get_item_title(item_url))
            for image_url, image_file in images.items():
                write_image(image_file, get_item_title(item_url), get_item_title(image_url))


d1 = dt.datetime(2021, 6, 29)
d2 = dt.datetime(2021, 7, 1)

download_all_between(d1, d2)
