import cherrypy
import atexit
import sqlite3

from subprocess import Popen, PIPE

trump_bot = None
clinton_bot = None
con = None

@atexit.register
def cleanup():
    global trump_bot
    if trump_bot:
        trump_bot.kill()
        trump_bot = None
        print 'Closed Trump bot'
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

        trump_bot.stdin.write(message + '\n')
        trump_bot.stdin.flush()
        response = trump_bot.stdout.readline()[1:].strip()

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
    translate_args = '--decode --data_dir {0} --train_dir {1} --size=256 --num_layers=1 --steps_per_checkpoint=50'

    trump_args = (translate_folder + '/trump_data_dir', translate_folder + '/trump_checkpoint_dir')
    trump_bot_cmd = 'python ' + translate_folder + '/translate.py ' + (translate_args.format(*trump_args))
    trump_bot = Popen(trump_bot_cmd.split(), shell=False, stdin=PIPE, stdout=PIPE)
    # flush out the intial info line
    trump_bot.stdout.readline()

    con = sqlite3.connect(
        home_dir + '/feedback.db', 
        isolation_level=None, 
        check_same_thread=False)
    con.execute("create table if not exists Feedback(bot TEXT, input TEXT, response TEXT, content_score INTEGER, style_score INTEGER, suggestion TEXT)")

    cherrypy.engine.subscribe('stop', cleanup)

    conf = {
        '/': {
            'tools.staticdir.on'    : True,
            'tools.staticdir.dir'   : home_dir + '/Static',
            'tools.staticdir.index' : 'ictc.html'
        }
    }

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080
                       })

    try:
        cherrypy.quickstart(ICTC(), '/', conf)
    except:
        cleanup()
        raise