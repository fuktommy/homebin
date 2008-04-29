#!/usr/bin/perl
#
# 簡易版HTTPプロキシ
# 主にヘッダの書き換えが目的
#
# Copyright (c) 2004,2006 Satoshi Fukutomi <info@fuktommy.com>.
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
#
# http://x68000.startshop.co.jp/~68user/ の各種スクリプトを参考にいたしました。
#

use strict;
use Socket;

my $PORT  = 8080;
my $IMENU = "ime.nu";
my @NO_IMENU = qw( mixi.jp );
my @NO_MOZILLA = qw( www.google.co.jp );

sub replaceReferer($$$) {
	my($referer, $host, $path) = @_;
	my $referer_host = ($referer =~ m|^\w+://([^:/]+)|)? $1: "";
	if (($host ne $referer_host) && (! grep $_ eq $host, @NO_IMENU)) {
		warn "$referer_host -> $host\n";
		$host =~ s|.*://||;
		return "http://ime.nu/$host$path";
	} else {
		return $referer;
	}
}

sub replaceAgent($$$) {
	my($agent, $host, $path) = @_;
	if ((! grep $_ eq $host, @NO_MOZILLA)) {
		return "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)";
	} else {
		return $agent;
	}
}

$SIG{PIPE} = "IGNORE";
$SIG{CHLD} = "IGNORE";

socket CLIENT_WAITING, PF_INET, SOCK_STREAM, 0 or die "failed to open socket. $!\n";
setsockopt CLIENT_WAITING, SOL_SOCKET, SO_REUSEADDR, 1 or die "failed to setsockopt. $!\n";
bind CLIENT_WAITING, pack_sockaddr_in($PORT, INADDR_ANY) or die "failed to bind. $!\n";
listen CLIENT_WAITING, SOMAXCONN or die "failed to listen: $!\n";

while (1){
	my($paddr, $pid);
	unless ($paddr = accept(CLIENT, CLIENT_WAITING)) {
		sleep 1;
		next;
	}
	my($client_port, $client_iaddr) = unpack_sockaddr_in $paddr;

	select CLIENT; $|=1;

	if ((! defined($pid = fork)) || $pid) {
		close CLIENT;
		next;

	} else {
		$SIG{PIPE} = "IGNORE";
		my $length = 0;
		my($method, $host, $port, $path);
		my @header = ();
		my $flag_referer;
		while (<CLIENT>) {
			s/[\n|\r]//g;
			if ($_ eq "") {
				last;
			} elsif (m{^(GET|POST) http://([^:/]+):(\d+)([^ ]*)}) {
				($method, $host, $port, $path) = ($1, $2, $3, $4);
			} elsif (m{^(GET|POST) http://([^:/]+)([^ ]*)}) {
				($method, $host, $port, $path) = ($1, $2, 80, $3);
			} elsif (/^Content-length:\s+(\d+)/i) {
				$length = $1;
			} elsif (/^User-Agent:/i ){
				my $agent = $';
				$_ = "User-Agent: " . replaceAgent($agent, $host, $path);
			} elsif (/^Referer: /i) {
				my $referer = $';
				$_ = "Referer: " . replaceReferer($referer, $host, $path);
				$flag_referer = 1;
			}
			push @header, $_;
		}
		if (! $flag_referer) {
			push @header, "Referer: " . replaceReferer("", $host, $path);
		}
		#if (($host eq "fuktommy.ddo.jp")
		#	|| ($host eq "shingetsu.p2p")) {
		#	$host = "localhost";
		#	$port = 8000 if ($port == 80);
		#}
		$path = "/" unless ($path);
		shift @header;
		my $addr = inet_aton $host or die "faild to resolv. $!";
		my $sockaddr = pack_sockaddr_in($port, $addr);
		socket SOCKET, PF_INET, SOCK_STREAM, 0;
		connect SOCKET, $sockaddr or die "failed to connect. $!";
		select SOCKET; $| = 1;
		print SOCKET "$method $path HTTP/1.0\r\n";
		print SOCKET join "\r\n", @header;
		print SOCKET "\r\n\r\n";
		if ($length) {
			read CLIENT, $_, $length;
			print SOCKET $_;
		}
		#my $replaced = 0;
		my $replaced = 1;
		while (<SOCKET>) {
			if ((! $replaced) && (/^Content-Type:/im)) {
				if (s|^Content-Type: (application/[-+\w]+)|Content-Type: text/html|im) {
					warn "Content-Type: $1\n";
				} elsif (s|^Content-Type: (audio/x-mpegurl)|Content-Type: text/plain|im) {
				}
				$replaced = 1;
			}
			print CLIENT $_;
		}
		shutdown SOCKET, 2;
		shutdown CLIENT, 2;
		close SOCKET;
		close CLIENT;
		exit;
	}
}
