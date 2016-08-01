"""Service to collect analytics for a given website.
"""
from flask import Flask, request, render_template
from user_agents import parse
from urlparse import urlparse
from collections import defaultdict
import uuid
import logging
import datetime
import statsd
import stat_server


app = Flask(__name__)
logging.basicConfig(filename='web_log', level=logging.INFO)

def send_info(stat, param=None): # stat is a func defined in stat_server is a string
    stat_func = getattr(stat_server, stat)
    logging.info('logged: {}, {}'.format(stat, param))
    stat_func(param)

@app.route('/index')
def index():
    # send  logs to a `web_log` file
    # Create response object
    response = app.make_response(render_template('index.html', time_spent=0))
    response.headers['Content-Type'] = 'text/html'
    print request.args.get('leaving', 'no value!!!')
    if request.args.get('leaving', ''):
        time_spent = request.args.get('timeSpent', '0')
        stat_server.time_spent(int(time_spent))

    # create cookie to be set on a given browser
    UUID = bytes(uuid.uuid4())
    print UUID , 'XXXXXXXXXXX'
    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=90)
    # cookie will expire in 90 days
    response.set_cookie('user_id', value=UUID, expires=future)
    send_info('user_id', param=UUID)

    # parse `user_agent` from the responce headers
    ua_string = request.headers['user-agent']
    user_agent = parse(ua_string)

    device_type = user_agent.device.family
    send_info('ua_device', param=device_type)

    browser = user_agent.browser.family
    send_info('ua_browser', param=browser)

    is_mobile = user_agent.is_mobile
    if is_mobile:
        send_info('mobile')

    is_touch_capable = user_agent.is_touch_capable
    if is_touch_capable:
        send_info('touch_capable')

    if request.headers.get('referer'):
        referer_parsed =  urlparse(request.headers['referer'])
        referer = referer_parsed.netloc.split(':')[0]
        send_info('referer', param=referer)

    code = response.status_code
    send_info('status_stat', param=code)

    send_info('users_stat')


    return response
    
if __name__ == '__main__':
    app.debug = True
    app.run()

