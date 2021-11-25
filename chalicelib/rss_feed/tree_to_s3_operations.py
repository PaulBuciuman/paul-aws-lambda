from datetime import date
from smart_open import open
import boto3
import pickle
from merkle_tree import MerkleTreeNode, is_leaf, complete_tree, print_merkle_tree, compare_merkle_trees
import tree_builder
import utils

# from parse_rss import get_article_content

URL = "https://www.buzzfeed.com/world.xml"

s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors/"


# s3://[user_id]/OPML  # <-Keeps all the feeds monitored
# s3://[user_id]/[feed_url_hash]/[start_time]/rss_feed.xml
# s3://[user_id]/[feed_url_hash]/[start_time]/merkle_tree
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/metadata.json
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/html.html
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/js/[js_url_hash].js
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/img/[img_url_hash].[img_ext]
# s3://[user_id]/[feed_url_hash]/[start_time]/items/[url_hash]/assets/css/[css_url_hash].css


def write_tree_to_s3(feed_url, root, start_time):
    pickle_root = pickle.dumps(root)
    with open(
        BUCKET_PATH + "Paul/" + utils.hash_object(feed_url) + "/" + start_time + "/merkle_tree.pkl",
        "wb",
    ) as fid:
        fid.write(pickle_root)


def read_tree_from_s3(feed_url, start_time):
    with open(
        BUCKET_PATH + "Paul/" + utils.hash_object(feed_url) + "/" + start_time + "/merkle_tree.pkl",
        "rb",
    ) as fid:
        return pickle.load(fid)


initial_size = 10


def build_random_tree(change=False):

    tree_nodes = []
    for i in range(1, initial_size + 1):
        j = 1
        print(i)
        if i == 5 and change:
            j = 0
        tree_nodes.append(MerkleTreeNode(str(i * j), i))
        root = tree_builder.build_merkle_tree(tree_nodes)
    return root


def append_new_articles_to_tree(root, new_node):
    if complete_tree(root):
        new_root = tree_builder.build_parent_node(root, new_node)
        return new_root
    if not is_leaf(root.left) and is_leaf(root.right):
        new_parent = tree_builder.build_parent_node(root.right, new_node)
        root.right = new_parent
        return root
    if not is_leaf(root.left) and not is_leaf(root.right):
        root.right = append_new_articles_to_tree(root.right, new_node)
        return root


def append_to_tree(feed_url, new_articles, start_time):
    new_tree_nodes = tree_builder.build_tree_nodes_list_from_article_list(new_articles)
    tree = read_tree_from_s3(feed_url, start_time)
    write_tree_to_s3(feed_url, tree, start_time)
    # print(tree_size(tree))
    for new_node in new_tree_nodes:
        append_new_articles_to_tree(tree, new_node)
    # print(tree_size(tree))


# root1 = build_random_tree()
# root2 = build_random_tree()

# print_merkle_tree(root1)
# print_merkle_tree(root2)

# diff_articles = compare_merkle_trees(root1, root2)
# print(diff_articles)
# root = build_random_tree()
# print_merkle_tree(root)
# new_node = tree_builder.create_tree_node(str(initial_size + 1), initial_size + 1)
# new_root = append_new_articles_to_tree(root, new_node)
# print_merkle_tree(new_root)
