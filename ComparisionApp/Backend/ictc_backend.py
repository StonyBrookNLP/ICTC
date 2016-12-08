# _*_ coding:utf-8 _*_
import cherrypy
import atexit
import sqlite3
import threading
from random import choice

con = None
pairs = {}
for i in range(12):
    s = str(i)
    b = 't' if (i/3) % 2 else 'c'
    pair = [i, i/3, b, 'inp' + s, 'r1_'+ s, 'r2_' + s]
    pairs[i] = pair

next_user_id = '1'
user_data = {}
waiting_lock = threading.Lock()
backlog_lock = threading.Lock()
user_lock = threading.Lock()
backlog = pairs.keys()
waiting = []
time_limit = 1 * 60

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
    def index(self):
        cookie = cherrypy.response.cookie
        cookies = {
            'order_id': '1',
            'bot' : 't',
            'input': 'A sized tweet from clinton. Testing to see long input',
            'response1': 'Response 1 from Trump Response 1',
            'response2': 'Response 2 from Trump'
        }
        for name, value in cookies.iteritems():
            cookie[name] = value
            cookie[name]['path'] = '/'
            cookie[name]['max-age'] = 3600 ** 5
            cookie[name]['version'] = 1
        return client_html

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getPair(self, user_id):
        global backlog
        selected_pair = None
        now = time.time()
        with waiting_lock:
            for pair in waiting:
                ts = pair[0]
                if ts + time_limit > now:
                    # need to serve this to user
                    if pair[2] in user_data[user_id]:
                        # user has already answered this q
                        # so skip it
                        continue
                    else:
                        pair[0] = now
                        # TODO: add things served also to user data?
                        selected_pair = pair
                        break

        if selected_pair:
            writeToServeDB(self, order_id, user_id, cherrypy.request.remote.ip)
            return selected_pair
        # else return pair with lowest order id
        with backlog_lock:
            selected_pair = min(backlog, key=lambda x: x[0])
            # remove pair from backlog
            backlog = [pair for pair in backlog if pair != selected_pair]
        # add timestamp to pair data
        selected_pair = [now] + selected_pair
        # put pair in waiting q
        with waiting_lock:
            waiting.append(pair)
        writeToServeDB(self, order_id, user_id, cherrypy.request.remote.ip)
        return pair

    def writeToServeDB(self, order_id, user_id, ip):
        values = [
            order_id,
            user_id,
            ip
            ]
        con.execute('insert into Serve(order_id, user_id, ip) values(?, ?, ?)', values)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def feedback(self):
        global waiting
        feedback_data = cherrypy.request.json
        user_id = feedback_data['user_id']
        order_id = feedback_data['order_id']
        with user_lock:
            try:
                user_data[user_id].add(true_id)
            except:
                user_data[user_id] = {true_id}
        with waiting_lock:
            # remove pair from waiting
            waiting = [pair for pair in waiting if pair[1] != order_id]
        values = [
            feedback_data['bot'],
            feedback_data['input'],
            feedback_data['response1'],
            feedback_data['response2'],
            feedback_data['content_score1'],
            feedback_data['content_score2'],
            feedback_data['style_score1'],
            feedback_data['style_score2'],
            user_id,
            cherrypy.request.remote.ip
            ]
        con.execute('insert into Feedback(bot, input, response1, response2, content_score1, content_score2, style_score1, style_score2, user_id, ip) values(?, ?, ?, ?, ?, ?, ?, ?, ? , ?)', values)

        return True


if __name__ == '__main__':
    home_dir = '/Users/bobby/Downloads'
    #home_dir = '/home/stufs1/vgottipati'

    con = sqlite3.connect(
        home_dir + '/comparision.db', 
        isolation_level=None, 
        check_same_thread=False)
    con.execute("create table if not exists Feedback(bot TEXT, input TEXT, response1 TEXT, response2 TEXT, content_score1 INTEGER NOT NULL, content_score2 INTEGER NOT NULL, style_score1 INTEGER NOT NULL, style_score2 INTEGER NOT NULL, suggestion TEXT, user_id TEXT, ip TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")
    con.execute("create table if not exists Serve(order_id TEXT, user_id, ip TEXT, ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)")

    cherrypy.engine.subscribe('stop', cleanup)

    app_conf = {
        '/': {
            'tools.staticdir.on'            : True,
            'tools.staticdir.dir'           : home_dir + '/Static'
        }
    }

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'log.screen': False,
        'log.access_file': home_dir + '/server_access.log',
        'log.error_file': home_dir + '/server_error.log'
                       })

    client_html = ''
    with open(home_dir + '/Static/ictc.html', 'r') as client_html_file:
        client_html = client_html_file.read()

    try:
        cherrypy.quickstart(ICTC(), '/', app_conf)
    except:
        cleanup()
        raise