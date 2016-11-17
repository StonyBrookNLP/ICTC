import sys
import tweepy
import time
import re
import operator
from datetime import datetime
from twitter import *

consumer_key = None
consumer_secret = None

access_token = None
access_token_secret = None



t = Twitter(auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret), retry=True)


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def compute_tag_frequency(tweets):
    tag_count = {}
    for tweet in tweets:
        tags = set(part[1:].rstrip().lower() for part in tweet.split() if part.startswith('#'))
        for tag in tags:
            count = tag_count.get(tag, 0)
            tag_count[tag] = count + 1

    sorted_tags = sorted(tag_count.items(), key=operator.itemgetter(1), reverse=True)

    return tag_count, sorted_tags


def parse_tweets(fn):

    f = open(fn, 'r')
    tweets_text = f.read()
    f.close()

    tweets = tweets_text.split('\n!@#$%\n')
    if tweets[-1].strip() == '':
        tweets.pop(-1)

    return tweets


def select_tweets_with_tags(fn, tags):
    


def extract_tweets(query_text, max_tweets, tweets_type = 'mixed', fn = None):

    if fn:
        f_out = open(fn, 'w')
    else:
        tweets = []

    cur = tweepy.Cursor(api.search, q = query_text, result_type = tweets_type, count = 100).items()
    err = None
    total_tweets = 0
    while True:
        try:
            for tweet in cur:

                txt = tweet.text.encode('utf-8')
                if fn:
                    f_out.write(txt + '\n!@#$%\n')
                else:
                    tweets.append(tweet)
                total_tweets += 1
                if total_tweets >= max_tweets:
                    break

            # break if we reach end of cursor
            break
        except tweepy.TweepError as e:
            err = e
            codes = re.findall(r'twitter error response: status code =(.*)', e.message, re.IGNORECASE)
            if len(codes) and codes[0].strip() == '429':
                print 'Rate limited at {0}. Total tweets so far: {1}. Query text: {2}'.format(str(datetime.now()), total_tweets, query_text)
                time.sleep(15 * 60)
            else:
                raise e

    print 'Extracted {0} tweets for {1}'.format(total_tweets, query_text)

    if fn:
        f_out.close()
    else:
        return tweets

queries = ['obamacare', 'gun control', 'gay marriage', 'marriageequality', 'abortion', 'pro life', 'pro choice']
max_tweets = 30000
for query in queries:
    #extract_tweets(query, max_tweets, fn = query + '.txt')
