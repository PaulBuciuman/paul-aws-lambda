from chalice import Chalice
import boto3
from smart_open import open
from chalicelib.rss_feed.parse_rss import (
    get_articles_from_rss,
    download_html,
    get_bucket_path,
    get_item_title,
    download_assets,
)
from chalicelib.rss_feed.merkle_tree import compare_merkle_trees, build_merkle_tree, articles_exist
import datetime as dt
import json


# def lambda_handler(event, context):

#     d1 = dt.datetime(2021, 6, 29)
#     d2 = dt.datetime(2021, 7, 1)

#     input_for_child = {"date1": d1, "date2": d2, "url": URL}

#     response = lambda_client.invoke(
#         FunctionName="arn:aws:lambda:us-east-2:816286866474:function:lambda_project-dev",
#         InvocationType="RequestResponse",
#         Payload=json.dumps(input_for_child),
#     )
