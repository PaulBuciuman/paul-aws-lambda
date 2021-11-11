import os
import hashlib

PATH = "rss_feed/web_pages/"


def hash_file(file):
    return hashlib.sha256(file.read().encode("utf-8")).hexdigest()


def get_files_hashes(path):
    file_hashes = []
    files = [f for f in os.listdir(path)]
    for file in files:
        with open(os.path.join(path, file), "r") as f:
            file_hashes.append(hash_file(f))
    return file_hashes


def concatenated_hash(hash1, hash2):
    conc_hash = hash1 + hash2
    return hash(conc_hash)


def build_tree_nodes_list(files_list):
    tree_nodes = []
    for file in files_list:
        tree_nodes.append(MerkleTreeNode(file))
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


def compare_merkle_trees(root1, root2):
    pass


def print_merkle_tree(root, level=0):
    if root is not None:
        print_merkle_tree(root.left, level + 1)
        print(" " * 4 * level + "->", root.value)
        print_merkle_tree(root.right, level + 1)


class MerkleTreeNode:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value


file_hashes = get_files_hashes(PATH)
root_node = build_merkle_tree(file_hashes)

print_merkle_tree(root_node)
