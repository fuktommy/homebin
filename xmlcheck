#!/usr/bin/python
#
'''XML Checker.

Try parsing XML.

Synopsis: xmlcheck foo.xml...
'''
#
# Copyright (c) 2006 Satoshi Fukutomi <info@fuktommy.com>.
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
import xml.dom.minidom
import xml.parsers.expat

def validate(xmlfile):
    '''Validate XML.

    Now it only checks valid XML or not.
    '''
    xmldata = file(xmlfile).read()
    try:
        found = re.search(r'^\s*<\?xml[^<>]*\?>', xmldata)
        if found:
            xmlhead = xmldata[:found.end()]
            xmlbody = xmldata[found.end():]
            found = re.search(r'encoding=["\'](.*?)["\']', xmlhead)
            if found:
                encoding = found.group(1)
                xmlhead = '%sencoding="%s"%s' % \
                            (xmlhead[:found.start()],
                             'utf-8',
                             xmlhead[found.end():])
                xmlbody = unicode(xmlbody, encoding).encode('utf-8')
            xmldata = xmlhead + xmlbody
        xml.dom.minidom.parseString(xmldata)
        return True
    except (xml.parsers.expat.ExpatError, UnicodeDecodeError, LookupError), e:
        print '%s: %s' % (xmlfile, e)
        return False


def main():
    if len(sys.argv) <= 1:
        sys.exit('usage xmlcheck foo.xml...')
    for i in sys.argv[1:]:
        validate(i)


if __name__ == "__main__":
    main()
