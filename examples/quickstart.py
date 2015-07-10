'''
Quickstart example.
'''

import json
import twitterwebsearch
import twitterwebsearch.io

QUERY = '@shinnonoir since:2010-01-20 until:2010-02-01'

def main():
    tweets = twitterwebsearch.search(QUERY)
    tweets = list(tweets) # convert generator into list
    
    print json.dumps(tweets, indent=2)
    
    twitterwebsearch.io.save_tweets(tweets, 'example.ljson')
    loaded_tweets = twitterwebsearch.io.load_tweets('example.ljson')
    
    assert list(loaded_tweets) == tweets

if __name__ == '__main__':
    main()
