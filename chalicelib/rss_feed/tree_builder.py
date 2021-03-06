from smart_open import open
from chalicelib.rss_feed import merkle_tree
from chalicelib.utils import util

from chalicelib.rss_feed import parser

from chalicelib.myconstants import BUCKET_PATH


def create_tree_node(value, article_title):
    return merkle_tree.MerkleTreeNode(value, article_title)


def build_tree_nodes_list_from_article_list(articles):
    tree_nodes = []
    for article in articles:
        tree_nodes.append(
            create_tree_node(util.hash_object(parser.get_article_content())), article.find("guid").text.split("/")[-1]
        )
    return tree_nodes


def build_tree_nodes_list_from_bucket(feed_url, start_time, mandatory_articles=[]):
    tree_nodes = []
    articles = parser.get_article_list_from_bucket(feed_url, start_time)
    for article in articles:
        with open(BUCKET_PATH + "/" + article, "r") as f:
            if article.split("/")[-1] in mandatory_articles:
                tree_nodes.append(create_tree_node(util.hash_object(f.read()), article.split("/")[-1]))
    return tree_nodes


def build_parent_node(node1, node2):
    parent_hash = util.concatenated_hash(node1.value, node2.value)
    parent = merkle_tree.MerkleTreeNode(parent_hash)
    parent.left = node1
    parent.right = node2
    return parent


def build_merkle_tree(tree_nodes):
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
