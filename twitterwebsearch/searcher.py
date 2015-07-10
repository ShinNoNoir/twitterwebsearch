"""
Module for using the web interface of Twitter's search.
"""
import sys
import time
import datetime
import twitterwebsearch.parser

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


TWITTER_SEARCH_URL = 'https://twitter.com/search-home'
SEARCH_FIELD = 'search-home-input'
WAIT_FOR_CLASS = 'AdaptiveSearchTitle-title'
SCROLLER_SCRIPT = '''
    footer = document.getElementsByClassName('stream-footer')[0];
    scroller = setInterval(function() { footer.scrollIntoView(); }, 250);
'''

LOAD_MORE_TWEETS_FUNCTION_NAME = 'load_more_tweets'
LOAD_MORE_TWEETS_FUNCTION = LOAD_MORE_TWEETS_FUNCTION_NAME + '();'
LOAD_MORE_TWEETS_SCRIPT = '''
footer = document.getElementsByClassName('stream-footer')[0];

%s = function () {
    document.body.classList.remove('more-tweets-loaded');
    var tweets = document.querySelectorAll('.tweet[data-tweet-id]');
    
    function removeTweets() {
        var more = document.querySelector(".timeline-end.has-more-items") !== null;
        var not_loaded = document.querySelectorAll('.tweet[data-tweet-id]').length === tweets.length;
        if (more && not_loaded) {
            window.setTimeout(removeTweets, 250);
        }
        else {
            document.body.scrollIntoView();
            for (var i=0; i < tweets.length; i++) {
                var tweetElem = tweets[i];
                var liElem = tweetElem.parentNode;
                liElem.parentNode.removeChild(liElem);
            }
            pruneEmptyListItems();
            document.body.classList.add('more-tweets-loaded');
            tweets = null;
        }
    };
    removeTweets();
    footer.scrollIntoView();
}

isEmptyLI = function(node) {
    return node.firstElementChild === null || node.firstElementChild.firstElementChild === null;
}
pruneEmptyListItems = function() {
    var lis = document.querySelectorAll('li.stream-item');
    
    for (var i=0; i < lis.length; i++)
        if (isEmptyLI(lis[i]))
            lis[i].parentNode.removeChild(lis[i]);
    
    lis = null;
}
''' % LOAD_MORE_TWEETS_FUNCTION_NAME
MORE_TWEETS_LOADED_CLASS = 'more-tweets-loaded'
MORE_TWEETS_LOADED_TIMEOUT = 1 # seconds
MORE_TWEETS_LOADED_TIMEOUT_MAX_ATTEMPTS = 20
SCROLL_BACK_AND_FORTH_SCRIPT = '''
    (function () {
        var scrollto = [document.body, footer];
        
        function scrollBackAndForth() {
            var elem = scrollto.pop(0);
            elem.scrollIntoView();
            if (scrollto.length > 0)
                window.setTimeout(scrollBackAndForth, 250);
        }
        scrollBackAndForth();
    })();
'''

LIVE_TWEETS_SELECTOR = 'a[href*="f=tweets"]'

DRIVER_PRIORITY = [webdriver.PhantomJS, webdriver.Firefox]

QUERY_TIMEOUT = 20 # seconds
POLL_TIME = 1 # seconds

def create_driver():
    if not hasattr(create_driver, 'driver'):
        for driver in DRIVER_PRIORITY:
            try:
                res = driver()
            except:
                continue
            
            create_driver.driver = driver
            return res
        else:
            raise RuntimeError('None of the following Selenium drivers are available: %r' % DRIVER_PRIORITY)
    else:
        return create_driver.driver()

def debug_screenshot(driver, dontraise=True):
    try:
        path = '__twitterwebsearch.%s.png' % datetime.datetime.now().strftime('%Y-%m-%d.%H%M')
        driver.save_screenshot(path)
        return path
    except:
        if dontraise:
            exc_type, exc_value, _ = sys.exc_info()
            print >>sys.stderr, 'Failed to create screenshot:', exc_type, '--', exc_value 
        else:
            raise
        
    

def wait_until_url(driver, predicate, sleep=0.25):
    while not predicate(driver.current_url):
        time.sleep(sleep)
    

def _fill_text_field_and_submit(driver, elem, value):
    elem.clear()
    time.sleep(0.2)
    elem.send_keys(value)
    time.sleep(0.2)
    elem.submit()
    

def start_search(driver, query):
    driver.get(TWITTER_SEARCH_URL)
    
    elem = driver.find_element_by_id(SEARCH_FIELD)
    _fill_text_field_and_submit(driver, elem, query)
    
    try:
        elem = WebDriverWait(driver, QUERY_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, WAIT_FOR_CLASS))
        )
        try:
            driver.find_element_by_css_selector(LIVE_TWEETS_SELECTOR).click()
        except NoSuchElementException:
            debug_screenshot(driver)
            raise
        
        wait_until_url(driver, predicate=lambda url: '&f=tweets' in url)
    except:
        debug_screenshot(driver)
        raise
        

def search(query):
    driver = create_driver()
    try:
        start_search(driver, query)
        driver.execute_script(LOAD_MORE_TWEETS_SCRIPT)
        
        more_tweets = True
        while more_tweets:
            source = driver.page_source
            driver.execute_script(LOAD_MORE_TWEETS_FUNCTION)
            
            more_tweets = False
            tweets = twitterwebsearch.parser.parse_search_results(source)
            for tweet in tweets:
                more_tweets = True
                yield tweet
            
            attempts = 0
            while True:
                attempts += 1
                try:
                    WebDriverWait(driver, MORE_TWEETS_LOADED_TIMEOUT).until(
                        EC.presence_of_element_located((By.CLASS_NAME, MORE_TWEETS_LOADED_CLASS))
                    )
                    break
                except:
                    if attempts <= MORE_TWEETS_LOADED_TIMEOUT_MAX_ATTEMPTS:
                        driver.execute_script(SCROLL_BACK_AND_FORTH_SCRIPT)
                    else:
                        raise
                
        
    except:
        debug_screenshot(driver)
        raise
    finally:
        driver.quit()

def search_html(query):
    driver = create_driver()
    
    res = ''
    try:
        start_search(driver, query)
        driver.execute_script(SCROLLER_SCRIPT)
        
        old_size = size = 0
        delta = not 0
        while delta != 0:
            time.sleep(POLL_TIME)
            
            old_size = size
            size = len(driver.page_source)
            delta = size - old_size
            
        res = driver.page_source
        
    except:
        debug_screenshot(driver)
        raise
    finally:
        driver.quit()
        
    return res

