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

import itertools
from traceback import format_exc
from lib.sendmail import sendmail
from lib.logger import log

# Thread-safe counter
sent = itertools.count()
error = itertools.count()

def worker(outbox, ses):
    while True:
        data = outbox.get()
        try:
            response = sendmail(data=data, ses=ses, callback=log)
            sent.next()
        except:
            error.next()
            msg = '-'*80
            msg += '\n%s\n' % format_exc()
            msg += str(data)
            msg += '\n'
            msg += '-'*80
            log(msg)


