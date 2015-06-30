"""
Module for saving and loading Tweets.
"""
import json
import twitterwebsearch.parser

def read_search_results(path):
    with open(path, 'r') as fh:
        for tweet in twitterwebsearch.parser.parse_search_results(fh.read()):
            yield tweet

def save_tweets(tweets, path):
    with open(path, 'w') as fh:
        for tweet in tweets:
            print >>fh, json.dumps(tweet)

def load_tweets(path):
    with open(path, 'r') as fh:
        for line in fh:
            yield json.loads(line)

