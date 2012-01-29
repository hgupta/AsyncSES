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

from datetime import datetime
from lib.amazon_ses import AmazonSES, EmailMessage

def sendmail(data, ses=None, callback=None, debug=False):

    assert isinstance(data, dict), u'`data` must be dict'
    assert isinstance(ses, AmazonSES), u'`ses` must be AmazonSES instance'
    
    msg = EmailMessage()
    msg.subject = data.get('subject', None)
    msg.bodyText = data.get('text', None)
    msg.bodyHtml = data.get('html', None)
    
    from_email = data.get('from', None)
    to_email = data.get('to', None)
    return_path = data.get('return_path', None)
    reply_to = data.get('reply_to', None)
    cc_email = data.get('cc', None)
    bcc_email = data.get('bcc', None)
    headers = data.get('headers', {})
    
    result = ses.sendEmail(source=from_email, toAddresses=to_email, message=msg,
             replyToAddresses=reply_to, returnPath=return_path, ccAddresses=cc_email,
             bccAddresses=bcc_email, headers=headers)

    response = result.__dict__
    response['to'] = to_email
    response['from'] = from_email
    response['date'] = str(datetime.now())
    
    if callback:
        callback(response)
    
    return response

