import boto3

URL = "https://www.buzzfeed.com/world.xml"

s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors"
client = boto3.client("s3")
paginator = client.get_paginator("list_objects_v2")
image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
LOCAL_PATH = "chalicelib/new_feed.xml"
lambda_client = boto3.client("lambda")
