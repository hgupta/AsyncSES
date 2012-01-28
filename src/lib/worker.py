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


