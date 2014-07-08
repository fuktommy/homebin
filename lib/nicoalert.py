#!/usr/bin/python3
"""NicoNicoAlert Clone.

http://dic.nicovideo.jp/a/%E3%83%8B%E3%82%B3%E7%94%9F%E3%82%A2%E3%83%A9%E3%83%BC%E3%83%88%28%E6%9C%AC%E5%AE%B6%29%E3%81%AE%E4%BB%95%E6%A7%98
"""
#
# Copyright (c) 2009,2014 Satoshi Fukutomi <info@fuktommy.com>.
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

import json
import re
import socket
import urllib.parse
import urllib.request
import xml.etree.ElementTree

__all__ = ['AlertLoginInfo', 'NicoAlert', 'Subscription']

NICO_LOGIN_URL = 'https://secure.nicovideo.jp/secure/login?site=nicoalert';
ALERT_LOGIN_URL = 'http://api.alert.nicovideo.jp/v2/login'
SUBSCRIPTIONS_URL = 'http://api.alert.nicovideo.jp/v2/subscriptions'
USER_AGENT = 'https://github.com/fuktommy/homebin/blob/master/lib/nicoalert.py'


class AlertLoginInfo:
    user_id = 0
    ticket = ''
    address = ''
    port = 2525


class Subscription:
    thread_id = 0
    service = ''
    provider_type = ''
    user_id = '0'
    community_id = ''


class WebApi:
    def login_account(self, mail, password):
        """Login niconico account and return ticket string.
        """
        params = {'mail': mail, 'password': password}
        headers = {'User-Agent': USER_AGENT}
        post_data = urllib.parse.urlencode(params).encode('utf-8')
        request = urllib.request.Request(NICO_LOGIN_URL, post_data, headers)
        response = urllib.request.urlopen(request)
        login_xml = xml.etree.ElementTree.fromstring(response.read())
        ticket = login_xml.find('./ticket').text
        return ticket

    def login_alert(self, ticket):
        """Login alert server and return AlertLoginInfo.
        """
        params = {'firstRun': '1', 'ticket': ticket}
        headers = {'User-Agent': USER_AGENT}
        post_data = urllib.parse.urlencode(params).encode('utf-8')
        request = urllib.request.Request(ALERT_LOGIN_URL, post_data, headers)
        response = urllib.request.urlopen(request)
        login_xml = xml.etree.ElementTree.fromstring(response.read())
        login_info = AlertLoginInfo()
        login_info.user_id = int(login_xml.find('./userId').text)
        login_info.ticket = login_xml.find('./ticket').text
        login_info.address = login_xml.find('./server/address').text
        login_info.port = int(login_xml.find('./server/port').text)
        return login_info

    def get_subscriptions(self, user_id, ticket):
        params = {'userId': user_id, 'ticket': ticket}
        headers = {'User-Agent': USER_AGENT}
        get_data = urllib.parse.urlencode(params)
        url = SUBSCRIPTIONS_URL + '?' + get_data
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        subscriptions_xml = xml.etree.ElementTree.fromstring(response.read())
        subscriptions = []
        for element in subscriptions_xml.findall('./subscription'):
            sub = Subscription()
            sub.thread_id = int(element.attrib['threadId'])
            sub.service = element.find('./service').text
            sub.provider_type = self._element_text(element, './providerType')
            sub.user_id = self._element_text(element, './userId')
            sub.community_id = self._element_text(element, './communityId')
            subscriptions.append(sub)
        return subscriptions

    def _element_text(self, element, xpath):
        value = element.find(xpath)
        if value is not None:
            return value.text
        else:
            return ''


class CommentServerApi:
    _socket = None
    _processing = False

    def close(self):
        self.processing = False
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None

    def connect(self, address, port):
        self.processing = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(120)
        self.socket.connect((address, port))

    def join_thread(self, thread_id):
        msg = (('<thread thread="%d"'
               + ' version="20061206" res_from="0" scores="1"'
               + '/>\0')
               % thread_id)
        self.socket.sendall(msg.encode('utf-8'))

    def __iter__(self):
        buf = ''
        while self.processing:
            try:
                buf += self.socket.recv(1024).decode('utf-8', 'replace')
            except socket.timeout:
                continue
            while True:
                found = re.search(r'<chat.*?>(.*?)</chat>', buf)
                if not found:
                    break
                buf = buf[found.end():]
                yield json.loads(found.group(1))

class NicoAlert:
    def connect(self, mail, password):
        webapi = WebApi()
        ticket = webapi.login_account(mail, password)
        self.login_info = webapi.login_alert(ticket)
        self.subscriptions = webapi.get_subscriptions(
            self.login_info.user_id, self.login_info.ticket)

        self.comment_server = CommentServerApi()
        self.comment_server.connect(
            self.login_info.address, self.login_info.port)
        for sub in self.subscriptions:
            self.comment_server.join_thread(sub.thread_id)

    def __iter__(self):
        return iter(self.comment_server)


def _parse_arg():
    import argparse
    parser = argparse.ArgumentParser('NicoNicoAlert Clone')
    parser.add_argument('--mail', dest='mail', required=True,
                   help='Mail address to login niconico')
    parser.add_argument('--pass', dest='password', required=True,
                   help='Password to login niconico')
    return parser.parse_args()


def _main():
    arg = _parse_arg()
    nicoalert = NicoAlert()
    nicoalert.connect(arg.mail, arg.password)

    for message in nicoalert:
        print(json.dumps(message, ensure_ascii=False, sort_keys=True, indent=4))
        if message['service'] == 'live':
            print(message['title'])
            print('http://live.nicovideo.jp/watch/' + message['id'])


if __name__ == '__main__':
    _main()
