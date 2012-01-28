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

