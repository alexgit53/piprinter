import praw
import re
import random
import requests

MAX_IMAGE_BYTES = 10e6
MAX_DOWNLOAD_TRIES = 5


class DownloadError(Exception):
    def __init__(self, message):
        self.message = message


def is_image_post(submission):
    return submission.url.startswith(r"https://i.redd.it")


def download_file(url):
    r = requests.get(url, stream=True)
    image_size = int(r.headers.get("Content-Length"))
    if image_size > MAX_IMAGE_BYTES:
        raise DownloadError(f"Image size ({image_size}) exceeds maximum size of {MAX_IMAGE_BYTES} bytes.")
    if r.status_code == 200:
        with open("tmp/image.jpg", 'wb') as f:
            for chunk in r:
                f.write(chunk)
    else:
        raise DownloadError(f"Image request failed: response code {r.status_code}.")


def get_cat_post():
    reddit = praw.Reddit("bot1", user_agent="pc:com.ozymandias.redditdigest:v1 (by /u/CoachOzymandias)")

    image_subs = []
    for submission in reddit.subreddit('cats').top("day", limit=50):
        if is_image_post(submission):
            image_subs.append(submission)
        if len(image_subs) >= 10:
            break

    tries = 0
    while tries < MAX_DOWNLOAD_TRIES:
        sub = random.choice(image_subs)
        try:
            download_file(sub.url)
        except DownloadError:
            tries += 1
        else:
            break
    else:
        raise ValueError("Could not download cat picture. Sorry. ^oᴥo^")



if __name__ == '__main__':
    get_cat_post()
