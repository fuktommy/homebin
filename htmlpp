#!/usr/bin/python
#
"""HTMLPP - Generate HTML like as CPP.

Synopsis: htmlpp [-f] [-n] [-I dir]... foo.txt...

This script generates foo.html when foo.txt is newer than it.

Options:
    -f: force genarate
    -n: do not validate html
    -I dir: specify include dir (for template files)

Example:
    htmlpp index.txt
    htmlpp -f -n index.txt

Contents of file:
    >command arguments
    HTML

Commands:
    >include "filename" [``localvars'']
    >define var value
    >undef var
    >if exp
    >ifdef var
    >ifndef var
    >else [//comment]
    >endif [//comment]
    >csvtable "filename" [[start]..[end]] [``escape'']
    >textpre "filename"
    ># comment_string

<$NAME> in HTML is a variable.

``>>>command'' is same as ``>command''.
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

import csv
import os
import re
import sys
import cgi
import xml.dom.minidom
import xml.parsers.expat

#
# Configuration
#

include_dir = ['.', './template', '../template'] # path to templates

csv_cache = {}

class HTML:
    """Partial HTML."""

    def __init__(self, txt, incdir=[], var={}, loop=[]):
        """Create partial HTML with text file."""
        self.txt = txt
        self.var = {}
        self.var.update(var)
        self.loop = loop[:]
        self.incdir = [os.path.dirname(txt)] + incdir

    def eval_var(self, line):
        """Eval var in HTML.

        <$NAME> in HTML is a variable.
        """
        re_var = re.compile(r"<\$([A-Za-z_][A-Za-z_0-9]*)>")
        m_var = re_var.search(line)

        if m_var is None:
            return line
        else:
            var = m_var.group(1)
            buf = line[:m_var.start()]
            buf += self.var.get(var, "")
            buf += self.eval_var(line[m_var.end():])
            return buf

    def eval_exp(self, exp):
        """Eval exp.

        Exp:
            operand
            operand[0] operator operand[1]

        operand: integer or string

        operator: ==, !=, <, >, <=, or >=
        """
        re_var = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)$")
        re_quote = re.compile(r"^['\"](.*)['\"]$")
        re_isint = re.compile(r"^[-+]?\d+$")
        m_exp = re.search(r"(\S+)\s*([=!<>]+)\s*(\S+)", exp)
        m_var = re_var.search(exp)

        if m_var is not None:
            var = m_var.group(1)
            return (var in self.var) and \
                   (self.var[var] != "0") and \
                   (self.var[var] != "")
        elif re_quote.search(exp):
            return exp != '""'
        elif re_isint.search(exp):
            return int(exp) != 0
        elif m_exp is None:
            sys.exit("syntax error(exp)\n")

        operand = ["", ""]
        operand[0], operator, operand[1] = m_exp.groups()

        isint = [False, False]
        for i in (0, 1):
            quote = re_quote.search(operand[i])
            if quote is not None:
                operand[i] = quote.group(1)
            elif re_var.search(operand[i]):
                if (operand[i] in self.var):
                    operand[i] = self.var[operand[i]]
                else:
                    operand[i] = "0"
                if re_isint.search(operand[i]):
                    isint[i] = True
            elif re_isint.search(operand[i]):
                isint[i] = True
            else:
                sys.exit("syntax error(exp): %s\n" % exp)

        if isint[0] and isint[1]:
            operand[0] = int(operand[0])
            operand[1] = int(operand[1])

        if operator == "==":
            return operand[0] == operand[1]
        elif operator == "!=":
            return operand[0] != operand[1]
        elif operator == "<":
            return operand[0] < operand[1]
        elif operator == ">":
            return operand[0] > operand[1]
        elif operator == "<=":
            return operand[0] <= operand[1]
        elif operator == ">=":
            return operand[0] >= operand[1]

    def do_include(self, fileobj, arg):
        """Include header file(template)."""
        quote = re.search(r"^['\"<](.*)['\">]", arg)
        if quote is not None:
            header = self.header_file(quote.group(1))
            if header:
                html = HTML(header,
                            incdir=self.incdir, var=self.var, loop=self.loop)
                return html
            else:
                sys.exit('%s: file not found' % quote.group(1))
        else:
            sys.exit("syntax error(include)")

    def do_define(self, arg):
        """Define variable."""
        exp = re.search(r"^([A-Za-z_][A-Za-z_0-9]*)\s+(.*)", arg)
        if exp is not None:
            buf = self.eval_var(exp.group(2))
            self.var[exp.group(1)] = buf
        else:
            sys.exit("syntax error(define)\n")

    def do_undef(self, arg):
        """Undefine variable."""
        exp = re.search(r"^([A-Za-z_][A-Za-z_0-9]*)", arg)
        if exp is not None:
            try:
                del self.var[exp.group(1)]
            except KeyError:
                pass
        else:
            sys.exit("syntax error(define)\n")

    def do_if(self, fileobj, arg, mode=""):
        """If state.

        >if exp
        >ifdef var
        >ifndef var
        >else
        >endif
        """
        buf = ""
        flag = False

        if mode == "if":
            flag = self.eval_exp(arg)
        elif mode == "ifdef":
            flag = arg in self.var
        elif mode == "ifndef":
            flag = not arg in self.var
        else:
            sys.exit("syntax error(exp): " + mode + "\n")

        if flag:
            return self.read(fileobj, ignore=False)
        else:
            return self.read(fileobj, ignore=True)
        return (buf, hpvars)

    def do_csvtable(self, arg):
        """Convert CSV to HTML table.

        >csvtable "filename" [[start]..[end]] [``escape'']
        >csvtable "filename" row_index [``escape'']
        """
        m_quote = re.search(r"^[\"'<](.*)[\"'>]\s*", arg)
        rows = []
        if m_quote is None:
            sys.exit("syntax error(csvtable)\n")
        else:
            name = self.header_file(m_quote.group(1), False)
            if name in csv_cache:
                rows = csv_cache[name]
            else:
                for row in csv.reader(file(name)):
                    rows.append(row)
                csv_cache[name] = rows

        ran = [0, None]
        m_range = re.search(r"([^.\s]*)\.\.([^.\s]*)", arg[m_quote.end():])
        m_index = re.search(r"([^.\s]*)", arg[m_quote.end():])
        re_isint = re.compile(r"^[-+]?\d+$")

        tmp = []
        if m_range is not None:
            tmp = m_range.groups()
        elif m_index is not None:
            tmp = (m_index.group(1), m_index.group(1))

        if tmp:
            for i in (0, 1):
                if tmp[i] == "":
                    pass
                elif re_isint.search(tmp[i]):
                    ran[i] = int(tmp[i])
                elif (tmp[i] in self.var) and \
                     re_isint.search(self.var[tmp[i]]):
                    ran[i] = int(self.var[tmp[i]])

        (start, end) = ran
        if (start != 0) and (end is not None):
            rows = rows[start-1:end]
        elif start != 0:
            rows = rows[start-1:]
        elif end is not None:
            rows = rows[0:end]

        escape = False
        if re.search(r"(.*\.\.\S*)?\s*escape", arg[m_quote.end():]):
            escape = True

        buf = ""
        for i in rows:
            buf += "  <tr>\n"
            for j in i:
                if escape:
                    j = cgi.escape(j).replace("\n", "<br />")
                buf += "    <td>%s</td>\n" % j
            buf += "  </tr>\n"
        return buf

    def do_textpre(self, arg):
        """Convert text to HTML <pre>...</pre>.

        >textpre "filename"
        """
        m_quote = re.search(r"^[\"'<](.*)[\"'>]\s*", arg)
        rows = []
        if m_quote is None:
            sys.exit("syntax error(textpre)\n")
        else:
            name = self.header_file(m_quote.group(1), False)

        buf = ""
        text = file(name)
        for i in text:
            buf += cgi.escape(i)
        buf = re.sub(r"[\r\n]*$", "", buf)
        return "<pre>%s</pre>\n" % buf

    def read(self, fileobj, ignore=False):
        """Read text of header file(template).

        Synopsis:
            >command arguments
            HTML

        Commands:
            >include "filename" [``localvars'']
            >define var value
            >undef var
            >if exp
            >ifdef var
            >ifndef var
            >else [//comment]
            >endif [//comment]
            >csvtable "filename" [[start]..[end]] [``escape'']
            >textpre "filename"
            ># comment_string

        <$NAME> in HTML is a variable.
        """
        buf = ""
        re_command = re.compile(r"^>+([a-z#]+)\s+(.*)[\r\n]*$")
        for line in fileobj:
            command = re_command.search(line)
            if command is None:
                if not ignore:
                    buf += self.eval_var(line)
            else:
                cmd, arg = command.groups()
                if cmd == "endif":
                    break
                elif ignore and (cmd == "else"):
                    ignore = False
                elif ignore:
                    if cmd in ('if', 'ifdef', 'ifndef'):
                        self.do_if(fileobj, arg, mode=cmd)
                elif cmd == "else":
                    ignore = True
                elif cmd == "include":
                    html = self.do_include(fileobj, arg)
                    buf += html.read_file()
                    if not re.search("^['\"<](.*)['\">].*localvars", arg):
                        self.var = html.var
                elif cmd == "define":
                    self.do_define(arg)
                elif cmd == "undef":
                    self.do_undef(arg)
                elif cmd == "if":
                    buf += self.do_if(fileobj, arg, mode="if")
                elif cmd == "ifdef":
                    buf += self.do_if(fileobj, arg, mode="ifdef")
                elif cmd == "ifndef":
                    buf += self.do_if(fileobj, arg, mode="ifndef")
                elif cmd == "csvtable":
                    buf += self.do_csvtable(arg)
                elif cmd == "textpre":
                    buf += self.do_textpre(arg)
                elif cmd == "#":
                    pass
                else:
                    sys.exit("syntax error(command)\n")
        else:
            fileobj.close()

        return buf

    def read_file(self):
        return self.read(file(self.txt))

    def header_file(self, head, check_loop=True):
        """Search header file (template).

        Header file is in include_dir.
        Stop when loop reference or do not exist header file.
        """
        path = ""
        for i in self.incdir:
            i = os.path.join(i, head)
            if os.path.isfile(i):
                path = i
                break

        if path == "":
            sys.exit(" %s: not found\n" % head)
        elif check_loop and (path in self.loop):
            print ' %s: loop' % path
            return ''
        else:
            self.loop += [path]
            return path

# End of HTML


def generate_html(txt, html, incdir, force=False):
    """Generate HTML from txt."""
    date_txt = os.path.getmtime(txt)
    date_html = 0
    if os.path.isfile(html):
        date_html = os.path.getmtime(html)
    if (not force) and (date_txt < date_html):
        return None

    parthtml = HTML(txt, incdir=incdir)
    htmldata = parthtml.read_file()

    f_html = file(html, "w")
    f_html.write(htmldata)
    f_html.close()
    #os.utime(html, (date_txt+1, date_txt+1))
    return htmldata


def validate(htmldata):
    '''Validate HTML.

    Now it only checks valid XML or not.
    '''
    try:
        found = re.search(r'^\s*<\?xml[^<>]*\?>', htmldata)
        if found:
            xmlhead = htmldata[:found.end()]
            xmlbody = htmldata[found.end():]
            found = re.search(r'encoding=["\'](.*?)["\']', xmlhead)
            if found:
                encoding = found.group(1)
                xmlhead = '%sencoding="%s"%s' % \
                            (xmlhead[:found.start()],
                             'utf-8',
                             xmlhead[found.end():])
                xmlbody = unicode(xmlbody, encoding).encode('utf-8')
            htmldata = xmlhead + xmlbody
        xml.dom.minidom.parseString(htmldata)
        return True
    except (xml.parsers.expat.ExpatError, UnicodeDecodeError, LookupError), e:
        print e
        return False


def main():
    txtfile = []
    flag_force = False
    flag_validate = True
    sys.argv.pop(0)
    idir = []
    cdir = []
    hlopt = []
    while len(sys.argv) > 0:
        i = sys.argv.pop(0)
        if i == "--":
            txtfile += sys.argv
        elif i == "-I":
            idir.append(sys.argv.pop(0))
        elif i == "-f":
            flag_force = True
        elif i == "-n":
            flag_validate = False
        else:
            txtfile.append(i)
    incdir = idir + include_dir

    if len(txtfile) == 0:
        sys.exit("htmlpp [-f] [-n] [-I dir]... foo.txt...")

    for txt in txtfile:
        html = re.sub(r"\.[^.]*$", ".html", txt)
        htmldata = generate_html(txt, html, incdir, force=flag_force)
        if htmldata is not None:
            print '%s:' % txt,
            if not flag_validate:
                print 'pass'
            elif validate(htmldata):
                print 'OK'
            else:
                print 'stop'
                sys.exit(1)
                
if __name__ == "__main__":
    main()
