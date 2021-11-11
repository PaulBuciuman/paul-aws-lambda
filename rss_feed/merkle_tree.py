import os
import hashlib
import datetime as dt
from smart_open import open
import boto3

PATH1 = "rss_feed/web_pages1/"
PATH2 = "rss_feed/web_pages2/"


s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors/"


def hash_file(file):
    return hashlib.sha256(file.read().encode("utf-8")).hexdigest()


def concatenated_hash(hash1, hash2):
    conc_hash = hash1 + hash2
    return hash(conc_hash)


def build_tree_nodes_list(save_date):
    # path = "rss_feed/" + save_date
    prefix = "Paul/" + save_date + "/"
    tree_nodes = []
    # files = [f for f in os.listdir(path)]
    files = [f for f in BUCKET.objects.filter(Prefix=prefix, Delimiter="/")]
    for file in files:
        print(file.key)
        # with open(os.path.join(path, file), "r") as f:
        with open(BUCKET_PATH + file.key, "r") as f:
            # print(hash_file(f))
            # print(f.read())
            tree_nodes.append(MerkleTreeNode(hash_file(f), file.key.split("/")[-1]))
            # print(f.read())
    return tree_nodes


def build_parent_node(node1, node2):
    parent_hash = concatenated_hash(node1.value, node2.value)
    parent = MerkleTreeNode(parent_hash)
    parent.left = node1
    parent.right = node2
    return parent


def build_merkle_tree(files_list):
    tree_nodes = build_tree_nodes_list(files_list)

    while len(tree_nodes) != 1:
        temp = []
        for i in range(0, len(tree_nodes), 2):
            node1 = tree_nodes[i]
            if i + 1 < len(tree_nodes):
                node2 = tree_nodes[i + 1]
            else:
                temp.append(tree_nodes[i])
                break
            parent = build_parent_node(node1, node2)
            temp.append(parent)
        tree_nodes = temp
    return tree_nodes[0]


def tree_size(root):
    pass


def compare_merkle_trees(root1, root2, diff_articles=[]):
    if tree_size(root1) != tree_size(root2):
        print("Trees have different sizes!")
        return None
    if root1 is not None and root2 is not None:
        if root1.value != root2.value:
            if root1.article_title is None and root2.article_title is None:
                compare_merkle_trees(root1.left, root2.left, diff_articles)
                compare_merkle_trees(root1.right, root2.right, diff_articles)
            else:
                diff_articles.append(root1.article_title)
    return diff_articles


def print_merkle_tree(root, level=0):
    if root is not None:
        print_merkle_tree(root.left, level + 1)
        print(" " * 4 * level + "->", root.value)
        print_merkle_tree(root.right, level + 1)


class MerkleTreeNode:
    def __init__(self, value, article_title=None):
        self.left = None
        self.right = None
        self.value = value
        self.article_title = article_title


d1 = dt.datetime(2021, 11, 10)
d2 = dt.datetime(2021, 11, 11)

root_node1 = build_merkle_tree(str(d1.date()))
root_node2 = build_merkle_tree(str(d2.date()))

diff_articles = compare_merkle_trees(root_node1, root_node2)
print("Articles with differences: ")
print(diff_articles)
