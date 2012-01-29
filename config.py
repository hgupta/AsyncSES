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

# Amazon ID and Secret
AMAZON_KEY = 'INSERT YOUR AMAZON SES KEY HERE'
AMAZON_SECRET = 'INSERT YOUR AMAZON SES SECRET HERE'

# Server config
HOST = '0.0.0.0'
PORT = '3000'

# Simultaneous workers to send email to Amazon SES.
# Low cpu and memory usage for each worker.
WORKERS = 100

# Maximum size of outbox (number of messages allowed to be waiting in queue)
# Remember that many messages in outbox will cause too much memory be consumed
# To fix this, increase the number of workers and reduce the outbox size,
# then all messages can be sent faster and outbox size will decrease.
OUTBOX_MAXSIZE = 1000000

