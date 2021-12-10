import hashlib
from datetime import datetime as dt
import datetime
from bs4 import BeautifulSoup
from chalicelib.myconstants import BUCKET_PATH


def concatenated_hash(hash1, hash2):
    conc_hash = hash_object(hash1 + hash2)
    return conc_hash


def idempotent_check(start_time, all_start_times):
    valid = False
    print(f"START TIME: {start_time} \n ALL TIMES: {all_start_times}")
    valid = any(
        time in all_start_times
        for time in [
            str(dt.strptime(start_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=4)),
            str(dt.strptime(start_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=3)),
            str(dt.strptime(start_time, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=2)),
        ]
    )

    return not valid


def hash_object(file):
    return hashlib.sha256(file.encode("utf-8")).hexdigest()


def is_power_of_2(n):
    if n == 1:
        return True
    elif n % 2 == 0:
        return is_power_of_2(n / 2)
    else:
        return False


def bucket_path(feed_url, start_time):
    return BUCKET_PATH + "/Paul/" + hash_object(feed_url) + "/" + start_time


def get_item_title(item_url):
    return item_url.split("/")[-1]


def get_item_url_hash(item_url):
    return item_url.split("/")[-2]


def generate_current_time():
    return dt.now().strftime("%Y-%m-%d %H:%M:%S")


def get_base_path(bucket_path, feed_url, start_time):
    return bucket_path + "Paul/" + hash_object(feed_url) + "/" + start_time + "/merkle_tree.pkl"


def convert_to_bs(obj):
    return BeautifulSoup(obj, "lxml")


def format_string_date(string_date):
    return datetime.strptime(string_date, "%a, %d %b %Y %H:%M:%S")
