#!/usr/bin/python
#
'''RSS1.0 to Hatena Diary XML filter.

usage: rss2hatena [date] < rss.rdf > hatena.xml
option:
    date: the end of range in whitch the diary is converted.
          unix time.
'''
#
# Copyright (c) 2005-2007 Satoshi Fukutomi <info@fuktommy.com>.
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

import re
import sys
from cgi import escape
from time import strftime, strptime, localtime, mktime
from xml.sax import parse, SAXParseException
from xml.sax.handler import ContentHandler

timezone = '+09:00'
timeformat = '%Y-%m-%dT%H:%M:%S' + timezone


class Item:
    '''RSS item'''

    def __init__(self, link='', title='', date='',
                 description='', content=''):
        self.link  = link
        self.date  = date
        self.title = title
        self.description = description
        self.content = content
        self.cached_unixtime = None

    def unixtime(self):
        if self.cached_unixtime is None:
            self.cached_unixtime = int(mktime(strptime(self.date, timeformat)))
        return self.cached_unixtime

# End of Item


class RSShandler(ContentHandler):
    elements = ['title', 'link', 'dc:date', 'description', 'content:encoded']

    def __init__(self):
        ContentHandler.__init__(self)
        self.items = []
        self.state = ''

    def startElement(self, name, attrs):
        if name == 'item':
            self.items.append(Item())
            self.state = 'item'
        elif (self.state == 'item') and (name in self.elements):
            self.state = name

    def endElement(self, name):
        if self.state and (name in self.elements):
            self.state = 'item'

    def characters(self, contents):
        contents = contents.encode('utf-8')
        if (not self.state) or (self.state == 'item'):
            pass
        elif self.state == 'title':
            self.items[-1].title += contents
        elif self.state == 'link':
            self.items[-1].link += contents
        elif self.state == 'dc:date':
            self.items[-1].date += contents
        elif self.state == 'description':
            self.items[-1].description += contents
        elif self.state == 'content:encoded':
            self.items[-1].content += contents

# End of RSShandler


class Day:
    '''One day diary.'''

    def __init__(self, item):
        self.date = strftime('%Y-%m-%d', localtime(item.unixtime()))
        body = item.content.strip().replace('\n', '\n ')
        self.body = '*%d* %s\n\n' % (item.unixtime(), item.title) + \
                    escape('>%s<\n\n' % body, True) + \
                    'Original Article: %s\n\n' % escape(item.link, True)

    def __str__(self):
        return self.body

# End of Day


def main():
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 0
    diary = {}
    handler = RSShandler()
    parse(sys.stdin, handler)
    for item in handler.items:
        if limit < item.unixtime():
            day = Day(item)
            diary[day.date] = diary.get(day.date, '') + str(day)
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<diary>'
    date = diary.keys()
    date.sort()
    for d in date:
        print '<day date="%s" title="">' % d
        print '<body>'
        print diary[d].rstrip()
        print '</body>'
        print '</day>'
    print '</diary>'

if __name__ == '__main__':
    main()
