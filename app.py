from chalice import Chalice
from chalicelib.rss_feed.feed_to_s3_operations import read_start_time
from chalicelib.myconstants import PODCAST_URL, URL, PODCAST_ID

from chalicelib.main_operations import (
    initial_population,
    run_trust_mode,
    run_validation_mode,
    run_podcast_download,
)


from chalicelib.utils import util

app = Chalice(app_name="lambda-project")


@app.route("/initial")
def pb_initial_population():
    start_time = util.generate_current_time()
    all_start_times = read_start_time(URL)
    if util.idempotent_check(start_time, all_start_times):
        initial_population(start_time, URL)
    return URL


@app.route("/trust_mode")
def pb_trust_mode():
    new_articles = run_trust_mode(URL)
    return f"New articles appended: {new_articles}"


@app.route("/validation_mode")
def pb_validation_mode():
    start_time = util.generate_current_time()
    try:
        different_articles = run_validation_mode(start_time, URL)
    except Exception:
        return "Forbidden validation mode before initial feed downloading"
    return f"Articles with differences: {different_articles}"


@app.route("/podcast/{d1}/{d2}")
def pb_podcast_download(d1, d2):
    start_time = util.generate_current_time()
    all_start_times = read_start_time(PODCAST_ID)
    if util.idempotent_check(start_time, all_start_times):
        run_podcast_download(start_time, PODCAST_URL, PODCAST_ID, d1, d2)
    return PODCAST_URL
