
# coding: utf-8

# In[1]:

from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import re
import happierfuntokenizing
import string
import math
import time
from collections import Counter
import scipy.stats as ss
import operator
import MySQLdb


def wordCount(text, wordDict):

    tok = happierfuntokenizing.Tokenizer(preserve_case=False)
    postCount = 0
    
    ##total words count
    totalWordCount = 0
    
    words = tok.tokenize(text)
    totalWordCount = totalWordCount+len(words)
    postCount = postCount+1

    for word in words:
        if word not in wordDict:
            wordDict[word] = 1
        else:
            wordDict[word] = wordDict[word]+1
    
    
            
    return totalWordCount

def wordCountAcrossAllUsers(usersWordsDict):
    
    totalWordsDict = set()
    for user in usersWordsDict:
        dictUser = usersWordsDict[user]
        for word in dictUser:
            if word not in totalWordsDict:
                totalWordsDict.add(word)
            
    
    return len(totalWordsDict)



# In[2]:

def readTweetsFromDb(side, host_name="localhost", user_name="shreya", db_name="twitterGH"):
    
    db = MySQLdb.connect(host=host_name,   
                     user=user_name,
                     db=db_name)
    
    cur = db.cursor()
    i = 1
    
    cur.execute("select message_id, message, created_time, message_side, original_tweet from twt_20mil where message_side=(%s)", (side))
    
    rows = cur.fetchall()
    i = 0
    
    tweets = []
    orig_tweets = []
    for row in rows:
        tweets.append(str(row[1]))
        orig_tweets.append(str(row[4]))
        
        
    db.close()
    
    return tweets, orig_tweets

for_tweets, for_orig_tweets = readTweetsFromDb("for")
against_tweets, against_orig_tweets = readTweetsFromDb("against")


# In[3]:


all_tweets = for_tweets+against_tweets

usersWordsDict = {}
totalWordsDict = {}

i = 0
for tweet in all_tweets:
    
    wordsDict = {}
    twc = wordCount(str(tweet), wordsDict)
    
    usersWordsDict[i] = wordsDict
    totalWordsDict[i] = twc
    
    i = i+1



# In[4]:

print usersWordsDict[2]

print len(for_tweets)
print len(against_tweets)

print against_tweets[29]


# In[5]:

def topicDistribution(topic_dict, userWDict, twc):
    
    p_topic_user = 0.0
    for word in userWDict:
        p_word_user = 0.0
        score = 0.0
        
        if word in topic_dict:
            p_word_user = float(userWDict[word])/float(twc)
            score = topic_dict[word]
       
        #print "word score\t", dfTopicslice[(dfTopicslice['term']==word)]['weight']
        p_topic_user = p_topic_user + score * p_word_user
    
    return p_topic_user


topic_file = open('topic_cond_word_probab.csv')
topic_dict = {}
flag_header = True


for line in topic_file.readlines():
    if flag_header:
        flag_header = False
        continue
    split_line = line.replace('"','').split(' ')
    term_weight = {}
    
    if len(split_line) > 2:
        topic = split_line[1]
        term = split_line[0]
        w = float(split_line[2])
        
        if topic in topic_dict: 
            term_weight = topic_dict[topic]
            term_weight[term] = w
            topic_dict[topic] = term_weight
        else:
            term_weight[term] = w
            topic_dict[topic] = term_weight
            
            
userTopicDistDict = {}
i = 0
topic_vectors = []

for users in usersWordsDict:
    topic_probab = {}
    
    for topic in topic_dict:
        probab = topicDistribution(topic_dict[topic], usersWordsDict[users], totalWordsDict[users])
        topic_probab [topic] = probab
    
    userTopicDistDict[users] = [v[1] for v in sorted(topic_probab.items(), key=operator.itemgetter(0)) ]
    topic_vectors.append(userTopicDistDict[users])

print userTopicDistDict[24]

print userTopicDistDict[128]



# In[20]:

'''
from sklearn.metrics.pairwise import linear_kernel



for i in range(20, 30):
    cosine_similarities = linear_kernel(np.array(topic_vectors[i]), np.array(topic_vectors[len(for_tweets):]))
    cosine_similarities = cosine_similarities.flatten()
    sorted_idx = np.argsort(cosine_similarities)[::-1]
    top_num = 5
    top5_pro = []
    top5_con = []
    
    
    print "\n########### ", for_tweets[i].strip(), "################"
    print topic_vectors[i]
    
    for idx in sorted_idx:
        top5_con.append(against_tweets[idx])
        print against_tweets[idx], "\t", against_orig_tweets[idx]
        print topic_vectors[len(for_tweets)+idx]
        if len(top5_con) == top_num:
            break

    
file_out.close()
file_out1.close()
'''


# In[ ]:

file_out = open('PrayAbortion_lda_cosine_similarity_5.txt', 'w')
file_out1 = open('Prochoice_lda_cosine_similarity_5.txt', 'w')


for i in range(1, len(for_tweets)):
    score_dict = {}
    for j in range(len(for_tweets), len(topic_vectors)):
        score = ss.entropy(topic_vectors[i], topic_vectors[j])
        score_dict[j] = score

    con_ids = [v[0] for v in sorted(score_dict.items(), key=operator.itemgetter(1))[:5] ]
    top = 0
    
    #print "\n-> ", for_orig_tweets[i].strip()
    for id_twt in con_ids:
        #print against_orig_tweets[id_twt - len(for_tweets)]
        top = top+1
        file_out.write(str(for_orig_tweets[i])+"\n")
        file_out1.write(str(against_orig_tweets[id_twt - len(for_tweets)])+"\n")
        if top == 5:
            break

file_out.close()
file_out1.close()            


# In[ ]:



