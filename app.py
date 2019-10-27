"""
Principal Author: Eric Linden
Description :

Notes :
October 27, 2019
"""

from datetime import datetime

import feedparser
import pandas


def get_results_from_url(url: str, date_cutoff = None):
    CL_Feed = feedparser.parse(url)

    entries_list = []

    for entry in CL_Feed.entries:
        id = entry.id
        title = entry.title
        link = entry.link
        date_published = entry.published  # format: '2019-10-27T14:17:12-04:00'
        date_published = pandas.to_datetime(date_published)

        if date_cutoff is not None:
            date_cutoff = pandas.to_datetime(date_cutoff)

        if date_cutoff is None or date_published > date_cutoff:
            entries_list.append(
                dict(
                    id=id,
                    title=title,
                    link=link,
                    published=date_published))

    print(f'Date of most recent run: {datetime.now()}')
    return entries_list


if __name__ == '__main__':
    # TODO
    #  fix TypeError: Cannot compare tz-naive and tz-aware timestamps between
    #  dates from feed and dates generated locally
    #
    # TODO
    #  add a way to email myself the new listings
    #
    # TODO
    #  add a way to persist the datetime for each search for reuse on next run
    #
    # TODO
    #  automate everything

    item_of_interest = 'refrigerator'
    rss_url = f'http://providence.craigslist.org/search/sss?format=rss&query={item_of_interest}'
    response = get_results_from_url(url=rss_url, date_cutoff='2019-10-27 19:00:18.356804')

    for item in response:
        print(item['link'])
