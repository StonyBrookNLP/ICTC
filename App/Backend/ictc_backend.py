# _*_ coding:utf-8 _*_

import cherrypy
import atexit
import sqlite3
import threading

from subprocess import Popen, PIPE

trump_bot = None
clinton_bot = None
con = None
trump_bot_lock = threading.Lock()
clinton_bot_lock = threading.Lock()
trump_tweets = None
clinton_tweets = None

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
            bot.stdin.write(input + '\n')
            bot.stdin.flush()
            response = bot.stdout.readline()[1:].strip()
        
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
        home_dir + '/feedback.db', 
        isolation_level=None, 
        check_same_thread=False)
    con.execute("create table if not exists Feedback(bot TEXT, input TEXT, response TEXT, content_score INTEGER NOT NULL, style_score INTEGER NOT NULL, suggestion TEXT, ip TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")
    con.execute("create table if not exists Interaction(bot TEXT NOT NULL, input TEXT NOT NULL, response TEXT NOT NULL, ip TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")

    cherrypy.engine.subscribe('stop', cleanup)

    with open(home_dir + '/clinton_tweets.txt', 'r') as tweets_file:
        clinton_tweets = tweets_file.read().split('\n')
        clinton_tweets.pop(-1)

    with open(home_dir + '/trump_tweets.txt', 'r') as tweets_file:
        trump_tweets = tweets_file.read().split('\n')
        trump_tweets.pop(-1)

    app_conf = {
        '/': {
            'tools.staticdir.on'            : True,
            'tools.staticdir.dir'           : home_dir + '/Static',
            'tools.staticdir.index'         : 'ictc.html',
            'tools.sessions.on'             : True,
            'tools.sessions.storage_class'  : 'cherrypy.lib.sessions.FileSession',
            'tools.sessions.storage_path'   : home_dir
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