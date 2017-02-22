import re

from unidecode import unidecode

from happierfuntokenizing import Tokenizer


def parse_tweet_file(fname):
    with open(fname, "r") as f:
        contents = f.read().decode("utf-8").lower()
    tweets = [unidecode(tweet.strip()) for tweet in contents.split("\n!@#$%\n")]
    print "Total Tweets:", len(tweets)
    return tweets


def strip_url(tweet):
    """
    Remove URLs from the tweet
    """
    url_re = re.compile(":? ?https?://( ?[^\s]+)+")
    url_re2 = re.compile(":? ?([a-z0-9]+\.)?([a-z0-9]+\.)+(com|edu|biz|gov|in(?:t|fo)|mil|net|org|[a-z]{1,4})(/[^\s]+)?")
    tweet = url_re.sub("", tweet)
    tweet = url_re2.sub("", tweet)
    return tweet


def strip_ending_hashtags(tweet):
    """
    Remove trailing hashtags from the tweet. Hashtags in the middle of the tweet
    are retained.
    """
    hash_re = re.compile("(#[^\s]+ *)+\Z")
    tweet = hash_re.sub("", tweet)
    return tweet


def process_quotes(tweet, target):
    """
    Often, the candidates tweet quotes. Here, we keep the contents of quotes
    attributed to the candidate and discard the rest.

    In addition, Trump often copy/pastes others' tweets (like a retweet but not
    actually marked as such). We remove those as well.
    """
    speaker_candidates = []
    if target == "clinton":
        speaker_candidates = ["hillary", "h", "hrc"]
    elif target == "trump":
        speaker_candidates = ["donald", "trump"]

    quote_re = re.compile("\A\"([^\"]+)\" *-+ *([@\w]+)")
    match = quote_re.search(tweet)
    if match:
        quote = match.group(1)
        speaker = match.group(2)
        if speaker in speaker_candidates:
            tweet = quote
        else:
            tweet = ""

    quote_re2 = re.compile("\A\" *@\w+ *:")
    quote_re3 = re.compile("\A\".+\"\Z")
    if quote_re2.search(tweet) or quote_re3.search(tweet):
        tweet = ""
    return tweet


def clean_tweet(tweet, target):
    """
    Clean the tweet by removing hashtags, urls, and quotes
    """
    tweet = strip_url(tweet)
    tweet = strip_ending_hashtags(tweet)
    tweet = process_quotes(tweet, target)
    return tweet


def tokenize_tweet(tweet, tok=None):
    """
    Tokenize the tweet and discard any with fewer than 3 tokens
    """
    if not tok:
        tok = Tokenizer()

    tweet = tweet.strip()
    tokens = tok.tokenize(tweet)
    if len(tokens) > 3:
        tweet = " ".join(tokens)
    else:
        tweet = ""
    return tweet


def remove_self_refs(tweet, target):
    """
    Remove tweets where the candidate's name is referenced, since this generally
    indicates the tweet isn't their own words.

    Ex: 'Watch Hillary on CNN at 9pm'
    """
    if target == "clinton" and "hillary" in tweet:
        tweet = ""
    elif target == "trump" and "donald" in tweet:
        tweet = ""
    return tweet


def process_tweets(tweets, target):
    tok = Tokenizer()

    processed_tweets = []
    for tweet in tweets:
        tweet = clean_tweet(tweet, target)
        tweet = remove_self_refs(tweet, target)
        tweet = tokenize_tweet(tweet, tok)
        if tweet:
            processed_tweets.append(tweet)
    print "Remaining Tweets:", len(processed_tweets)
    return processed_tweets


def write_tweets_to_f(tweets, out_fname):
    with open(out_fname, "w") as f:
        for tweet in tweets:
            f.write(tweet + "\n")


if __name__ == '__main__':
    fnames = ["HillaryClinton.txt", "realDonaldTrump.txt"]
    targets = ["clinton", "trump"]

    for fname, target in zip(fnames, targets):
        print target
        tweets = parse_tweet_file(fname)
        tweets = process_tweets(tweets, target)

        out_fname = "processed_" + fname
        write_tweets_to_f(tweets, out_fname)

