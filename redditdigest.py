import praw
import random
import requests
import os
import io
from PIL import Image
import tempfile

MAX_IMAGE_BYTES = 10e6
MAX_DOWNLOAD_TRIES = 5


class DownloadError(Exception):
    def __init__(self, message):
        self.message = message


def is_image_post(submission):
    return submission.url.startswith(r"https://i.redd.it")


def get_image(url):
    with tempfile.SpooledTemporaryFile(max_size=MAX_IMAGE_BYTES) as buffer:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            image_size = int(r.headers.get("Content-Length"))
            if image_size > MAX_IMAGE_BYTES:
                raise DownloadError(f"Image size ({image_size}) exceeds maximum size of {MAX_IMAGE_BYTES} bytes.")
            for chunk in r.iter_content():
                buffer.write(chunk)
            buffer.seek(0)
            i = Image.open(io.BytesIO(buffer.read()))
            return i


def get_cat_post():
    reddit = praw.Reddit("bot1", user_agent="pc:com.ozymandias.redditdigest:v1 (by /u/CoachOzymandias)")
    image_posts = []
    for post in reddit.subreddit('cats').top("day", limit=50):
        if is_image_post(post) and not post.over_18:
            image_posts.append(post)
        if len(image_posts) >= 10:
            break

    tries = 0
    while tries < MAX_DOWNLOAD_TRIES:
        choice = random.choice(image_posts)
        try:
            cat_pic = get_image(choice.url)
        except DownloadError:
            tries += 1
        else:
            break
    else:
        return None

    return {"pic": cat_pic, "title": choice.title, "link":choice.permalink}
