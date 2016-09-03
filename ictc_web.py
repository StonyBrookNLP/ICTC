import cherrypy
import atexit

from subprocess import Popen, PIPE

class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <form method="post" action="translate">
              <p>Please enter text against abortion to see its opposing view:</p>
              <textarea name="text" cols=40 rows=6></textarea>
              <button type="submit">Translate!</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def translate(self, text=''):
        translate_prog.stdin.write(text + '\n')
        translate_prog.stdin.flush()
        op_text = translate_prog.stdout.readline()[1:] .strip()
        #return op_text

        return_pg = '''
            <html>
                <head></head>
              <body>
                <form method="post" action="feedback">
                    <input type="hidden" name="inp_text" value="{0}">
                    <input type="hidden" name="op_text" value="{1}">
                    <p>The translated text is: <b>{2}</b></p>
                    <p>Please choose the following about the translation:</p>
                    <select name=feedback>
                      <option value="" selected>Please select an option...</option>
                      <option value="1">Translation makes sense</option>
                      <option value="0">Translation is incorrect</option>
                    </select>
                    <p>If it doesnt make sense, please type a better translation:</p>
                    <textarea name="corrected_text" cols=40 rows=6></textarea>
                    <button type="submit">Submit</button>
                </form>
              </body>
            </html>
            '''.format(text, op_text, op_text)

        return return_pg

    @cherrypy.expose
    def feedback(self, inp_text, op_text, feedback='', corrected_text=''):
        if feedback:
            correct = True if int(feedback) else False
            corrected_text = corrected_text if not correct else ''
            feedbacks.append((inp_text, op_text, correct, corrected_text))

            print feedbacks[-1]

        return_html = '''<html>
          <head></head>
          <body>'''
        if feedback:
            return_html = return_html + '''<p>Thank you for your feedback!</p>'''
        return_html = return_html + '''
            <form method="post" action="translate">
              <p>Please enter text against abortion to see its opposing view:</p>
              <textarea name="text" cols=40 rows=6></textarea>
              <button type="submit">Translate!</button>
            </form>
          </body>
        </html>'''
        return return_html

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
    translate_prog = Popen(args, shell=False, stdin=PIPE, stdout=PIPE)

    # flush out the intial info line
    translate_prog.stdout.readline()

    cherrypy.quickstart(HelloWorld())