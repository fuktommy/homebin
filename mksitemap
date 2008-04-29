#!/usr/bin/python
#
"""Make Google sitemap (text format).

See http://www.google.com/webmasters/sitemaps/docs/en/other.html#text_file

usage: mksitemap parent-url directorys
example: mksitemap http://example.com/ /home/joe/public_html

"""
#
# Copyright (c) 2005 Satoshi Fukutomi <info@fuktommy.com>.
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
import sys
from urlparse import urljoin

def mksitemap(parent, dir):
    if not dir.endswith("/"):
        dir += "/"
    for root, dirs, files in os.walk(dir):
        root = root[len(dir):]
        for f in files:
            if f == "index.html":
                f = ""
            elif f.endswith(".html"):
                f = f[:-len(".html")]
            else:
                continue
            path = os.path.join(root, f)
            print urljoin(parent, path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: mksitemap parent-url dirs")
    parent = sys.argv[1]
    for i in sys.argv[2:]:
        mksitemap(parent, i)
