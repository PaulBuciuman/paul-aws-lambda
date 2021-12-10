import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.request as urllib2
from smart_open import open
import shutil
from chalicelib.utils import util

from chalicelib.myconstants import paginator, BUCKET_NAME


# s3://[user_id]/OPML  # <-Keeps all the feeds monitored
# s3://[user_id]/[feed_url_hash]/[start_time]/rss_feed.xml
# s3://[user_id]/[feed_url_hash]/[start_time]/merkle_tree
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/metadata.json
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/html.html
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/js/[js_url_hash].js
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/img/[img_url_hash].[img_ext]
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/css/[css_url_hash].css


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
    return util.convert_to_bs(feed.read())


def read_feed_xml_from_bucket(feed_url, start_time):
    with open(
        util.bucket_path(feed_url, start_time) + "/rss_feed.xml",
        "r",
    ) as f:
        return util.convert_to_bs(f.read())


# def read_feed_xml_from_local():
#     with open(
#         LOCAL_PATH,
#         "r",
#     ) as f:
#         return util.convert_to_bs(f.read())


def get_article_list_from_bucket(feed_url, start_time):
    articles = []
    prefix = "Paul/" + util.hash_object(feed_url) + "/" + str(start_time) + "/items/"
    page_iterator = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)
    for page in page_iterator:
        for item in page["Contents"]:
            if item["Key"].endswith(".html"):
                articles.append(item["Key"])
    return articles


def get_new_articles(feed, most_recent_date):
    new_articles = []
    for item in feed.find_all("item"):
        pub_date_str = item.find("pubdate").get_text()[0:-6]
        pub_date = util.format_string_date(pub_date_str)
        if pub_date > most_recent_date:
            new_articles.append(item)
    return new_articles


def append_new_articles_to_feed(feed, articles):
    for item in reversed(articles):
        new_tag = feed.new_tag("item")
        new_tag.contents = item.contents
        feed.rss.channel.image.insert_after(new_tag)
    return str(feed)


def most_recent_article_date(feed_xml):
    first_item = feed_xml.find("item")
    pub_date_str = first_item.find("pubdate").get_text()[0:-6]
    pub_date = util.format_string_date(pub_date_str)
    return pub_date


def get_article_content(article):
    article_url = article.find("guid").text
    page = urllib2.urlopen(article_url)
    return page.read()
