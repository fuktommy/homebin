#!/usr/bin/python
"""Make RSS for file list.

It requires rss.py by Fuktommy.

Synopsis:
    mkrss.py [/path/to/html/dir] > rss.xml
    mkrss.py -b /path/to/html/dir file_list > rss.xml
    find /path/to/html/dir -type f | \
        mkrss.py -b /path/to/html/dir > rss.xml

Options:
    -h header_file: File includes title for RSS.

It generates RSS for file, if file.txt exist or file is a HTML.
If file is HTML, it use <title> tag and <meta name="description"...> tag
and use <!-- $Id: ... $ --> comment for timestamp.

Header file:
    version: 1.0/2.0        # version of RSS
    parent: URI             # URI of parent of documents
    uri: URI                # URI of RSS
    link: URI               # URI of main page
    title: string           # title of RSS
    description: string     # description of RSS

Text file:
    Top line is the title.
    $Id: ... $ line is the timestamp.
    Following line is description.
"""

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

import HTMLParser
import fileinput
import os
import sys
import re
import time

import rss      # module written by Fuktommy

#
# Configuration
#

rss_version = "1.0"
encode = "utf-8"
parent_uri = "http://example.com/files/"
link = parent_uri
rss_uri = parent_uri + "rss.xml"
title = "Files"
description = "My Files"
xsl = ""
header_file = ""

os.environ['TZ'] = 'UTC'
time.tzset()

def read_header(f):
    """Read header file.

    version: 1.0/2.0        # version of RSS
    parent: URI             # URI of parent of documents
    uri: URI                # URI of RSS
    link: URI               # URI of main page
    title: string           # title of RSS
    description: string     # description of RSS
    xsl: path               # PATH or URI of XSL
    """

    global rss_version, parent_uri, rss_uri, link, title, description, xsl
    re_iscomment = re.compile(r"^\s*#")
    re_keyval = re.compile(r"\s*:\s*")
    del_space = re.compile(r"^\s*")
    del_eof = re.compile(r'[\r\n]*')
    last = ""
    conf = {}
    for line in file(f):
        if line == "\n":
            continue
        elif re_iscomment.search(line):
            continue
        line = del_space.sub("", line)
        line = del_eof.sub("", line)
        try:
            (key, val) = re_keyval.split(line, 1)
            conf[key]  = val
            last = key
        except ValueError:
            conf[last] += line
    for key in conf:
        if key == "version":
            rss_version =conf[key]
        elif key == "parent":
            parent_uri = conf[key]
        elif key == "uri":
            rss_uri = conf[key]
        elif key == "link":
            link = conf[key]
        elif key == "title":
            title = conf[key]
        elif key == "description":
            description = conf[key]
        elif key == "xsl":
            xsl = conf[key]

def read_text(f):
    """Read from text file.

    Top line is the title.
    Following line is description.
    """

    txt = file(f + ".txt")
    title = txt.readline()
    desc = ''
    date = None
    for line in txt:
        found = re.search(
            '\$Id: \S+ \d+ (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z) .*\$', line)
        if found:
            try:
                date = time.strptime(found.group(1), '%Y-%m-%d %H:%M:%SZ')
                date = time.mktime(date)
            except ValueError:
                sys.stderr.write('Id parse error in %s.txt\n' % f)
        else:
            desc += line
    txt.close()
    return (title, desc, date)

class HtmlReader(HTMLParser.HTMLParser):
    """Read from HTML.

    Use <title> tag and <meta name="description"...> tag.
    """

    attrs = {}
    now = ""
    encode = ""
    re_xmlencode = re.compile(r"xml.*encoding=.([^<>\"']+)..*\?$")
    re_htmlencode = re.compile(r"charset=([^<>\"'/]+)")
    del_space = re.compile(r"^\s*|\s*$")

    def __init__(self):
        """Constructor."""

        HTMLParser.HTMLParser.__init__(self)
        self.attrs = {"title": "", "description": "", "date": None}
        self.now = ""
        self.encode = encode

    def dic_attr(self, attrs):
        """Convert attrs list to dictionary."""

        da = {}
        for i in attrs:
            da[i[0]] = i[1]
        return da

    def handle_starttag(self, tag, attrs):
        """Overwrite method."""

        attrs = self.dic_attr(attrs)
        if tag == "title":
            self.now = "title"
        elif tag == "meta" \
            and "name" in attrs \
            and "content" in attrs \
            and attrs["name"] == "description":
            self.attrs["description"] = attrs["content"]
        elif tag == "meta" \
            and "http-equiv" in attrs \
            and "content" in attrs\
            and attrs["http-equiv"].lower() == "content-type":
            htmlencode = self.re_htmlencode.search(attrs["content"])
            self.encode = htmlencode.group(1)
        else:
            self.now = ""

    def handle_data(self, data):
        """Overwrite method."""
        if self.now:
            self.attrs[self.now] += data

    def handle_comment(self, data):
        found = re.search(
            '\$Id: \S+ \d+ (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z) .*\$', data)
        if found:
            try:
                date = time.strptime(found.group(1), '%Y-%m-%d %H:%M:%SZ')
                self.attrs['date'] = time.mktime(date)
            except ValueError:
                sys.stderr.write('Id parse error in %s.txt\n' % f)

    def handle_pi(self, data):
        """Overwrite method."""
        xmlencode = self.re_xmlencode.search(data)
        if xmlencode:
            self.encode = xmlencode.group(1)

    def getData(self):
        """Return title and description."""

        for k in ("title", "description"):
            data = unicode(self.attrs[k], self.encode).encode(encode)
            self.attrs[k] = self.del_space.sub("", data, 0)
        return (self.attrs["title"], self.attrs["description"], self.attrs["date"])

def read_html(f):
    """Read from HTML.

    Wrapper of HtmlReader.
    """
    html = file(f)
    parser = HtmlReader()
    parser.feed(html.read())
    (title, description, date) = parser.getData()
    parser.close()
    return(title, description, date)

def findfiles(dir):
    """Search directorys for files.

    It works lile ``find dir -type f''.
    """

    files = []
    buf = []
    for f in os.listdir(dir):
        buf.append(dir + "/" + f)

    while len(buf) > 0:
        f = buf.pop(0)
        if os.path.islink(f):
            pass
        elif os.path.isdir(f):
            for g in os.listdir(f):
                buf.append(f + "/" + g)
        elif os.path.isfile(f):
            files.append(f)

    return files

#
# main
#

#
# make list of files
#

dir = ""
files = []
lists = []
mode = "self_find"    # self_find / given_list
sys.argv.pop(0)
while (sys.argv):
    i = sys.argv.pop(0)
    if i == "-b":
        mode = "given_list"
        dir  = sys.argv.pop(0)
    elif i == "-h":
        read_header(sys.argv.pop(0))
    else:
        lists.append(i)

if mode == "self_find" and len(lists) == 1:
    dir = lists[0]
    files = findfiles(dir)
elif mode == "self_find" and len(lists) == 0:
    dir = "."
    files = findfiles(dir)
elif mode == "given_list":
    for line in fileinput.input():
        files.append(*line.splitlines())

#
# Generate RSS
#

list = rss.RSS(encode=encode, title=title,
        parent=parent_uri, uri=rss_uri, link=link,
        description=description, xsl=xsl)

ishtml = re.compile(r"\.html$")
del_index = re.compile(r"index\.html$")
for f in files:
    fullname = f
    date = None
    title = ""
    desc = ""

    if os.path.isfile(f + ".txt"):
        title, desc, date = read_text(f)
    elif ishtml.search(f):
        title, desc, date = read_html(f)
        f = del_index.sub("", f)
        f = ishtml.sub("", f)
    if date is None:
        #date = os.path.getmtime(fullname)
        date = 0
    if title:
        f = f[len(dir)+1:]
        list.append(f, title=title, date=date, description=desc)

if rss_version == "1.0":
    sys.stdout.write(rss.make_rss1(list))
elif rss_version == "2.0":
    sys.stdout.write(rss.make_rss2(list))
