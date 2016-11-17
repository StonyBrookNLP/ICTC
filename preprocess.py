# coding: utf-8
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


def filter_tweets(line, file_name):
    
    if "hillary" in file_name:
        pattern_cli = "(—|-)\s*(hillary|h)"
        handle = "@hillaryclinton" 
    else:
        pattern_cli = "(—|-)\s*(donaldtrump|trump|donald)" 
        handle = "@realdonaldtrump"
    
    
    line = line.strip()
    flag = True

    #if "\"" in line or "“" in line or "”" in line:
    pattern = re.compile(pattern_cli)
    if pattern.search(line):
        line = re.sub(pattern, "", line)
        line = line.replace('"', "").replace('“', "").replace('”', "")
    else:
        pattern = re.compile("(—|-)\s*@")
        if pattern.search(line):
            flag = False


    if handle in line:
        flag = False

        
    if flag:
        return line
    else:
        return ''

