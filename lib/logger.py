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


