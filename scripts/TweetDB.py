__author__ = 'shreya'

from sets import Set
import MySQLdb
import sys
import datetime
from happierfuntokenizing import Tokenizer
import preprocess as pre




def preprocessTweets(file):
    fhandle = open(file)
    allLines = Set()
    originalSet = {}
    for line in fhandle.read().split('\n!@#$%\n'):
        text = pre.strip_url(line.lower())
        text = pre.strip_hash_tags(text)
        
        allLines.add(text)
        originalSet[text] = line.lower()
    
    return allLines, originalSet


##filtering tweets containing tags from both sides"
def tweetsFilter(tweets_file, fname):

    inFile = open(tweets_file)
    outFile = open(fname, 'w')
    tok = Tokenizer(preserve_case=True)
    
    for line in inFile.read().split('\n!@#$%\n'):
       tokenized = tok.tokenize(line)
       
       flag = pre.filter_tweets(tokenized, ["#prolife"], ["#prochoice"])
       if flag:
           continue
       
       if len(line) > 0: outFile.write(line+"\n!@#$%\n")
       

   

def storeInDb(tweets, side, originalTweetSet=None, host_name="localhost", user_name="shreya", db_name="twitterGH"):
    
    db = MySQLdb.connect(host=host_name,   
                     user=user_name,
                     db=db_name)
    
    cur = db.cursor()
    i = 1
    now = datetime.datetime.now()
    str_now = now.date().isoformat()
    
    for line in tweets:
        cur.execute("INSERT INTO twt_20mil (message_id, message, created_time, message_side, original_tweet) VALUES (%s,%s,%s,%s,%s)", (str(i), str(line), str_now, side, originalTweetSet[line]))
        i = i+1
        db.commit()
    
    db.close()
    

if __name__ == '__main__':
    
    fname1 = sys.argv[1]
    fname2 = sys.argv[2]
    
    tweetsFilter(fname1, fname1.split('.')[0]+"_filtered."+fname1.split('.')[1])
    tweetsFilter(fname2, fname2.split('.')[0]+"_filtered."+fname2.split('.')[1])
    
    originalSet = {}
    tweets, originalSet = preprocessTweets(fname1.split('.')[0]+"_filtered."+fname1.split('.')[1])
    storeInDb(tweets, "for", originalSet)
    
    tweets, originalSet = preprocessTweets(fname2.split('.')[0]+"_filtered."+fname2.split('.')[1])
    storeInDb(tweets, "against", originalSet)
    
    
    
    
        
    