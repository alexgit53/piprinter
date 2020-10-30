from thermalprinter import ThermalPrinter
from redditdigest import get_cat_post
from datetime import datetime
import redis
import time
import logging


PRINTER_PORT = "/dev/serial0"


def get_day_section(hour):
    if 4 < hour <= 11:
        day_section = "morning"
    elif 11 < hour <= 6:
        day_section = "afternoon"
    else:
        day_section = "evening"
    return day_section


def scale_image(image):
    size = (384, 512)
    image.thumbnail(size)
    return image


def build_post():
    post = get_cat_post()
    now_dt = datetime.now()
    day_section = get_day_section(now_dt.hour)
    task = {
        "metadata": "bla",
        "print_job": [
            {"type": "text", "content": "Hello! Here's a cat picture"},
            {"type": "image", "image": post["pic"]},
            {"type": "text", "content": post["title"]},
            {"type": "text", "content": f"Have a good {day_section}!"},
        ],
    }
    return task


def print_post(post, printer):
    for el in post["print_job"]:
        if el["type"] == "text":
            printer.out(el["content"])
        elif el["type"] == "image":
            printer.image(scale_image(el["image"]))
    printer.feed(3)


def main():
    r = redis.Redis(host="localhost", port=6379, db=0)
    logging.info("Connected to Redis")
    printer = ThermalPrinter(port=PRINTER_PORT)
    logging.info("Printer initialised")
    while True:
        if r.get("print") == "true":
            logging.info("Printing...")
            r.set("print", "false")
            post = build_post()
            print_post(post, printer)
            logging.info("Print completed")
            time.sleep(5)
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()
