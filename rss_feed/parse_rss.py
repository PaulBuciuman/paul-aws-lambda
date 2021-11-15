import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import datetime as dt
import urllib.request as urllib2
from smart_open import open

URL = "https://www.buzzfeed.com/world.xml"
html_text = requests.get(URL).text
soup = BeautifulSoup(html_text, "html.parser")

BUCKET_PATH = "s3://aws-lambda-juniors"


def download_articles_between(d1, d2):
    for item in soup.find_all("item"):
        pub_date_str = item.find("pubdate").get_text()[0:16]
        pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y")

        if d1 < pub_date < d2:
            item_url = item.find("guid").get_text()
            print(item_url)
            page = urllib2.urlopen(item_url)

            page_content = page.read()
            with open(
                BUCKET_PATH + "/Paul/" + str(date.today()) + "/" + item_url.split("/")[-1] + ".html",
                "wb",
            ) as fid:
                fid.write(page_content)


d1 = dt.datetime(2021, 9, 10)
d2 = dt.datetime(2021, 10, 1)

download_articles_between(d1, d2)
