import boto3

URL = "https://www.buzzfeed.com/world.xml"
PODCAST_ID = "UCsXVk37bltHxD1rDPwtNM8Q"
PODCAST_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCsXVk37bltHxD1rDPwtNM8Q"
s3 = boto3.resource("s3")
BUCKET = s3.Bucket("aws-lambda-juniors")
BUCKET_PATH = "s3://aws-lambda-juniors"
BUCKET_NAME = "aws-lambda-juniors"
client = boto3.client("s3")
paginator = client.get_paginator("list_objects_v2")
image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
LOCAL_PATH = "chalicelib/new_feed.xml"
lambda_client = boto3.client("lambda")
