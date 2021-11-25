import hashlib


def concatenated_hash(hash1, hash2):
    conc_hash = hash_object(hash1 + hash2)
    return conc_hash


def hash_object(file):
    return hashlib.sha256(file.encode("utf-8")).hexdigest()


def is_power_of_2(n):
    if n == 1:
        return True
    elif n % 2 == 0:
        return is_power_of_2(n / 2)
    else:
        return False


def get_item_title(item_url):
    return item_url.split("/")[-1]


def get_item_url_hash(item_url):
    return item_url.split("/")[-2]
