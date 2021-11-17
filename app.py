from chalice import Chalice
import boto3
from smart_open import open
from chalicelib.rss_feed.parse_rss import download_all_between
from chalicelib.rss_feed.merkle_tree import compare_merkle_trees, build_merkle_tree, articles_exist
import datetime as dt

app = Chalice(app_name="lambda-project")
BUCKET_PATH = "aws-lambda-juniors"


s3 = boto3.client("s3")


@app.route("/download")
def pb_download_articles_to_s3():
    d1 = dt.datetime(2021, 6, 29)
    d2 = dt.datetime(2021, 7, 1)
    download_all_between(d1, d2)


# don't hardcode the arguments, parametrize in terminal
# use SQS (chaining lambda functions) - runs automatically
# trigger a lambda functon everytime a url is found, that will upload that image to s3
# reuse lambda to save podcast files as well - make it generic s that it doesn't care what it downloads
# try to use youtube rss, youtube dl, take only the audio


@app.route("/compare")
def pb_compare_merkle_trees():
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
