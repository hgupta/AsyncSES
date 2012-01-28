# Debug mode (bottle will expose tracebacks on error requests)
DEBUG = True

# Amazon ID and Secret
AMAZON_KEY = 'INSERT YOUR AMAZON SES KEY HERE'
AMAZON_SECRET = 'INSERT YOUR AMAZON SES SECRET HERE'

# Server config
HOST = '0.0.0.0'
PORT = '3000'

# Simultaneous workers to send email to Amazon SES.
# Low cpu and memory usage for each worker.
WORKERS = 1000

# Maximum size of outbox (number of messages allowed to be waiting in queue)
# Remember that many messages in outbox will cause too much memory be consumed
# To fix this, increase the number of workers and reduce the outbox size,
# then all messages can be sent faster and outbox size will decrease.
OUTBOX_MAXSIZE = 1000000

