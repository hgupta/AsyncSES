"""
Copyright (C) 2012 <Robson r@linux.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

try:
    import cjson
    json_encode = cjson.encode
    json_decode = cjson.decode
except ImportError:
    from json import loads as json_decode, dumps as json_encode

import itertools
from lib.bottle import default_app, run, route, request
from lib.amazon_ses import AmazonSES, AmazonError
from lib.outbox import Outbox
from lib.worker import worker, sent, error
from lib.logger import logger
from config import *


class StripPathMiddleware(object):
    #http://bottlepy.org/docs/dev/recipes.html#ignore-trailing-slashes
    def __init__(self, app):
        self.app = app
    
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.app(e,h)

app = StripPathMiddleware(default_app())
outbox = Outbox(maxsize=OUTBOX_MAXSIZE)
ses = AmazonSES(AMAZON_KEY, AMAZON_SECRET)
required_fields = ['from', 'to', 'subject', 'text']


# Thread-safe counters
queued = itertools.count()
rejected = itertools.count()

def error_msg(msg):
    data = {'status': 'error', 'message': msg}
    return json_encode(data)


@route('/add', method=['GET', 'POST'])
def add():
    data = {
        'subject': request.params.get('subject', None),
        'from': request.params.get('from', None),
        'to': request.params.get('to', None),
        'text': request.params.get('text', None),
        'html': request.params.get('html', None),
    }

    headers = request.params.get('headers', None)
    if headers:
        try:
            headers = json_decode(headers)
            data['headers'] = headers
        except:
            rejected.next()
            return error_msg('headers contains invalid json data')

    for field in required_fields:
        if not (data.has_key(field) and data[field]):
            rejected.next()
            return error_msg('missing field %s'%field)

    outbox.put(data)
    queued.next()
    resp = {'status': 'queued', 'message': 'ok',}

    return json_encode(resp)


@route('/status', method=['GET', 'POST'])
def index():
    getvalue = lambda x: str(x.__reduce__()[1][0])
    resp = {
        'sent': getvalue(sent),
        'error': getvalue(error),
        'queued': getvalue(queued),
        'rejected': getvalue(rejected),
        'outbox': outbox.qsize(),
    }
    return json_encode(resp)


@route('/quota', method=['GET', 'POST'])
def quota():
    try:
        q = ses.getSendQuota()
    except AmazonError, e:
        return error_msg(e.__unicode__())
    resp = {
        'max-24h-send': q.max24HourSend,
        'sent-last-24h': q.sentLast24Hours,
        'max-send-rate': q.maxSendRate,
    }
    return json_encode(resp)


@route('/statistics', method=['GET', 'POST'])
def statistic():
    try:
        s = ses.getSendStatistics()
    except AmazonError, e:
        return error_msg(e.__unicode__())
    resp = s.members
    return json_encode(resp)


@route('/verify', method=['GET', 'POST'])
def verify():
    try:
        v = ses.listVerifiedEmailAddresses()
    except AmazonError, e:
        return error_msg(e.__unicode__())
    return json_encode(v.members)


@route('/verify/add', method=['GET', 'POST'])
def verify():
    email = request.params.get('email', None)
    if not email:
        return error_msg('Missing field email')
    try:
        v = ses.verifyEmailAddress(email)
    except AmazonError, e:
        return error_msg(e.__unicode__())
    resp = {'status': 'ok', 'message': v.requestId,}
    return json_encode(resp)


@route('/verify/del', method=['GET', 'POST'])
def verify():
    email = request.params.get('email', None)
    if not email:
        return error_msg('Missing field email')
    try:
        v = ses.deleteVerifiedEmailAddress(email)
    except AmazonError, e:
        return error_msg(e.__unicode__())
    resp = {'status': 'ok', 'message': v.requestId,}
    return json_encode(resp)


def runserver(host, port):
    run(app=app, host=host, port=port, server='gevent')


if __name__ == '__main__':
    import os
    import sys
    from gevent.pool import Pool

    try:
        host, port = sys.argv[1:3]
    except:
        host, port = HOST, PORT
        print 'Host and Port not defined. Using defaults'
        print
    
    bottle_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'lib/')
    sys.path.append(bottle_path)

    p = Pool()
    p.spawn(runserver, host, port)
    p.spawn(logger)
    for i in range(WORKERS):
        p.spawn(worker, outbox, ses)
    try:
        p.join()
    except:
        # prevent loss of the message queue
        import time
        while not outbox.empty():
            try:
                print ' -- waiting for empty outbox. (%d mails remaining)' % outbox.qsize()
                time.sleep(1)
            except:
                continue

