import cherrypy
import atexit
import sqlite3

from subprocess import Popen, PIPE

translate_prog = None
con = None

@atexit.register
def cleanup():
    global translate_prog
    if translate_prog:
        translate_prog.kill()
        translate_prog = None
        print 'Closed translation programs'
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
        print message, optionsBot

        # translate_prog.stdin.write(text + '\n')
        # translate_prog.stdin.flush()
        # op_text = translate_prog.stdout.readline()[1:] .strip()

        return message

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
    cmd = '''
          python tensorflow/tensorflow/models/rnn/translate/translate.py --decode --data_dir tensorflow/tensorflow/models/rnn/translate/Tweet_Latest --train_dir tensorflow/tensorflow/models/rnn/translate/checkpoint_latest --size=256 --num_layers=1 --steps_per_checkpoint=50
          '''

    args = cmd.split()
    # translate_prog = Popen(args, shell=False, stdin=PIPE, stdout=PIPE)

    # # flush out the intial info line
    # translate_prog.stdout.readline()

    con = sqlite3.connect(
        '/Users/bobby/Downloads/feedback.db', 
        isolation_level=None, 
        check_same_thread=False)
    con.execute("create table if not exists Feedback(bot TEXT, input TEXT, response TEXT, content_score INTEGER, style_score INTEGER, suggestion TEXT)")

    cherrypy.engine.subscribe('stop', cleanup)

    conf = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/Users/bobby/Downloads/static',
            'tools.staticdir.index': 'ictc.html',
        }
    }

    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080
                       })

    try:
        cherrypy.quickstart(ICTC(), '/', conf)
    except:
        cleanup()
        raise