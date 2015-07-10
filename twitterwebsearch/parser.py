"""
Parser module for parsing Twitter search results obtained through the web 
interface.
"""
import bs4

def has_class(class_name):
    return lambda class_: class_ and class_name in class_.split()

only_tweet_tags = bs4.SoupStrainer('div', class_=has_class('tweet'), **{'data-tweet-id': True})

def parse_tweet_tag(tag):
    tweet_id = tag['data-tweet-id']
    permalink = tag['data-permalink-path']
    screen_name = tag['data-screen-name']
    name = tag['data-name']
    user_id = tag['data-user-id']
    
    content_div = tag.find('div', class_=has_class('content'))
    tweet_body_tag = content_div.find('p', class_=has_class('tweet-text'))
    
    lang = tweet_body_tag['lang']
    tweet_text = tweet_body_tag.text
    
    urls = [
        a['data-expanded-url']
        for a in tweet_body_tag.find_all('a', class_=has_class('twitter-timeline-link'))
        if 'data-expanded-url' in a.attrs
    ]
    
    mentions = [
        a.text
        for a in tweet_body_tag.find_all('a', class_=has_class('twitter-atreply'))
    ]
    
    timestamp = int(content_div.find(**{'data-time-ms':True})['data-time-ms'])/1000.
    
    footer_div = content_div.find('div', class_=has_class('stream-item-footer'))
    def get_stats(stats_type):
        span = footer_div.find('span', class_=has_class("ProfileTweet-action--%s" % stats_type))
        spanspan = span.find('span', class_=has_class("ProfileTweet-actionCount"))
        return int(spanspan['data-tweet-stat-count'])
    
    footer_div.find('span', class_="ProfileTweet-action--retweet")
    retweet_count = get_stats('retweet')
    favorite_count = get_stats('favorite')
    
    tweet = dict(tweet_id=tweet_id,
                 permalink=permalink,
                 screen_name=screen_name,
                 name=name,
                 user_id=user_id,
                 lang=lang,
                 tweet_text=tweet_text,
                 urls=urls,
                 mentions=mentions,
                 retweet_count=retweet_count,
                 favorite_count=favorite_count,
                 timestamp=timestamp)
    
    return tweet
    
def parse_search_results(html):
    soup_tweets = bs4.BeautifulSoup(html, 'html.parser', parse_only=only_tweet_tags)
    for tag in soup_tweets:
        tweet = parse_tweet_tag(tag)
        yield tweet

