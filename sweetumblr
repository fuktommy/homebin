#!/usr/bin/python
'''Download images from sweetumblr.
'''
#
# Copyright (c) 2008 Satoshi Fukutomi <info@fuktommy.com>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import os
import re
import urllib
from gzip import GzipFile
from StringIO import StringIO
from urlparse import urlparse

class MyAgent(urllib.FancyURLopener):
    def __init__(self):
        self.version = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
        urllib.FancyURLopener.__init__(self, proxies={})
        self.addheader('Accept-Encoding',
                       'gzip, compres, bzip, bzip2, deflate')
        self.addheader('Accept-Language', 'ja; q=1.0, en;q=0.5')
agent = MyAgent()

wget = ['wget', '--random-wait', '-nv', '-nc',
    '--header=Accept-Encoding: gzip, compres, bzip, bzip2, deflate',
    '--header=Accept-Language: ja; q=1.0, en;q=0.5',
    '-U', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    '-w', '6']

rssurl = 'http://mashimaro.tumblr.com/rss'

os.chdir(os.path.expanduser('~/fuk/img/sweetumblr'))

rss = agent.open(rssurl).read()
try:
    rss = GzipFile(fileobj=StringIO(rss)).read()
except IOError:
    pass

images = []
for img in re.findall('img src="(.*?)"', rss):
    images.append(img)

os.spawnvp(os.P_WAIT, 'wget', wget+images)
