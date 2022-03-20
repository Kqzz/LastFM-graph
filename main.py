#!/bin/python3

import bs4
import requests
import termplotlib as tpl
import sys

user = sys.argv[1]

r = requests.get(
    f"https://www.last.fm/user/{user}/library?date_preset=LAST_30_DAYS"
)

soup = bs4.BeautifulSoup(r.text, 'html5lib')

times = []
counts = []

for (i, x) in enumerate(soup.select(".table > tbody > tr")):
    timeframe = x.select_one("a").text.strip()
    count = int(x.select_one(".js-scrobbles").text.strip())

    times.append(i)
    counts.append(count)

fig = tpl.figure()
fig.hist(counts, times, force_ascii=False)
print()
fig.show()
print(f"\n{user} - last.fm")
print(f"peak last 30 days: {max(*counts)}")
print(f"scrobbles today: {counts[-1]}")
