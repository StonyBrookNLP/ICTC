import sys
import got
import json
from datetime import datetime


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def extract_tweets(query_text, since, until, max_tweets, fn = None):

    if fn:
        f_out = open(fn, 'w')
    else:
        tweets = []

    tweetCriteria = got.manager.TweetCriteria()
    tweetCriteria.setQuerySearch(query_text)
    tweetCriteria.setSince("2012-01-01")
    tweetCriteria.setUntil("2014-01-01")
    tweetCriteria.setMaxTweets(max_tweets)
    tweet_objs = got.manager.TweetManager.getTweets(tweetCriteria)

    latest_time = datetime.min

    tweet_dicts = []

    for tweet in tweet_objs:

        tweet_dicts.append(tweet.__dict__)

        txt = tweet.text.encode('utf-8')
        if fn:
            f_out.write(txt + '\n!@#$%\n')

        if tweet.date > latest_time:
            latest_time = tweet.date

    print 'Extracted {0} tweets for {1}'.format(len(tweet_objs), query_text)
    print 'Latest tweet time = {0}'.format(latest_time)

    if fn:
        f_out.close()
        with open(query_text + '.json', 'wb') as f_json:
            json_txt = json.dumps(tweet_dicts, default=date_handler)
            f_json.write(json_txt)
    else:
        return tweets

#queries = ['obamacare', 'gun control', 'gay marriage', 'marriageequality', 'abortion', 'pro life', 'pro choice']
#queries = ['PrayToEndAbortion', 'prolife', 'defundpp', 'stand4life', 'prochoice', 'StandWithPP', 'reprorights', 'protectchoice', 'ChooseLife']
queries = ['EndGunViolence', 'GunSense', 'GunRights', '2A', '2ndamendment', 'secondamendment', 'guncontrolnow']
#queries = ['PrayToEndAbortion']
max_tweets = 50000
for query in queries:
    extract_tweets(query, "2012-01-01", "2014-01-01", max_tweets, fn = query + '.txt')
