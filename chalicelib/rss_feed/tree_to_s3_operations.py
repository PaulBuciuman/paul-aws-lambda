from smart_open import open
import pickle
from . import merkle_tree
from .tree_builder import build_parent_node, build_tree_nodes_list_from_article_list
from . import utils
from .constants import BUCKET_PATH


def write_tree_to_s3(feed_url, root, start_time):
    pickle_root = pickle.dumps(root)
    with open(
        BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/" + start_time + "/merkle_tree.pkl",
        "wb",
    ) as fid:
        fid.write(pickle_root)


def read_tree_from_s3(feed_url, start_time):
    with open(
        BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/" + start_time + "/merkle_tree.pkl",
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
