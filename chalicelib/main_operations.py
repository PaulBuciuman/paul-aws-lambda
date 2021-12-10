from chalicelib.rss_feed.feed_to_s3_operations import (
    read_start_time,
    write_feed_to_s3,
    download_all_htmls,
    insert_old_articles,
    get_only_new_articles,
    append_to_feed,
)

from chalicelib.rss_feed.tree_to_s3_operations import read_tree_from_s3, append_to_tree, generate_tree
from chalicelib.rss_feed.merkle_tree import compare_merkle_trees
from chalicelib.rss_feed.parser import read_feed_xml_from_bucket
from datetime import datetime as dt

from chalicelib.podcast_feed.podcast_to_s3_operations import download_podcasts


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


def run_podcast_download(start_time, podcast_url, postcast_id, d1, d2):
    date1 = dt.strptime(d1, "%Y-%m-%d")
    date2 = dt.strptime(d2, "%Y-%m-%d")
    download_podcasts(podcast_url, postcast_id, date1, date2, start_time)
