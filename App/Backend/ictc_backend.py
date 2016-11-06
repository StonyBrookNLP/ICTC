# _*_ coding:utf-8 _*_

import cherrypy
import atexit
import sqlite3
import threading
from random import choice
from subprocess import Popen, PIPE

trump_bot = None
clinton_bot = None
con = None
trump_bot_lock = threading.Lock()
clinton_bot_lock = threading.Lock()
trump_tweets = None
clinton_tweets = None

def read_tweets(fn):
    with open(fn, 'r') as tweets_file:
        tweets = tweets_file.read().split('\n')

    tweets.pop(-1)
    processed_tweets = []
    for tweet in tweets:
        tweet = tweet.decode('utf-8')
        num_words = len(tweet.split())
        if num_words < 40 and num_words >= 5:
            processed_tweets.append(tweet)

    return processed_tweets

@atexit.register
def cleanup():
    global trump_bot
    if trump_bot:
        trump_bot.kill()
        trump_bot = None
        cherrypy.log('Closed Trump bot')
    global clinton_bot
    if clinton_bot:
        clinton_bot.kill()
        clinton_bot = None
        cherrypy.log('Closed Clinton bot')
    global con
    if con:
        con.close()
        con = None
        cherrypy.log('Closed DB connection')
    cherrypy.log('Finished cleanup')


class ICTC(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def randomTweet(self, candidate):
        if candidate == 'c':
            return choice(clinton_tweets)
        return choice(trump_tweets)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def translate(self, input, optionsBot):
        if optionsBot == 'c':
            bot = clinton_bot
            lock = clinton_bot_lock
        else:
            bot = trump_bot
            lock = trump_bot_lock

        with lock:
            # the input str is in unicode
            # need to encode into normal string before piping
            try:
                bot.stdin.write(input.encode('utf8') + '\n')
                bot.stdin.flush()
                response = bot.stdout.readline()[1:].strip()
            except:
                cherrypy.log('Input: ' + input)
                cherrypy.log('Response: ' + response)
                raise

        # the response str is in normal string
        # need to convert to unicode before responding
        response = response.decode('utf-8')
        values = [
            optionsBot,
            input,
            response,
            cherrypy.request.remote.ip
            ]
        con.execute('insert into Interaction(bot, input, response, ip) values(?, ?, ?, ?)', values)

        return response

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def feedback(self):
        feedback_data = cherrypy.request.json
        values = [
            feedback_data['bot'],
            feedback_data['inp_text'],
            feedback_data['response_text'],
            feedback_data['content_score'],
            feedback_data['style_score'],
            feedback_data['suggestion_text'],
            cherrypy.request.remote.ip
            ]
        con.execute('insert into Feedback(bot, input, response, content_score, style_score, suggestion, ip) values(?, ?, ?, ?, ?, ?, ?)', values)

        return "Success"


if __name__ == '__main__':
    home_dir = '/Users/bobby/Downloads'
    #home_dir = '/home/stufs1/vgottipati'
    translate_folder = home_dir + '/tensorflow/tensorflow/models/rnn/translate'
    translate_args = '--decode --data_dir {0} --train_dir {1} --size=256 --num_layers=1 --steps_per_checkpoint=10000'

    trump_args = (translate_folder + '/trump_data_dir', translate_folder + '/trump_checkpoint_dir')
    trump_bot_cmd = 'python ' + translate_folder + '/translate.py ' + (translate_args.format(*trump_args))
    trump_bot = Popen(trump_bot_cmd.split(), shell=False, stdin=PIPE, stdout=PIPE)
    # flush out the intial info line
    trump_bot.stdout.readline()
    cherrypy.log('Started Trump bot')

    clinton_args = (translate_folder + '/clinton_data_dir', translate_folder + '/clinton_checkpoint_dir')
    clinton_bot_cmd = 'python ' + translate_folder + '/translate.py ' + (translate_args.format(*clinton_args))
    clinton_bot = Popen(clinton_bot_cmd.split(), shell=False, stdin=PIPE, stdout=PIPE)
    # flush out the intial info line
    clinton_bot.stdout.readline()
    cherrypy.log('Started Clinton bot')

    con = sqlite3.connect(
        home_dir + '/feedback_v2.db', 
        isolation_level=None, 
        check_same_thread=False)
    con.execute("create table if not exists Feedback(bot TEXT, input TEXT, response TEXT, content_score INTEGER NOT NULL, style_score INTEGER NOT NULL, suggestion TEXT, ip TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")
    con.execute("create table if not exists Interaction(bot TEXT NOT NULL, input TEXT NOT NULL, response TEXT NOT NULL, ip TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")

    cherrypy.engine.subscribe('stop', cleanup)

    
    clinton_tweets = read_tweets(home_dir + '/clinton_tweets.txt')
    trump_tweets = read_tweets(home_dir + '/trump_tweets.txt')
    cherrypy.log('Number of Clinton tweets: {0}'.format(len(clinton_tweets)))
    cherrypy.log('Number of Trump tweets: {0}'.format(len(trump_tweets)))

    app_conf = {
        '/': {
            'tools.staticdir.on'            : True,
            'tools.staticdir.dir'           : home_dir + '/Static',
            'tools.staticdir.index'         : 'ictc.html'
        }
    }

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8081,
        'log.screen': False,
        'log.access_file': home_dir + '/server_access.log',
        'log.error_file': home_dir + '/server_error.log'
                       })

    try:
        cherrypy.quickstart(ICTC(), '/', app_conf)
    except:
        cleanup()
        raise