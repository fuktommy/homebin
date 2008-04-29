#!/usr/bin/python
#
"""Tiny HTTP Daemon.

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

import BaseHTTPServer
import SimpleHTTPServer
import CGIHTTPServer
import SocketServer
import re
import os

class HTTPRequestHandler(CGIHTTPServer.CGIHTTPRequestHandler):
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Enable multiview.
        """
        path = CGIHTTPServer.CGIHTTPRequestHandler.translate_path(self, path)
        for suffix in ("", ".html", ".cgi", ".rdf", ".xml"):
            if os.path.exists(path + suffix):
                return path + suffix
        return path

    def is_cgi(self):
        """Test request URI is *.cgi."""
        path = self.path
        qi = path.find("?")
        if qi > 0:
            query = path[qi:]
            path = path[:qi]
        else:
            query = ""
        found = re.search(r"^(.*?)/([^/]+\.cgi.*)", path)
        if found:
            self.cgi_info = found.group(1), found.group(2)+query
            return True
        elif path.endswith("/") and \
             os.path.exists(os.path.join(os.getcwd(),
                                         path[1:],
                                         "index.cgi")):
            self.cgi_info = path[:-1], "index.cgi"+query
            return True
        else:
            return False

    def run_cgi(self):
        """Execute a CGI script."""
        ref = self.headers.getheader('referer')
        if ref:
            os.environ['HTTP_REFERER'] = ref
        elif 'HTTP_REFERER' in os.environ:
            del os.environ['HTTP_REFERER']
        CGIHTTPServer.CGIHTTPRequestHandler.run_cgi(self)


    def send_head(self):
        """Common code for GET and HEAD commands."""
        path = self.translate_path(self.path)
        if self.is_cgi():
            return self.run_cgi()
        else:
            qi = self.path.find("?")
            if qi > 0:
                self.path = self.path[:qi]
            return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)


HTTPRequestHandler.extensions_map.update({
    '': 'text/plain', # Default
    '.py': 'text/plain',
    '.rdf': 'text/xml',
    '.xsl': 'text/xml',
    })

class HTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

def test():
    try:
        BaseHTTPServer.test(HTTPRequestHandler, HTTPServer)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    test()
