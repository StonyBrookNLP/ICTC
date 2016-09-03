# coding: utf-8

import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from preprocess import *

def discard_from_set(s, discard_items):
    for item in discard_items:
        s.discard(item)
        
discard_items = ['', ' ']


def parse_tweets(fn):

    f = open(fn, 'r')
    tweets_text = f.read().lower()
    f.close()

    tweets = tweets_text.split('\n!@#$%\n')
    tweets = [tweet.lower().strip() for tweet in tweets]
    tweets = set(tweets)
    
    discard_from_set(tweets, discard_items)

    return tweets

pro_tags = ['PrayToEndAbortion']#, 'prolife', 'defundpp', 'stand4life', 'ChooseLife']
con_tags = ['prochoice']#, 'StandWithPP', 'reprorights', 'protectchoice']

pro_tags_filter = {tag.lower() for tag in ['#prochoice']}
con_tags_filter = {tag.lower() for tag in ['#prolife']}

pro_tweets = set()
for tag in pro_tags:
    current_tweets = parse_tweets(tag + '.txt')
    
    pre_processed_tweets = []
    c = 0
    for tweet in current_tweets:
        if not contains_both_tags(tweet, pro_tags_filter, con_tags_filter):
            tweet = preprocess(tweet).strip()
            pre_processed_tweets.append(tweet)
        else:
            c += 1

    print 'Number of filtered tweets: {0} in tag: {1}'.format(c, tag)
        
    
    pro_tweets.update(pre_processed_tweets)


con_tweets = set()
for tag in con_tags:
    current_tweets = parse_tweets(tag + '.txt')
    
    pre_processed_tweets = []
    
    c = 0
    for tweet in current_tweets:
        if not contains_both_tags(tweet, pro_tags_filter, con_tags_filter):
            tweet = preprocess(tweet).strip()
            pre_processed_tweets.append(tweet)
        else:
            c += 1 

    print 'Number of filtered tweets: {0} in tag: {1}'.format(c, tag)
    
    con_tweets.update(pre_processed_tweets)

discard_from_set(pro_tweets, discard_items)
discard_from_set(con_tweets, discard_items)

pro_tweets = list(pro_tweets)
con_tweets = list(con_tweets)

con_start_idx = len(pro_tweets)

tweets = pro_tweets + con_tweets

print 'Number of pro and con tweets: {0}, {1}'.format(len(pro_tweets), len(con_tweets))

vectorizer = TfidfVectorizer()
tfidf_vecs = vectorizer.fit_transform(tweets)

file_out = open('PrayAbortion_cosine_similarity_5.txt', 'w')
file_out1 = open('Prochoice_cosine_similarity_5.txt', 'w')

k = 5
for i in range(0, len(pro_tweets)):
#for i in random.sample(range(con_start_idx), 5):
    cosine_similarities = linear_kernel(tfidf_vecs[i:i+1], tfidf_vecs)
    cosine_similarities = cosine_similarities.flatten()
    sorted_idx = np.argsort(cosine_similarities)[::-1]
    topk_pro = []
    topk_con = []

    for idx in sorted_idx:
        if idx < con_start_idx and idx != i:
            topk_pro.append(tweets[idx])
            if len(topk_pro) == k:
                break

    for idx in sorted_idx:
        if idx >= con_start_idx and idx != i:
            topk_con.append(tweets[idx])
            if len(topk_con) == k:
                break
        
    for tweet in topk_con:
        file_out.write(str(tweets[i])+"\n")
        file_out1.write(str(tweet)+"\n")
    
    
    # print 'Candidate tweet:', tweets[i]
    # print 'Top con tweets:'
    # for tweet in topk_con:
    #     print tweet
        
    # print '\n\n'


file_out.close()
file_out1.close()

