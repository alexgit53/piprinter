import praw
import random
import requests
import os
import io
from PIL import Image
import tempfile
import logging


MAX_IMAGE_BYTES = 10e6
MAX_DOWNLOAD_TRIES = 5


class DownloadError(Exception):
    def __init__(self, message):
        self.message = message


def is_image_post(submission):
    return submission.url.startswith(r"https://i.redd.it")


def get_image(url):
    logging.debug("Fetching image")
    with tempfile.SpooledTemporaryFile(max_size=MAX_IMAGE_BYTES) as buffer:
        r = requests.get(url)
        if r.status_code == 200:
            i = Image.open(io.BytesIO(r.content))
            return i
        else:
            raise DownloadError("Download failed")


def get_cat_post():
    logging.debug("Fetching cat post")
    reddit = praw.Reddit("bot1", user_agent="pc:com.ozymandias.redditdigest:v1 (by /u/CoachOzymandias)")
    image_posts = []
    for post in reddit.subreddit('cats').random_rising()
        if is_image_post(post) and not post.over_18:
            break
    tries = 0
    while tries < MAX_DOWNLOAD_TRIES:
        try:
            cat_pic = get_image(post.url)
            logging.info(f"Selected {post.permalink}")
            return {"pic": cat_pic, "title": post.title, "link":post.permalink}
        except DownloadError:
            logging.debug(f"Download failed on try {tries}/{MAX_DOWNLOAD_TRIES}.")
            tries += 1
        else:
            break
    else:
        logging.warn("Reached maximum download tries")
        return None
