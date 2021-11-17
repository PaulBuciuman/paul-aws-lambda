from datetime import date
import datetime as dt
import boto3
from smart_open import open
from chalicelib.rss_feed.parse_rss import get_article_from_rss, download_html, download_assets
from os import listdir

s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors/"


# def get_files_from_s3(date):
#     prefix = "Paul/" + str(date) + "/"
#     files = [f for f in BUCKET.objects.filter(Prefix=prefix, Delimiter="/")]
#     return files


def read_files_from_folder(path):
    files = [f for f in listdir(path)]
    return files


def test_read_articles():
    url = "https://www.buzzfeed.com/world.xml"
    d1 = dt.datetime(2021, 9, 1)
    d2 = dt.datetime(2021, 9, 20)
    article_count = 0
    for article_url in get_article_from_rss(url, d1, d2):
        article_count += 1

    assert article_count > 0


def test_download_html():
    url = "https://www.buzzfeed.com/world.xml"
    local_path = "chalicelib/test_files/"
    d1 = dt.datetime(2021, 9, 1)
    d2 = dt.datetime(2021, 9, 20)
    count = 0
    for article_url in get_article_from_rss(url, d1, d2):
        count += 1
        download_html(article_url, local_path)

    files = read_files_from_folder(local_path)
    assert count == len(files)


def test_download_assets():
    url = "https://www.buzzfeed.com/world.xml"
    local_path = "chalicelib/test_assets/"
    d1 = dt.datetime(2021, 9, 1)
    d2 = dt.datetime(2021, 9, 20)
    count = 0
    for article_url in get_article_from_rss(url, d1, d2):
        count += download_assets(article_url, local_path)

    files = read_files_from_folder(local_path)
    assert count >= len(files) > 0
