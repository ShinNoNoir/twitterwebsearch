"""
Module for using the web interface of Twitter's search.
"""
import json
import time
import requests
from twitterwebsearch.parser import parse_search_results


TWITTER_PROFILE_URL = 'https://twitter.com/{term}'
TWITTER_PROFILE_MORE_URL = 'https://twitter.com/i/profiles/show/{term}/timeline?include_available_features=1&include_entities=1&max_position={max_position}'
TWITTER_SEARCH_URL = 'https://twitter.com/search?q={term}&src=typd'
TWITTER_SEARCH_MORE_URL = 'https://twitter.com/i/search/timeline?q={term}&src=typd&vertical=default&include_available_features=1&include_entities=1&max_position={max_position}'

def find_value(html, key):
    pos_begin = html.find(key) + len(key) + 2
    pos_end = html.find('"', pos_begin)
    return html[pos_begin: pos_end]

def download_tweets(search=None, profile=None, sleep=1):
    assert search or profile

    term = (search or profile)
    url = TWITTER_SEARCH_URL if search else TWITTER_PROFILE_URL
    url_more = TWITTER_SEARCH_MORE_URL if search else TWITTER_PROFILE_MORE_URL

    response = requests.get(url.format(term=term)).text
    max_position = find_value(response, 'data-max-position')
    min_position = find_value(response, 'data-min-position')

    for tweet in parse_search_results(response.encode('utf8')):
        yield tweet

    has_more_items = True
    while has_more_items:
        response = requests.get(url_more.format(term=term, max_position=min_position)).text
        response_dict = json.loads(response)
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

