from datetime import datetime
from datetime import date
import datetime as dt
import urllib.request as urllib2
from smart_open import open
import shutil
from . import utils
from . import parser
from . import tree_builder
from . import tree_to_s3_operations
from .constants import s3, BUCKET, BUCKET_PATH, paginator, client
from io import StringIO


def add_start_time(feed_url, start_time):
    file = start_time
    print(f"adding start_time: {file}")
    try:
        with open(BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/start_times.txt", "r") as fid:
            file = fid.read()
        file = file + "\n" + start_time
    except Exception:
        pass
    with open(
        BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/start_times.txt",
        "w",
    ) as fid:
        fid.write(file)


def read_start_times(feed_url):
    with open(
        BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/start_times.txt",
        "r",
    ) as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


def read_start_time(feed_url):
    start_times = []
    prefix = "Paul/" + utils.hash_object(feed_url) + "/"

    result = client.list_objects(Bucket="aws-lambda-juniors", Prefix=prefix, Delimiter="/")
    if result.get("CommonPrefixes"):
        for start_time in result.get("CommonPrefixes"):
            start_times.append(start_time.get("Prefix").split("/")[-2])
        return start_times
    else:
        return []


def write_feed_to_s3(feed_url, start_time, feed_xml=None, trust_mode=True):
    if feed_xml is None:
        feed_xml = parser.read_feed_xml_from_online(feed_url)
    with open(
        BUCKET_PATH + "/Paul/" + utils.hash_object(feed_url) + "/" + start_time + "/rss_feed.xml",
        "w",
    ) as fid:
        print(start_time)
        print("writting to S333333333333")
        try:
            fid.write(str(feed_xml))
            print("wrote to s3!!!!")
        except Exception as e:
            print(f"Exception: {e}")


def copy_article(feed_url, article_hash, article_title, start_time_original, start_time_new):
    copy_source = {
        "Bucket": BUCKET,
        "Key": "Paul/"
        + utils.hash_object(feed_url)
        + "/"
        + start_time_original
        + "/items/"
        + article_hash
        + "/"
        + article_title,
    }

    dest_source = s3.Bucket(BUCKET)
    dest_source.copy(
        copy_source,
        "Paul/" + utils.hash_object(feed_url) + "/" + start_time_new + "/items/" + article_hash + "/" + article_title,
    )


def get_bucket_path(path, article, item):
    bucket_path = path + "/Paul/" + str(date.today() + dt.timedelta(days=0)) + "/" + article + "/" + item
    return bucket_path


def download_assets(article_url, path):
    article = parser.convert_page_to_bs(article_url)
    images = parser.parse_images(article)
    count = 0
    for image_url, image_file in images.items():
        count += 1
        with open(
            # get_local_path(path, get_item_title(image_url) + ".html"),
            get_bucket_path(path, utils.get_item_title(article_url), utils.et_item_title(image_url)),
            "wb",
        ) as fid:
            shutil.copyfileobj(image_file.raw, fid)
    return count


def download_html(feed_url, article_url, start_time):
    page = urllib2.urlopen(article_url)
    page_content = page.read()
    with open(
        BUCKET_PATH
        + "/Paul/"
        + utils.hash_object(feed_url)
        + "/"
        + start_time
        + "/items/"
        + utils.hash_object(article_url)
        + "/"
        + utils.get_item_title(article_url)
        + ".html",
        "w",
    ) as fid:
        fid.write(str(page_content))


def download_all_htmls(feed_url, start_time, most_recent_date=None):
    bucket_feed = parser.read_feed_xml_from_bucket(feed_url, start_time)
    count = 0
    for item in bucket_feed.find_all("item"):
        if count == 3:
            break
        count += 1
        print(count)
        print(item.find("guid").text)
        download_html(feed_url, item.find("guid").text, start_time)


def generate_tree(feed_url, start_time, start_time_original=None):
    print("Generating tree...\n")
    mandatory_articles = parser.get_article_list_from_bucket(feed_url, start_time)
    mandatory_article_titles = list(map(lambda a: a.split("/")[-1], mandatory_articles))

    if start_time_original is not None:
        mandatory_articles = parser.get_article_list_from_bucket(feed_url, start_time_original)
        mandatory_article_titles = list(map(lambda a: a.split("/")[-1], mandatory_articles))

    tree_nodes = tree_builder.build_tree_nodes_list_from_bucket(feed_url, start_time, mandatory_article_titles)
    tree_root = tree_builder.build_merkle_tree(tree_nodes)
    tree_to_s3_operations.write_tree_to_s3(feed_url, tree_root, start_time)
    return tree_root


def insert_old_articles(feed_url, start_time_original, start_time_new):
    print("Inserting old articles...\n")
    old_articles = parser.get_article_list_from_bucket(feed_url, start_time_original)
    new_articles = parser.get_article_list_from_bucket(feed_url, start_time_new)
    new_articles = list(map(lambda a: a.split("/")[-1], new_articles))
    for article in old_articles:
        if utils.get_item_title(article) not in new_articles:
            print(article.split("/")[-1])
            copy_article(
                feed_url,
                utils.get_item_url_hash(article),
                utils.get_item_title(article),
                start_time_original,
                start_time_new,
            )


def get_only_new_articles(feed_url, bucket_feed):
    online_feed = parser.read_feed_xml_from_online(feed_url)
    most_recent_date = parser.most_recent_article_date(bucket_feed)
    # most_recent_date = most_recent_date - timedelta(days=1)
    return parser.get_new_articles(online_feed, most_recent_date)


def append_to_feed(feed_url, start_time, bucket_feed, new_articles):
    feed = parser.append_new_articles_to_feed(bucket_feed, new_articles)
    file = StringIO(feed)

    new_xml_feed = utils.convert_to_bs(file.read())
    # new_xml_feed = parser.read_feed_xml_from_local()
    write_feed_to_s3(feed_url, start_time, new_xml_feed)
