# twitterwebsearch
The goal of this Python package is to automate the process for finding tweets 
older than several weeks.
These older tweets cannot be found using the Twitter
search API, but can be found through the web interface.

Instead of manually entering a query in Twitter's web interface, retrieving all
results and saving them, this package aims to automate these steps through 
Selenium and Firefox.



## Installation:
    pip install https://github.com/ShinNoNoir/twitterwebsearch/archive/master.zip

## Requirements:
One of the following needs to be installed and available on your system's `PATH`:
 * [PhantomJS](http://phantomjs.org/)
 * [Firefox](https://www.mozilla.org/en-US/firefox/)

## Small example:

    import json
    import twitterwebsearch.searcher
    import twitterwebsearch.parser
    
    QUERY = '@shinnonoir since:2010-01-20 until:2010-02-01'
    
    
    def main():
        results = twitterwebsearch.searcher.search_html(QUERY)
        tweets = twitterwebsearch.parser.parse_search_results(results)
        tweets = list(tweets) # convert generator into list
        print json.dumps(tweets, indent=2)
    
    if __name__ == '__main__':
        main()





