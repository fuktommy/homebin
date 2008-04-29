#!/usr/bin/python
'''Accsess Log Parser for Search Query.

usage: parse-query log-files
'''
#
# Copyright (c) 2007 Satoshi Fukutomi <info@fuktommy.com>.
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
from cgi import escape
from fileinput import input
from urllib import unquote

count = {}
for line in input():
    found = re.search(r'(query|q)=([^&"]+)', line)
    if found:
        query = found.group(2)
        query = query.replace('+', ' ')
        query = unquote(query)
        query = re.sub(r'\s+', ' ', query)
        try:
            query = unicode(query, 'shift_jis')
        except UnicodeError:
            try:
                query = unicode(query, 'euc-jp')
            except UnicodeError:
                query = unicode(query, 'utf-8')
        count[query] = count.get(query,  0) + 1

keys = count.keys()
keys.sort(lambda a,b: -cmp(count[a], count[b]))
for k in keys:
    try:
        print '<tr><td>%s</td><td>%d</td></tr>' % (escape(k.encode('utf-8'), 'replace'), count[k])
    except UnicodeError:
        pass
