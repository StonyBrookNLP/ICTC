import cherrypy
import atexit

from subprocess import Popen, PIPE

class ICTC(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def translate(self, message, optionsBot):
        print message, optionsBot

        # translate_prog.stdin.write(text + '\n')
        # translate_prog.stdin.flush()
        # op_text = translate_prog.stdout.readline()[1:] .strip()

        
        if optionsBot == 'c':
          response = 'Clinton response'
          meme_url = 'https://i.imgflip.com/1cq4kr.jpg'
        else:
          response = 'Trump response' 
          meme_url = 'https://i.imgflip.com/1cblat.jpg' 

        return_json = {
          'response': response,
          'meme_url': meme_url
        }

        return return_json

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def feedback(self):
        input_json = cherrypy.request.json
        print input_json

        return "Success"

translate_prog = None
feedbacks = []

@atexit.register
def kill_subprocesses():
    if translate_prog:
        translate_prog.kill()
    else:
        print 'no python prog'


if __name__ == '__main__':
    cmd = '''
          python tensorflow/tensorflow/models/rnn/translate/translate.py --decode --data_dir tensorflow/tensorflow/models/rnn/translate/Tweet_Latest --train_dir tensorflow/tensorflow/models/rnn/translate/checkpoint_latest --size=256 --num_layers=1 --steps_per_checkpoint=50
          '''

    args = cmd.split()
    # translate_prog = Popen(args, shell=False, stdin=PIPE, stdout=PIPE)

    # # flush out the intial info line
    # translate_prog.stdout.readline()

    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080
                       })

    conf = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/home/stufs1/vgottipati/ICTC/App/UI',
            'tools.staticdir.index': 'ictc.html',
        },
        '/Trump': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/home/stufs1/vgottipati/Images/Trump'
        },
        '/Clinton': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/home/stufs1/vgottipati/Images/Clinton'
        }
    }

    cherrypy.quickstart(ICTC(), '/', conf)