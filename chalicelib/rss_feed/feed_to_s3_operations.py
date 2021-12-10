from datetime import datetime
from datetime import date
import datetime as dt
import urllib.request as urllib2
from smart_open import open
import shutil
from chalicelib.utils import util
from chalicelib.rss_feed import parser
from chalicelib.myconstants import s3, BUCKET, BUCKET_NAME, client
from io import StringIO


def read_start_time(feed_url):
    start_times = []
    prefix = "Paul/" + util.hash_object(feed_url) + "/"
    result = client.list_objects(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter="/")
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
        util.bucket_path(feed_url, start_time) + "/rss_feed.xml",
        "w",
    ) as fid:
        try:
            fid.write(str(feed_xml))
        except Exception as e:
            print(f"Exception: {e}")


def copy_article(feed_url, article_hash, article_title, start_time_original, start_time_new):
    copy_source = {
        "Bucket": BUCKET,
        "Key": "Paul/"
        + util.hash_object(feed_url)
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
        "Paul/" + util.hash_object(feed_url) + "/" + start_time_new + "/items/" + article_hash + "/" + article_title,
    )


# def get_bucket_path(path, article, item):
#     bucket_path = path + "/Paul/" + str(date.today() + dt.timedelta(days=0)) + "/" + article + "/" + item
#     return bucket_path


# def download_assets(article_url, path):
#     article = parser.convert_page_to_bs(article_url)
#     images = parser.parse_images(article)
#     count = 0
#     for image_url, image_file in images.items():
#         count += 1
#         with open(
#             get_bucket_path(path, util.get_item_title(article_url), util.et_item_title(image_url)),
#             "wb",
#         ) as fid:
#             shutil.copyfileobj(image_file.raw, fid)
#     return count


def download_html(feed_url, article_url, start_time):
    page = urllib2.urlopen(article_url)
    page_content = page.read()
    with open(
        util.bucket_path(feed_url, start_time)
        + "/items/"
        + util.hash_object(article_url)
        + "/"
        + util.get_item_title(article_url)
        + ".html",
        "w",
    ) as fid:
        fid.write(str(page_content))


def download_all_htmls(feed_url, start_time, most_recent_date=None):
    bucket_feed = parser.read_feed_xml_from_bucket(feed_url, start_time)
    # count = 0
    for item in bucket_feed.find_all("item"):
        # if count == 3:
        #     break
        # count += 1
        download_html(feed_url, item.find("guid").text, start_time)


def insert_old_articles(feed_url, start_time_original, start_time_new):
    print("Inserting old articles...\n")
    old_articles = parser.get_article_list_from_bucket(feed_url, start_time_original)
    new_articles = parser.get_article_list_from_bucket(feed_url, start_time_new)
    new_articles = list(map(lambda a: a.split("/")[-1], new_articles))
    for article in old_articles:
        if util.get_item_title(article) not in new_articles:
            copy_article(
                feed_url,
                util.get_item_url_hash(article),
                util.get_item_title(article),
                start_time_original,
                start_time_new,
            )


def get_only_new_articles(feed_url, bucket_feed):
    online_feed = parser.read_feed_xml_from_online(feed_url)
    most_recent_date = parser.most_recent_article_date(bucket_feed)
    return parser.get_new_articles(online_feed, most_recent_date)


def append_to_feed(feed_url, start_time, bucket_feed, new_articles):
    feed = parser.append_new_articles_to_feed(bucket_feed, new_articles)
    file = StringIO(feed)
    new_xml_feed = util.convert_to_bs(file.read())
    write_feed_to_s3(feed_url, start_time, new_xml_feed)
