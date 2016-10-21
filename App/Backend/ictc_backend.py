import cherrypy
import atexit

from subprocess import Popen, PIPE

class ICTC(object):
    @cherrypy.expose
    def index(self):
        return client_html

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def translate(self, message, optionsBot):
        print message, optionsBot

        # translate_prog.stdin.write(text + '\n')
        # translate_prog.stdin.flush()
        # op_text = translate_prog.stdout.readline()[1:] .strip()

        return_json = {
          'response': 'Trump response kjsbgerbgreskgrelntselgbtleshbltskrbhlsebgl g esglsenhlthslrdn slgrlkgselhsl slgrlgeargogsgalgiluaguwgAI GO;GHAOGHRAOIHGROEHGOIAHGOIHGR WFHOEGHAOGHAWROGHRREORHGEO HSEOIHESOHTSOIRH gseohsohos',
          'meme_url': 'https://i.imgflip.com/1cblat.jpg'
        }

        return return_json

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def feedback(self, **kwargs):
        input_json = cherrypy.request.json
        print input_json
        print kwargs

        return "Success"

translate_prog = None
feedbacks = []

client_html = ''
with open('/Users/bobby/Downloads/temp2.html', 'r') as client_html_file:
    client_html = client_html_file.read()

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

    conf = {
        '/code': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/Users/bobby/Downloads/'
        },
        '/Trump': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/Users/bobby/Downloads/Trump'
        }
    }

    cherrypy.quickstart(ICTC(), '/', conf)