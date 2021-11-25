import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.request as urllib2
from smart_open import open
import shutil
import utils
import boto3


URL = "https://www.buzzfeed.com/world.xml"

BUCKET_PATH = "s3://aws-lambda-juniors"

image_extensions = [".jpg", ".jpeg", ".png", ".gif"]

LOCAL_PATH = "chalicelib/new_feed.xml"

client = boto3.client("s3")
paginator = client.get_paginator("list_objects_v2")


# s3://[user_id]/OPML  # <-Keeps all the feeds monitored
# s3://[user_id]/[feed_url_hash]/[start_time]/rss_feed.xml
# s3://[user_id]/[feed_url_hash]/[start_time]/merkle_tree
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/metadata.json
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/html.html
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/js/[js_url_hash].js
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/img/[img_url_hash].[img_ext]
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/css/[css_url_hash].css


# def articles_exist(save_date):
#     date_exists = False
#     for key in BUCKET.objects.all():
#         if str(save_date.date()) in str(key):
#             date_exists = True
#     if not date_exists:
#         print(f"There is no article from {save_date.date()}")
#     return date_exists


def parse_images(page):
    images = {}
    for img_tag in page.find_all("img"):
        for attr, value in img_tag.attrs.items():
            if str(value).startswith("https"):
                images[str(value)] = requests.get(str(value), stream=True)
    return images


def convert_page_to_bs(url):
    html_text = requests.get(url).text
    rss_feed = BeautifulSoup(html_text, "html.parser")
    return rss_feed


def read_feed_xml_from_online(feed_url):
    feed = urllib2.urlopen(feed_url)
    return BeautifulSoup(feed.read(), "lxml")


def read_feed_xml_from_bucket(feed_url, start_time):
    with open(
        BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/" + str(start_time) + "/rss_feed.xml",
        "r",
    ) as f:
        return BeautifulSoup(f.read(), "lxml")


def read_feed_xml_from_local():
    with open(
        LOCAL_PATH,
        "r",
    ) as f:
        return BeautifulSoup(f.read(), "lxml")


def get_article_list_from_bucket(feed_url, start_time):
    articles = []
    prefix = "Paul/" + utils.hash_object(feed_url) + "/" + str(start_time) + "/items/"
    page_iterator = paginator.paginate(Bucket="aws-lambda-juniors", Prefix=prefix)
    for page in page_iterator:
        for item in page["Contents"]:
            if item["Key"].endswith(".html"):
                articles.append(item["Key"])
    return articles


def get_new_articles(feed, most_recent_date):
    new_articles = []
    for item in feed.find_all("item"):
        pub_date_str = item.find("pubdate").get_text()[0:-6]
        pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S")
        if pub_date > most_recent_date:
            new_articles.append(item)
    return new_articles


def append_new_articles_to_feed(feed, articles):
    for item in reversed(articles):
        new_tag = feed.new_tag("item")
        new_tag.contents = item.contents
        feed.rss.channel.image.insert_after(new_tag)
    with open(LOCAL_PATH, "w") as f:
        f.write(str(feed))


def most_recent_article_date(feed_xml):
    first_item = feed_xml.find("item")
    pub_date_str = first_item.find("pubdate").get_text()[0:-6]
    # pub_date_str = "Fri, 11 Nov 2021"
    pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S")
    return pub_date


def get_article_content(article):
    article_url = article.find("guid").text
    page = urllib2.urlopen(article_url)
    return page.read()