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
        title = entry.title
        link = entry.link
        date_published = entry.published  # format: '2019-10-27T14:17:12-04:00'
        date_published = pandas.to_datetime(date_published)

        if date_cutoff is not None:
            date_cutoff = pandas.to_datetime(date_cutoff, utc=True)

        if date_cutoff is None or date_published > date_cutoff:
            entries_list.append(
                dict(
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
              "to": ["coralvanda@gmail.com"],
              "subject": "Latest search results",
              "html": email_body})


def send_error_email(text):
    requests.post(
        "https://api.mailgun.net/v3/mail.coralvanda.com/messages",
        auth=("api", os.environ.get(MAILGUN_API_KEY)),
        data={"from": "CraigsList searchbot <admin@mail.coralvanda.com>",
              "to": ["coralvanda@gmail.com"],
              "subject": "Error with CraigsList bot",
              "text": f"The CraigsList bot encountered an error: {text}"})


def build_html_email_body(fridges, washers, dryers, combos) -> str:
    fridge_content = build_links_from_list(title='Fridges', content_list=fridges)
    washer_content = build_links_from_list(title='Washers', content_list=washers)
    dryer_content = build_links_from_list(title='Dryers', content_list=dryers)
    washer_dryer_combo_content = build_links_from_list(
        title='Washer/dryer combos',
        content_list=combos)

    template = """
    <body>
        {fridge_content}
        {washer_content}
        {dryer_content}
        {washer_dryer_combo_content}
    </body>
    """.format(
        fridge_content=fridge_content,
        washer_content=washer_content,
        dryer_content=dryer_content,
        washer_dryer_combo_content=washer_dryer_combo_content)

    return template


def build_links_from_list(title: str, content_list: List[dict]) -> str:
    base_string = f'<br><h4>{title}</h4><br>'

    for item in content_list:
        base_string += '<a href="{link}"><p>{title}</p></a><br>'.format(
            link=item['link'],
            title=item['title'])

    return base_string


if __name__ == '__main__':
    twelve_hour_delta = timedelta(hours=12)
    twelve_hours_ago = datetime.now() - twelve_hour_delta

    fridge_list = get_results_from_url(
        url=build_url(item_of_interest='refrigerator'),
        date_cutoff=twelve_hours_ago)

    washer_list = get_results_from_url(
        url=build_url(item_of_interest='washer'),
        date_cutoff=twelve_hours_ago)

    dryer_list = get_results_from_url(
        url=build_url(item_of_interest='dryer'),
        date_cutoff=twelve_hours_ago)

    washer_dryer_combo_list = get_results_from_url(
        url=build_url(item_of_interest='washer dryer'),
        date_cutoff=twelve_hours_ago)

    email_body = build_html_email_body(
        fridges=fridge_list,
        washers=washer_list,
        dryers=dryer_list,
        combos=washer_dryer_combo_list)

    response = send_email(email_body=email_body)

    if response.status_code != 200:
        send_error_email(text=response.content)
