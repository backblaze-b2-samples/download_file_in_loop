#!/usr/bin/env python

'''
Backblaze wants developers and organization to copy and re-use our
code examples, so we make the samples available by several different
licenses.  One option is the MIT license (below).  Other options are
available here:

    https://www.backblaze.com/using_b2_code.html


The MIT License (MIT)

Copyright (c) 2020 Backblaze

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import sys
import datetime
from b2_connector import B2Connector

if (len(sys.argv) < 4 or len(sys.argv) > 4):
    print('Usage: start.py '
          '[filepath] '
          '[Sha1] '
          '[num of requests]')
    exit()

filepath  = sys.argv[1]
sha1_hash = sys.argv[2]
loops     = int(sys.argv[3])

# Instantiate B2 connector
b2 = B2Connector()

now = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

print('[%s]: Starting downloads, %s times' % (now, str(loops)))

for x in range(loops):
    result = b2.download_file_by_name(filepath, sha1_hash, str(x))

now = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
print('[%s]: End' % now)