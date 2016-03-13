"""
Module for using the web interface of Twitter's search.
"""
import json
import time
import urllib
import requests
from twitterwebsearch.parser import parse_search_results


TWITTER_PROFILE_URL = 'https://twitter.com/{term}'
TWITTER_PROFILE_MORE_URL = 'https://twitter.com/i/profiles/show/{term}/timeline?include_available_features=1&include_entities=1&max_position={max_position}'
TWITTER_SEARCH_URL = 'https://twitter.com/search?q={term}&src=typd&vertical=default&f=tweets'
TWITTER_SEARCH_MORE_URL = 'https://twitter.com/i/search/timeline?q={term}&src=typd&vertical=default&f=tweets&include_available_features=1&include_entities=1&max_position={max_position}'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0'

DEFAULT_SLEEP = 0.5

def find_value(html, key):
    pos_begin = html.find(key) + len(key) + 2
    pos_end = html.find('"', pos_begin)
    return html[pos_begin: pos_end]

def download_tweets(search=None, profile=None, sleep=DEFAULT_SLEEP):
    assert search or profile

    term = (search or profile)
    url = TWITTER_SEARCH_URL if search else TWITTER_PROFILE_URL
    url_more = TWITTER_SEARCH_MORE_URL if search else TWITTER_PROFILE_MORE_URL

    response = requests.get(url.format(term=urllib.quote_plus(term)), headers={'User-agent': USER_AGENT}).text
    max_position = find_value(response, 'data-max-position')
    min_position = find_value(response, 'data-min-position')

    for tweet in parse_search_results(response.encode('utf8')):
        yield tweet

    has_more_items = True
    while has_more_items:
        response = requests.get(url_more.format(term=urllib.quote_plus(term), max_position=min_position), headers={'User-agent': USER_AGENT}).text
        try:
            response_dict = json.loads(response)
        except:
            import datetime
            with open('__debug.response_%s.txt' % datetime.datetime.now().strftime('%Y-%m-%d.%H%M'), 'wb') as fh:
                print >>fh, repr(response)
            raise
        
        min_position = response_dict['min_position']
        has_more_items = response_dict['has_more_items'] if profile else False

        for tweet in parse_search_results(response_dict['items_html'].encode('utf8')):
            yield tweet

            if search:
                has_more_items = True

        time.sleep(sleep)



def search(query):
    for tweet in download_tweets(search=query):
        yield tweet

