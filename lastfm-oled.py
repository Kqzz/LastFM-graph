#!/usr/bin/env python

import datetime
import json
import math
import sys
import time
from datetime import datetime, timedelta

import bs4
import requests
from luma.core.render import canvas

from demo_opts import get_device

user = "kqzz"
API_KEY = "c92cefd9ab9957cec3ffccdb70ae16c6"

start = time.time()
month_ago = round(start - 60 * 60 * 24 * 31)


def get_recents_page(api_key, user, page, from_time):
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={api_key}&from={from_time}&page={page}&limit=1000&format=json"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        print("failed: ", r.status_code)
        return None


def get_last_30_days():

    data = get_recents_page(API_KEY, user, 1, month_ago)
    complete_scrobble_list = [*data["recenttracks"]["track"]]

    with open("data.json", "w") as f:
        f.write(json.dumps(data, indent=2))

    page_count = int(data["recenttracks"]["@attr"]["totalPages"])

    for i in range(2, page_count):
        data = get_recents_page(API_KEY, user, i, month_ago)
        complete_scrobble_list += data["recenttracks"]["track"]

    # complete_scrobble_list = json.loads(open("scrobbles.json", "r").read())
    scrobbles_by_day = {}

    for date in (datetime.now() - timedelta(n) for n in range(30)):
        scrobbles_by_day[date.strftime("%d/%m/%Y")] = 0

    print(scrobbles_by_day)

    for scrobble in reversed(complete_scrobble_list):
        if (
            scrobble.get("@attr") is not None
            and scrobble.get("@attr").get("nowplaying") == "true"
        ):
            continue

        scrobble_time = datetime.fromtimestamp(int(scrobble["date"]["uts"]))
        date = scrobble_time.strftime("%d/%m/%Y")

        if scrobbles_by_day.get(date) is None:
            continue

        scrobbles_by_day[date] += 1

    return scrobbles_by_day


def main():
    today_last_time = "Unknown"
    while True:
        with canvas(device) as draw:
            scrobbles = get_last_30_days()

            if len(scrobbles) == 0:
                time.sleep(120)
                continue

            days = list(scrobbles.keys())
            counts = list(scrobbles.values())

            margin_right = 30
            margin_bottom = 0
            width = device.width - margin_right
            height = device.height - margin_bottom

            maximum = max(counts)
            barwidth = math.floor(width / len(counts))
            print(barwidth)

            for i, (day, count) in enumerate(scrobbles.items()):
                pos = math.floor(barwidth * i)
                barheight = math.floor((count / maximum) * height)
                print(count / maximum)
                print(day, count, pos, barheight)
                draw.rectangle(
                    [
                        (pos, device.height - margin_bottom - barheight),
                        (pos + barwidth, device.height - margin_bottom),
                    ],
                    fill="white",
                )
            draw.text(
                (device.width - margin_right + 3, 0), f"{max(counts)}", fill="white"
            )
            draw.text((device.width - margin_right + 3, 8), f"max", fill="white")

            draw.text(
                (device.width - margin_right + 3, 20), f"{counts[-1]}", fill="white"
            )
            draw.text((device.width - margin_right + 3, 30), f"tdy", fill="white")

            draw.text(
                (device.width - margin_right + 3, 43),
                f"{round(sum(counts) / len(counts), 1)}",
                fill="white",
            )
            draw.text((device.width - margin_right + 3, 51), f"avg", fill="white")

        time.sleep(60)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
