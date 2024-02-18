#!/bin/python3

import json
import sys
import time
from datetime import datetime

import requests
import termplotlib as tpl

user = sys.argv[-1]
API_KEY = "c92cefd9ab9957cec3ffccdb70ae16c6"

start = time.time()
month_ago = round(start - 60 * 60 * 24 * 30)

r = requests.get(
    f"https://www.last.fm/user/{user}/library?date_preset=LAST_30_DAYS",
    headers={
        "set-cookie": "sessionid=eyJfYXV0aF91c2VyX2hhc2giOiJkZWZhdWx0Iiwic2Vzc2lvbl9pZCI6Ijg0NTRkZWI4LWIwMjMtNDgyOS04YTA0LTFiMGZlMDZkMzYyZSJ9:1rbT3x:yKbXcBAhi99I54a3hIIaP0UsSlXV1tJt45rHThQV7ZQ"
    },
)


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

    scrobbles_by_day = {}

    for scrobble in reversed(complete_scrobble_list):
        if (
            scrobble.get("@attr") is not None
            and scrobble.get("@attr").get("nowplaying") == "true"
        ):
            continue

        scrobble_time = datetime.fromtimestamp(int(scrobble["date"]["uts"]))
        date = scrobble_time.strftime("%d/%m/%Y")
        if scrobbles_by_day.get(date) is None:
            scrobbles_by_day[date] = 0
            continue

        scrobbles_by_day[date] += 1

    return scrobbles_by_day


scrobbles_by_day = get_last_30_days()

fig = tpl.figure()
fig.hist(
    list(scrobbles_by_day.values()), list(scrobbles_by_day.keys()), force_ascii=False
)
print()
fig.show()
print(f"\n{user} - last.fm")
print(f"scrobbles today: {list(scrobbles_by_day.values())[-1]}")
