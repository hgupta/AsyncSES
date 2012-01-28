import cjson
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
    return cjson.encode(data)


@route('/status')
@route('/status/')
def index():
    getvalue = lambda x: str(x.__reduce__()[1][0])
    sent_qtd = getvalue(sent)
    error_qtd = getvalue(error)
    queued_qtd = getvalue(queued)
    rejected_qtd = getvalue(rejected)
    msg = u'Queued: %s\nRejected: %s\nSent: %s\nError: %s\n' % \
          (queued_qtd, rejected_qtd, sent_qtd, error_qtd)
    return msg.replace('\n', '<br/>')


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
            headers = cjson.decode(headers)
            data['headers'] = headers
        except:
            return error_msg('headers contains invalid json data')

    for field in REQUIRED_FIELDS:
        if not (data.has_key(field) and data[field]):
            return error_msg('missing field %s'%field)

    outbox.put(data)
    queued.next()
    resp = {'status': 'queued', 'message': 'ok',}

    return cjson.encode(resp)


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

