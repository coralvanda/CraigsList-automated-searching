"""
Principal Author: Eric Linden
Description :

Notes :
October 27, 2019
"""

import os

from datetime import datetime, timedelta
from typing import List

import feedparser
import pandas
import requests


MAILGUN_API_KEY = 'mailgun_api_key'


def get_results_from_url(url: str, date_cutoff = None) -> List[dict]:
    CL_Feed = feedparser.parse(url)

    entries_list = []

    for entry in CL_Feed.entries:
        id = entry.id
        title = entry.title
        link = entry.link
        date_published = entry.published  # format: '2019-10-27T14:17:12-04:00'
        date_published = pandas.to_datetime(date_published)

        if date_cutoff is not None:
            date_cutoff = pandas.to_datetime(date_cutoff, utc=True)

        if date_cutoff is None or date_published > date_cutoff:
            entries_list.append(
                dict(
                    id=id,
                    title=title,
                    link=link,
                    published=date_published))

    return entries_list


def build_url(item_of_interest: str) -> str:
    return f'http://providence.craigslist.org/search/sss?format=rss&query={item_of_interest}'


def send_email(email_body: str):
    return requests.post(
        "https://api.mailgun.net/v3/mail.coralvanda.com/messages",
        auth=("api", os.environ.get(MAILGUN_API_KEY)),
        data={"from": "CraigsList searchbot <admin@mail.coralvanda.com>",
              "to": ["angelinadowell@gmail.com", "coralvanda@gmail.com"],
              "subject": "Latest search results",
              "text": email_body})


if __name__ == '__main__':
    twelve_hour_delta = timedelta(hours=12)
    twelve_hours_ago = datetime.now() - twelve_hour_delta

    response_list = get_results_from_url(
        url=build_url(item_of_interest='refrigerator'),
        date_cutoff=twelve_hours_ago)

    response_list.extend(get_results_from_url(
        url=build_url(item_of_interest='washer'),
        date_cutoff=twelve_hours_ago))

    response_list.extend(get_results_from_url(
        url=build_url(item_of_interest='dryer'),
        date_cutoff=twelve_hours_ago))

    response_list.extend(get_results_from_url(
        url=build_url(item_of_interest='washer dryer'),
        date_cutoff=twelve_hours_ago))

    for entry in response_list:
        print(entry['title'])
        print(entry['published'])
        print()
