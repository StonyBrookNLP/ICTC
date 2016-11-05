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

@atexit.register
def cleanup():
    global trump_bot
    if trump_bot:
        trump_bot.kill()
        trump_bot = None
        print 'Closed Trump bot'
    global clinton_bot
    if clinton_bot:
        clinton_bot.kill()
        clinton_bot = None
        print 'Closed Clinton bot'
    global con
    if con:
        con.close()
        con = None
        print 'Closed DB connection'
    print 'Finished cleanup'


class ICTC(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def translate(self, message, optionsBot):
        if optionsBot == 'c':
            bot = clinton_bot
            lock = clinton_bot_lock
        else:
            bot = trump_bot
            lock = trump_bot_lock

        with lock:
            bot.stdin.write(message + '\n')
            bot.stdin.flush()
            response = bot.stdout.readline()[1:].strip()
        
        return response

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def feedback(self):
        feedback_data = cherrypy.request.json
        print feedback_data
        values = [
            feedback_data['bot'],
            feedback_data['inp_text'],
            feedback_data['response_text'],
            feedback_data['content_score'],
            feedback_data['style_score'],
            feedback_data['suggestion_text']
            ]
        con.execute('insert into Feedback values (?, ?, ?, ?, ?, ?)', values)

        return "Success"


if __name__ == '__main__':
    #home_dir = '/Users/bobby/Downloads'
    home_dir = '/home/stufs1/vgottipati'
    translate_folder = home_dir + '/tensorflow/tensorflow/models/rnn/translate'
    translate_args = '--decode --data_dir {0} --train_dir {1} --size=256 --num_layers=1 --steps_per_checkpoint=10000'

    trump_args = (translate_folder + '/trump_data_dir', translate_folder + '/trump_checkpoint_dir')
    trump_bot_cmd = 'python ' + translate_folder + '/translate.py ' + (translate_args.format(*trump_args))
    trump_bot = Popen(trump_bot_cmd.split(), shell=False, stdin=PIPE, stdout=PIPE)
    # flush out the intial info line
    trump_bot.stdout.readline()
    print 'Started Trump bot'

    clinton_args = (translate_folder + '/clinton_data_dir', translate_folder + '/clinton_checkpoint_dir')
    clinton_bot_cmd = 'python ' + translate_folder + '/translate.py ' + (translate_args.format(*clinton_args))
    clinton_bot = Popen(clinton_bot_cmd.split(), shell=False, stdin=PIPE, stdout=PIPE)
    # flush out the intial info line
    clinton_bot.stdout.readline()
    print 'Started Clinton bot'

    con = sqlite3.connect(
        home_dir + '/feedback.db', 
        isolation_level=None, 
        check_same_thread=False)
    con.execute("create table if not exists Feedback(bot TEXT, input TEXT, response TEXT, content_score INTEGER, style_score INTEGER, suggestion TEXT)")

    cherrypy.engine.subscribe('stop', cleanup)

    conf = {
        '/': {
            'tools.staticdir.on'    : True,
            'tools.staticdir.dir'   : home_dir + '/Static_new',
            'tools.staticdir.index' : 'ictc.html'
        }
    }

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8081
                       })

    try:
        cherrypy.quickstart(ICTC(), '/', conf)
    except:
        cleanup()
        raise