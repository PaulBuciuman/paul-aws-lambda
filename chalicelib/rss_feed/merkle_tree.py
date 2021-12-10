from chalicelib.utils import util


class MerkleTreeNode:
    def __init__(self, value, article_title=None):
        self.left = None
        self.right = None
        self.value = value
        self.article_title = article_title


def print_merkle_tree(root, level=0):
    if root is not None:
        print_merkle_tree(root.right, level + 1)
        print(" " * 4 * level + "->", root.value)
        print_merkle_tree(root.left, level + 1)


def complete_tree(root):
    size = tree_size(root)
    if util.is_power_of_2(size + 1):
        return True
    else:
        return False


def is_leaf(node):
    if node.article_title is not None:
        return True
    else:
        return False


def tree_size(root):
    left_size = tree_size(root.left) if root.left else 0
    right_size = tree_size(root.right) if root.right else 0
    return left_size + right_size + 1


def compare_merkle_trees(root1, root2, diff_articles=[]):
    if root1 is not None and root2 is not None:
        if root1.value != root2.value:
            if root1.article_title is None and root2.article_title is None:
                compare_merkle_trees(root1.left, root2.left, diff_articles)
                compare_merkle_trees(root1.right, root2.right, diff_articles)
            else:
                diff_articles.append(root1.article_title)
    return diff_articles
