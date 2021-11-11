from chalice import Chalice
import boto3
from smart_open import open

app = Chalice(app_name="lambda-project")
BUCKET_PATH = "aws-lambda-juniors"


s3 = boto3.client("s3")


@app.route("/")
def index():
    # pb_write_to_s3()
    return {"hello": "world"}


@app.lambda_function()
def pb_write_to_s3(event, context):
    # return s3.Object(BUCKET_PATH, "Paul/helloworld.txt").put(Body=open("chalicelib/helloworld.txt", "rb"))
    return s3.put_object(Bucket=BUCKET_PATH, Key="Paul/helloworld.txt", Body=open("chalicelib/helloworld.txt", "rb"))
