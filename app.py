from chalice import Chalice
import boto3
from smart_open import open
from rss_feed.parse_rss import download_articles_between
from rss_feed.merkle_tree import compare_merkle_trees, build_merkle_tree, articles_exist
import datetime as dt

app = Chalice(app_name="lambda-project")
BUCKET_PATH = "aws-lambda-juniors"


s3 = boto3.client("s3")


@app.route("/")
def index():
    return {"hello": "world"}


@app.lambda_function()
def pb_write_to_s3(event, context):
    return s3.put_object(Bucket=BUCKET_PATH, Key="Paul/hello.txt", Body=open("chalicelib/helloworld.txt", "rb"))


@app.lambda_function()
def pb_download_articles_to_s3():
    d1 = dt.datetime(2021, 9, 10)
    d2 = dt.datetime(2021, 10, 1)
    download_articles_between(d1, d2)


@app.lambda_function()
def pb_compare_merkle_trees():
    d1 = dt.datetime(2021, 11, 11)
    d2 = dt.datetime(2021, 11, 12)

    if articles_exist(d1) and articles_exist(d2):
        root1 = build_merkle_tree(str(d1.date()))
        root2 = build_merkle_tree(str(d2.date()))
        diff_articles = compare_merkle_trees(root1, root2)
        print("Articles with differences: ")
        print(diff_articles)
    else:
        print("Comparison not possible.One of the dates doesn't exist!")
