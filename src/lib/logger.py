from gevent.queue import Queue

import os
PATH = 'logs/'
if not os.path.exists(PATH):
    os.makedirs(PATH)

LOGFILE = os.path.join(PATH, 'worker.log')

logs = Queue()

def timestamp():
    from datetime import datetime
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def log(msg):
    if not isinstance(msg, basestring):
        if hasattr(msg, '__unicode__'):
            msg = msg.__unicode__()
        elif hasattr(msg, '__str__'):
            msg = msg.__str__()
        else:
            try:
                msg = str(msg)
            except:
                msg = 'I don\'t know how to manage this  msg type: %s' % msg.__class__

    if not msg.endswith('\n'):
        msg += '\n'
    msg = '[%s] %s' % (timestamp(), msg)
    logs.put(msg)
    return True


def logger():
    with open(LOGFILE, 'a') as f:
        start_msg = '\n\n%s\nLogger started at %s\n\n' % ('-'*80, timestamp())
        f.write(start_msg)
        f.flush()
        i=0
        while True:
            msg = logs.get()
            i += 1
            f.write(msg)
            if i%10 == 0:
                f.flush()


