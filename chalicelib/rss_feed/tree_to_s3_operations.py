from smart_open import open
import pickle
from chalicelib.rss_feed import merkle_tree
from chalicelib.rss_feed.tree_builder import (
    build_parent_node,
    build_tree_nodes_list_from_article_list,
    parser,
    build_merkle_tree,
    build_tree_nodes_list_from_bucket,
)
from chalicelib.utils import util


def write_tree_to_s3(feed_url, root, start_time):
    pickle_root = pickle.dumps(root)
    with open(
        util.bucket_path(feed_url, start_time) + "/merkle_tree.pkl",
        "wb",
    ) as fid:
        fid.write(pickle_root)


def read_tree_from_s3(feed_url, start_time):
    with open(
        util.bucket_path(feed_url, start_time) + "/merkle_tree.pkl",
        "rb",
    ) as fid:
        return pickle.load(fid)


def append_new_articles_to_tree(root, new_node):
    if merkle_tree.complete_tree(root):
        new_root = build_parent_node(root, new_node)
        return new_root
    if merkle_tree.is_leaf(root.right):
        new_parent = build_parent_node(root.right, new_node)
        root.right = new_parent
        return root
    if not merkle_tree.is_leaf(root.right):
        root.right = append_new_articles_to_tree(root.right, new_node)
        return root


def append_to_tree(feed_url, new_articles, start_time):
    new_tree_nodes = build_tree_nodes_list_from_article_list(new_articles)
    tree = read_tree_from_s3(feed_url, start_time)
    write_tree_to_s3(feed_url, tree, start_time)
    for new_node in new_tree_nodes:
        append_new_articles_to_tree(tree, new_node)


def generate_tree(feed_url, start_time, start_time_original=None):
    mandatory_articles = parser.get_article_list_from_bucket(feed_url, start_time)
    mandatory_article_titles = list(map(lambda a: a.split("/")[-1], mandatory_articles))

    if start_time_original is not None:
        mandatory_articles = parser.get_article_list_from_bucket(feed_url, start_time_original)
        mandatory_article_titles = list(map(lambda a: a.split("/")[-1], mandatory_articles))

    tree_nodes = build_tree_nodes_list_from_bucket(feed_url, start_time, mandatory_article_titles)
    tree_root = build_merkle_tree(tree_nodes)
    write_tree_to_s3(feed_url, tree_root, start_time)
    return tree_root
