from chalice import Chalice
from chalicelib.rss_feed.feed_to_s3_operations import (
    read_start_times,
    read_start_time,
    write_feed_to_s3,
    download_all_htmls,
    generate_tree,
    insert_old_articles,
    get_only_new_articles,
    append_to_feed,
)
from chalicelib.rss_feed.constants import URL

from chalicelib.rss_feed.tree_to_s3_operations import read_tree_from_s3, append_to_tree
from chalicelib.rss_feed.merkle_tree import compare_merkle_trees
from chalicelib.rss_feed.parser import read_feed_xml_from_bucket
import datetime
from datetime import datetime as dt
import json
import requests
from chalicelib.rss_feed import utils


# !!!!!!!!
# SOMETHING BROKE AND FOR SOME REASON IT DOESN'T WRITE TO S3 ANYMORE,
# BUT IT DOESN'T GIVE ANY ACCESS ERROR! JUST HAVE TO CHECK AGAIN THE
# PART WHERE IT'S WRITTING THE NEW FEED TO S3
# !!!!!!!!


app = Chalice(app_name="lambda-project")


def initial_population(start_time, feed_url):
    write_feed_to_s3(feed_url, start_time, None, False)
    download_all_htmls(feed_url, start_time)
    generate_tree(feed_url, start_time)


def run_trust_mode(feed_url):
    start_time = read_start_time(feed_url)[0]
    bucket_feed = read_feed_xml_from_bucket(feed_url, start_time)
    new_articles = get_only_new_articles(feed_url, bucket_feed)
    print(new_articles)
    append_to_feed(feed_url, start_time, bucket_feed, new_articles)
    append_to_tree(feed_url, new_articles, start_time)
    return new_articles


def run_validation_mode(start_time, feed_url):
    write_feed_to_s3(feed_url, start_time, None, False)
    download_all_htmls(feed_url, start_time)

    start_time_original = read_start_time(feed_url)[0]
    start_time_new = read_start_time(feed_url)[-1]
    insert_old_articles(feed_url, start_time_original, start_time_new)
    generate_tree(feed_url, start_time, start_time_original)

    original_tree = read_tree_from_s3(feed_url, start_time_original)
    new_tree = read_tree_from_s3(feed_url, start_time_new)
    diff_articles = compare_merkle_trees(original_tree, new_tree)
    return diff_articles


@app.route("/initial")
def pb_initial_population():
    start_time = utils.generate_current_time()
    all_start_times = read_start_time(URL)
    if utils.idempotent_check(start_time, all_start_times):
        initial_population(start_time, URL)
    return URL


@app.route("/trust_mode")
def pb_trust_mode():
    new_articles = run_trust_mode(URL)
    return f"New articles appended: {new_articles}"


@app.route("/validation_mode")
def pb_validation_mode():
    start_time = utils.generate_current_time()
    try:
        different_articles = run_validation_mode(start_time, URL)
    except Exception:
        return "Forbidden validation mode before initial feed downloading"
    return f"Articles with differences: {different_articles}"
