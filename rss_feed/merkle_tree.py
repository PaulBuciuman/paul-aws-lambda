import os
import hashlib
import datetime as dt
from datetime import datetime
from datetime import date
from smart_open import open
import boto3


s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors/"


client = boto3.client("s3")
paginator = client.get_paginator("list_objects_v2")


def hash_node(file):
    return hashlib.sha256(file.encode("utf-8")).hexdigest()


def concatenated_hash(hash1, hash2):
    conc_hash = hash1 + hash2
    return hash_node(conc_hash)


def articles_exist(save_date):
    date_exists = False
    for key in BUCKET.objects.all():
        if str(save_date.date()) in str(key):
            date_exists = True
    if not date_exists:
        print(f"There is no article from {save_date.date()}")
    return date_exists


def build_tree_nodes_list(save_date, mutation=""):
    prefix = "Paul/" + save_date + "/"
    tree_nodes = []
    # files = [f for f in BUCKET.objects.filter(Prefix=prefix, Delimiter="/")]

    page_iterator = paginator.paginate(Bucket="aws-lambda-juniors", Prefix=prefix)
    for page in page_iterator:
        for item in page["Contents"]:
            if item["Key"].endswith(".html"):
                print(item["Key"])
                with open(BUCKET_PATH + item["Key"], "r") as f:
                    tree_nodes.append(MerkleTreeNode(hash_node(f.read() + mutation), item["Key"].split("/")[-1]))
    return tree_nodes


def build_parent_node(node1, node2):
    parent_hash = concatenated_hash(node1.value, node2.value)
    parent = MerkleTreeNode(parent_hash)
    parent.left = node1
    parent.right = node2
    return parent


def build_merkle_tree(save_date, mutation=""):
    print(save_date)
    tree_nodes = build_tree_nodes_list(save_date, mutation)
    if len(tree_nodes) > 0:
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
    else:
        return None


def compare_merkle_trees(root1, root2, diff_articles=[]):
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
