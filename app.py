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
import requests

app = Chalice(app_name="lambda-project")
BUCKET_PATH = "s3://aws-lambda-juniors"


s3 = boto3.client("s3")
lambda_client = boto3.client("lambda")

URL = "https://www.buzzfeed.com/world.xml"


@app.route("/read_article")
def pb_read_articles_from_rss():
    d1 = dt.datetime(2021, 6, 29)
    d2 = dt.datetime(2021, 7, 1)
    for article in get_articles_from_rss(URL, d1, d2):
        return article


@app.route("/download_html")
def pb_download_html():
    response = requests.get("https://dr2g4112b2.execute-api.us-east-2.amazonaws.com/api/read_article")

    download_html(response.text, BUCKET_PATH)
    return response.text


@app.route("/download_images")
def pb_download_images():
    article_url = ""
    download_assets(article_url, BUCKET_PATH)


# don't hardcode the arguments, parametrize in terminal
# use SQS (chaining lambda functions) - runs automatically
# trigger a lambda functon everytime a url is found, that will upload that image to s3
# reuse lambda to save podcast files as well - make it generic s that it doesn't care what it downloads
# try to use youtube rss, youtube dl, take only the audio

# 3 diff lambdas -
@app.route("/compare")
def pb_compare_merkle_trees():
    d1 = dt.datetime(2021, 11, 17)
    d2 = dt.datetime(2021, 11, 18)

    if articles_exist(d1) and articles_exist(d2):
        root1 = build_merkle_tree(str(d1.date()))
        root2 = build_merkle_tree(str(d2.date()))
        diff_articles = compare_merkle_trees(root1, root2)
        print("Articles with differences: ")
        print(diff_articles)
    else:
        print("Comparison not possible.One of the dates doesn't exist!")
