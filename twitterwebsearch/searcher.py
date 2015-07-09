"""
Module for using the web interface of Twitter's search.
"""
import sys
import time
import datetime
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
    

def start_search(driver, query):
    driver.get(TWITTER_SEARCH_URL)
    
    elem = driver.find_element_by_id(SEARCH_FIELD)
    elem.send_keys(query)
    elem.send_keys(Keys.ENTER)
    
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
    return search_html(query)

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

