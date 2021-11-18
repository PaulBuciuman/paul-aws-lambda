from chalice import Chalice
import boto3
from smart_open import open
from chalicelib.rss_feed.parse_rss import (
    get_articles_from_rss,
    download_html,
    get_bucket_path,
    get_item_title,
    download_assets,
)
from chalicelib.rss_feed.merkle_tree import compare_merkle_trees, build_merkle_tree, articles_exist
import datetime as dt
import json


# @app.route("/read_article")
def pb_read_articles_from_rss(event, context):
    url = "https://www.buzzfeed.com/world.xml"
    d1 = dt.datetime(2021, 6, 29)
    d2 = dt.datetime(2021, 7, 1)
    for article in get_articles_from_rss(url, d1, d2):
        yield article
