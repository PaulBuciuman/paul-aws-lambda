from constants import s3, BUCKET, BUCKET_PATH, paginator, client
import utils


def read_start_time(feed_url):

    prefix = "Paul/" + utils.hash_object(feed_url) + "/"
    print(prefix)

    result = client.list_objects(Bucket="aws-lambda-juniors", Prefix=prefix, Delimiter="/")
    for o in result.get("CommonPrefixes"):
        print("sub folder : ", o.get("Prefix").split("/")[-2])


# read_start_time("https://www.buzzfeed.com/world.xml")
