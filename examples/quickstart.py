'''
Quickstart example.
'''

import json
import twitterwebsearch
import twitterwebsearch.parser
import twitterwebsearch.io

QUERY = '@shinnonoir since:2010-01-20 until:2010-02-01'


def main():
    results = twitterwebsearch.search(QUERY)
    tweets = twitterwebsearch.parser.parse_search_results(results)
    tweets = list(tweets) # convert generator into list
    
    print json.dumps(tweets, indent=2)
    
    twitterwebsearch.io.save_tweets(tweets, 'example.ljson')
    loaded_tweets = twitterwebsearch.io.load_tweets('example.ljson')
    
    assert list(loaded_tweets) == tweets

if __name__ == '__main__':
    main()
