try:
    import cjson
    json_encode = cjson.encode
    json_decode = cjson.decode
except ImportError:
    from json import loads as json_decode, dumps as json_encode

import itertools
from lib.bottle import default_app, run, route, request
from lib.amazon_ses import AmazonSES
from lib.outbox import Outbox
from lib.worker import worker, sent, error
from lib.logger import logger
from config import *

if DEBUG:
    from lib import bottle
    bottle.DEBUG = True

REQUIRED_FIELDS = ['from', 'to', 'subject', 'text']
outbox = Outbox(maxsize=OUTBOX_MAXSIZE)
ses = AmazonSES(AMAZON_KEY, AMAZON_SECRET)
app = default_app()

# Thread-safe counters
queued = itertools.count()
rejected = itertools.count()

def error_msg(msg):
    data = {'status': 'error', 'message': msg}
    rejected.next()
    return json_encode(data)


@route('/add', method=['GET', 'POST'])
@route('/add/', method=['GET', 'POST'])
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
            return error_msg('headers contains invalid json data')

    for field in REQUIRED_FIELDS:
        if not (data.has_key(field) and data[field]):
            return error_msg('missing field %s'%field)

    outbox.put(data)
    queued.next()
    resp = {'status': 'queued', 'message': 'ok',}

    return json_encode(resp)


@route('/status')
@route('/status/')
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


@route('/quota')
@route('/quota/')
def quota():
    q = ses.getSendQuota()
    resp = {
        'max-24h-send': q.max24HourSend,
        'sent-last-24h': q.sentLast24Hours,
        'max-send-rate': q.maxSendRate,
    }
    return json_encode(resp)


@route('/statistics')
@route('/statistics/')
def statistic():
    s = ses.getSendStatistics()
    resp = s.members
    return json_encode(resp)


@route('/verify')
@route('/verify/')
def verify():
    v = ses.listVerifiedEmailAddresses()
    return json_encode(v.members)


@route('/verify/add')
@route('/verify/add/')
def verify():
    email = request.params.get('email', None)
    if not email:
        return error_msg('Missing field email')
    v = ses.verifyEmailAddress(email)
    resp = {'status': 'ok', 'message': v.requestId,}
    return json_encode(resp)


@route('/verify/del')
@route('/verify/del/')
def verify():
    email = request.params.get('email', None)
    if not email:
        return error_msg('Missing field email')
    v = ses.deleteVerifiedEmailAddress(email)
    resp = {'status': 'ok', 'message': v.requestId,}
    return json_encode(resp)


def runserver(host, port):
    run(app=app, host=host, port=port, server='gevent')


if __name__ == '__main__':
    import sys
    from gevent.pool import Pool

    try:
        host, port = sys.argv[1:3]
    except:
        host, port = HOST, PORT
        print 'Host and Port not defined. Using defaults'
        print
    
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

