from chalice import Chalice
import boto3
from chalicelib.rss_feed.feed_to_s3_operations import (
    read_start_times,
    write_feed_to_s3,
    download_all_htmls,
    generate_tree,
    insert_old_articles,
    get_only_new_articles,
    append_to_feed,
)
from chalicelib.rss_feed.tree_to_s3_operations import read_tree_from_s3, append_to_tree
from chalicelib.rss_feed.merkle_tree import compare_merkle_trees
from chalicelib.rss_feed.parser import read_feed_xml_from_bucket
from datetime import datetime
import json
import requests

app = Chalice(app_name="lambda-project")
BUCKET_PATH = "s3://aws-lambda-juniors"


s3 = boto3.client("s3")
lambda_client = boto3.client("lambda")

URL = "https://www.buzzfeed.com/world.xml"


def initial_population(feed_url):
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_feed_to_s3(feed_url, start_time, None, False)
    download_all_htmls(feed_url, start_time)
    generate_tree(feed_url, start_time)


def run_trust_mode(feed_url):
    start_time = read_start_times(feed_url)[-2]
    bucket_feed = read_feed_xml_from_bucket(feed_url, start_time)
    new_articles = get_only_new_articles(feed_url, bucket_feed)

    append_to_feed(feed_url, start_time, bucket_feed, new_articles)
    append_to_tree(feed_url, new_articles, start_time)
    return new_articles


def run_validation_mode(feed_url):
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    write_feed_to_s3(feed_url, start_time, None, False)
    download_all_htmls(feed_url, start_time)

    start_time_original = read_start_times(feed_url)[-2]
    start_time_new = read_start_times(feed_url)[-1]

    print(f"{start_time_original} -- {start_time_new}")

    insert_old_articles(feed_url, start_time_original, start_time_new)
    generate_tree(feed_url, start_time, start_time_original)

    original_tree = read_tree_from_s3(feed_url, start_time_original)
    new_tree = read_tree_from_s3(feed_url, start_time_new)
    # print_merkle_tree(original_tree)
    # print("\n")
    # print_merkle_tree(new_tree)
    # print(f"{original_tree.value} \n{new_tree.value}")
    diff_articles = compare_merkle_trees(original_tree, new_tree)
    return diff_articles


@app.route("/initial/{feed_url}")
def pb_initial_population(feed_url):
    initial_population(feed_url)


@app.route("/trust_mode/{feed_url}")
def pb_trust_mode(feed_url):
    new_articles = run_trust_mode(feed_url)
    return new_articles


@app.route("/validation_mode/{feed_url}")
def pb_validation_mode(feed_url):
    different_articles = run_validation_mode(feed_url)
    return different_articles


# @app.route("/read_article/{date1}/{date2}")
# def pb_read_articles_from_rss(date1, date2):
#     articles = {}
#     for article in get_articles_from_rss(URL, date1, date2):
#         articles[get_item_title(article)] = article
#     return articles


# @app.route("/download_html/{date1}/{date2}")
# def pb_download_html(date1, date2):
#     response = requests.get(f"https://dr2g4112b2.execute-api.us-east-2.amazonaws.com/api/read_article/{date1}/{date2}")
#     json_object = json.loads(response.text)
#     for key, value in json_object.items():
#         download_html(value, BUCKET_PATH)
#     return response.text


# @app.route("/download_images/{date1}/{date2}")
# def pb_download_images(date1, date2):
#     response = requests.get(f"https://dr2g4112b2.execute-api.us-east-2.amazonaws.com/api/read_article/{date1}/{date2}")
#     json_object = json.loads(response.text)
#     for key, value in json_object.items():
#         download_assets(value, BUCKET_PATH)
#     return response.text


# reuse lambda to save podcast files as well - make it generic s that it doesn't care what it downloads
# try to use youtube rss, youtube dl, take only the audio


# @app.route("/compare")
# def pb_compare_merkle_trees():
#     d1 = dt.datetime(2021, 11, 17)
#     d2 = dt.datetime(2021, 11, 18)

#     if articles_exist(d1) and articles_exist(d2):
#         root1 = build_merkle_tree(str(d1.date()))
#         root2 = build_merkle_tree(str(d2.date()))
#         diff_articles = compare_merkle_trees(root1, root2)
#         print("Articles with differences: ")
#         print(diff_articles)
#     else:
#         print("Comparison not possible.One of the dates doesn't exist!")
