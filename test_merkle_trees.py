from datetime import date
import datetime as dt
import boto3
from smart_open import open
from rss_feed.merkle_tree import build_tree_nodes_list, compare_merkle_trees, build_merkle_tree, print_merkle_tree

s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors/"


def ttest_build_tree_nodes():
    d = dt.datetime(2021, 11, 15)
    nodes = build_tree_nodes_list(str(d.date()))
    files = get_files_from_s3(d.date())
    assert len(nodes) == len(files)


def ttest_build_tree_none():
    d1 = dt.datetime(2021, 11, 1)
    nodes = build_merkle_tree(str(d1.date()))
    assert nodes is None


def ttest_compare_trees_true():
    d1 = dt.datetime(2021, 11, 10)
    root1 = build_merkle_tree(str(d1.date()))
    root2 = build_merkle_tree(str(d1.date()))
    diff_articles = compare_merkle_trees(root1, root2, [])
    assert len(diff_articles) == 0


def ttest_compare_trees_false():
    d1 = dt.datetime(2021, 11, 10)
    root1 = build_merkle_tree(str(d1.date()))
    root2 = build_merkle_tree(str(d1.date()), "mutation")
    diff_articles = compare_merkle_trees(root1, root2, [])
    assert len(diff_articles) > 0
