from smart_open import open
import boto3
from app import app

BUCKET_PATH = "aws-lambda-juniors"

s3 = boto3.resource("s3")


@app.lambda_function()
def write_to_s3(event, context):
    s3.Object(BUCKET_PATH, "Paul/helloworld.txt").put(Body=open("chalicelib/helloworld.txt", "rb"))
    return "world"
