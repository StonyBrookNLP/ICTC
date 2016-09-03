import re

def strip_url(text):
    url_re = re.compile(r'(https?:// ?[^\s]+)')
    text =  url_re.sub('', text)
    url_re = re.compile(r'([a-z0-9]+\.)?([a-z0-9]+\.)+(com|edu|biz|gov|in(?:t|fo)|mil|net|org|[a-z]{1,4})(/[^\s]+)?')
    
    text = url_re.sub('', text)
    
    return text


def strip_hash_tags(text):
    hash_re = re.compile(r'(#[^\s]+)')
    return hash_re.sub('', text)


def contains_both_tags(tweet, tag_set1, tag_set2):

    tweet_words = tweet.split()

    tag1_present = False
    
    for tag in tag_set1:
        if tag in tweet_words:
            tag1_present = True
            break
    
    for tag in tag_set2:
        if tag in tweet_words:
            if tag1_present:
                return True    
    
    return False

def preprocess(tweet):
    tweet = strip_url(tweet)
    tweet = strip_hash_tags(tweet)

    return tweet
