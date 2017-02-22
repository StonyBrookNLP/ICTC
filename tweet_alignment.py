import cPickle
import numpy as np
import re

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as stopwords


def load_embeddings(fname):
    with open(fname, "rb") as f:
        embeddings = cPickle.load(f)
    return embeddings


def load_tweets(fname):
    tweets = []
    with open(fname, "r") as f:
        for line in f:
            tokens = line.strip().split()
            tweets.append(tokens)
    return tweets


def add_embed_for_tok(cur_embeds, tok, embeddings_dict):
    if tok not in embeddings_dict:
        return 0
    e = embeddings_dict[tok]
    for i in range(len(e)):
        cur_embeds[i] += e[i]
    return 1


def get_tweet_embeddings(tweets, embeddings_dict, num_dims=200):
    tweet_embeds = []

    user_re = re.compile("@\w+")
    hashtag_re = re.compile("#(\S+)")
    number_re = re.compile("[-+]?[.\d]*[\d]+[:,.\d]*")

    for tweet in tweets:
        embed = [0.0 for _ in range(num_dims)]
        count = 0
        for tok in tweet:
            if tok in stopwords:
                continue
            if user_re.search(tok):
                count += add_embed_for_tok(embed, "<user>", embeddings_dict)
            elif hashtag_re.search(tok):
                count += add_embed_for_tok(embed, "<hashtag>", embeddings_dict)

                hashtag_val = hashtag_re.search(tok).group(1)
                count += add_embed_for_tok(embed, hashtag_val, embeddings_dict)
            elif number_re.search(tok):
                count += add_embed_for_tok(embed, "<number>", embeddings_dict)
            else:
                count += add_embed_for_tok(embed, tok, embeddings_dict)
        if count != 0:
            embed = [e / count for e in embed]
        tweet_embeds.append(embed)
    return tweet_embeds


def align_tweets(src_tweets, src_embed, tgt_tweets, tgt_embed, k=5):
    sims = cosine_similarity(src_embed, tgt_embed)
    pairs = [[], [], []]
    cur_bin = 0
    for i in range(len(src_tweets)):
        src_t = src_tweets[i]
        sorted_idx = np.argsort(sims[i])[::-1][:k]
        for j in sorted_idx:
            tgt_t = tgt_tweets[j]
            if cur_bin == 0:
                pairs[0].append((src_t, tgt_t))
                break
            elif cur_bin == 1:
                pairs[1].append((src_t, tgt_t))
                break
            else:
                pairs[2].append((src_t, tgt_t))
        cur_bin = (cur_bin + 1) % 10
    print "Test: {}; Tune: {}; Train: {}".format(len(pairs[0]), len(pairs[1]),
                                                 len(pairs[2]))
    return pairs


def write_pairs_to_f(pairs, src_fname, tgt_fname):
    with open(src_fname, "w") as src_f:
        with open(tgt_fname, "w") as tgt_f:
            for src_t, tgt_t in pairs:
                src_f.write(" ".join(src_t) + "\n")
                tgt_f.write(" ".join(tgt_t) + "\n")


if __name__ == '__main__':
    embeddings_dict = load_embeddings("data/glove.twitter.200d.pkl")

    hrc_tweets = load_tweets("data/processed_HillaryClinton.txt")
    hrc_embed = get_tweet_embeddings(hrc_tweets, embeddings_dict)

    trump_tweets = load_tweets("data/processed_realDonaldTrump.txt")
    trump_embed = get_tweet_embeddings(trump_tweets, embeddings_dict)

    print "Aligning Clinton --> Trump"
    hrc_test, hrc_tune, hrc_train = align_tweets(hrc_tweets, hrc_embed, trump_tweets,
                                                 trump_embed)
    out_dir = "tensorflow/data/clinton_to_trump/"
    write_pairs_to_f(hrc_test, out_dir + "test.clinton", out_dir + "test.trump")
    write_pairs_to_f(hrc_tune, out_dir + "dev.clinton", out_dir + "dev.trump")
    write_pairs_to_f(hrc_tune, out_dir + "train.clinton", out_dir + "train.trump")

    print "Aligning Trump --> Clinton"
    trump_test, trump_tune, trump_train = align_tweets(trump_tweets, trump_embed,
                                                       hrc_tweets, hrc_embed)
    out_dir = "tensorflow/data/trump_to_clinton/"
    write_pairs_to_f(trump_test, out_dir + "test.trump", out_dir + "test.clinton")
    write_pairs_to_f(trump_tune, out_dir + "tune.trump", out_dir + "tune.clinton")
    write_pairs_to_f(trump_train, out_dir + "train.trump", out_dir + "train.clinton")
