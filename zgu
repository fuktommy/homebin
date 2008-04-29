#!/usr/bin/perl -w
#
# ざるげっちゅー  "Zaru" Get Uri
#
# URIをHTMLファイルなどから抜き出す。
#
# 使用法：　zgu [-h] [-s] [-a] [-L] [-b base] [-w URI] [file...]
#
# オプション
#	-h : HTML形式での出力
#	-s : //で始まる文字列のみ抜き出す
#	-a : 強制的にhttp://を補う
#	-L : 相対パスのみを抜き出す
#	-b : ベースとなるURIを指定する
#	-w : wgetを使用する
#
# Copyright (c) 2001-2003 Satoshi Fukutomi <info@fuktommy.com>.
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
# 2001/05/16	ver.0.1.0
# 2001/06/10	ver.0.1.1	~が取り出せないバグの修正
# 2001/06/24	ver.0.1.2	blankのスペルミス修正
# 2001/06/30	ver.0.1.3	%が取り出せないバグの修正
# 2001/09/22	ver.0.1.4	抜き出すのを//で始まる文字列とする
# 2002/01/27	ver.0.2.0	相対パス対応
# 2002/01/31	ver.0.2.1	名称をgeturlからzguに変更
# 2002/02/14	ver.0.2.2	;が取り出せないバグの修正
# 2002/03/03	ver.0.2.3	[]が取り出せないバグの修正
# 2002/07/09	ver.0.2.4	+が取り出せないバグの修正
# 2003/10/26	ver.0.3.0	いろいろ
# 2003/11/05	ver.0.3.1	標準入力から読めないバグの修正
#

# オプションの初期設定
$htmlMode = 0;
$simpleMode = 0;
$appendMode = 0;
$localMode = 0;
$base = "";

# 引数の処理
@files = ();
@wgetUri = ();
while (@ARGV) {
	$_ = shift @ARGV;
	if ($_ eq "--help") {
		exec "cat $0";
	} elsif ($_ eq "-h") {
		$htmlMode = 1;
	} elsif ($_ eq "-s") {
		$simpleMode = 1;
	} elsif ($_ eq "-a") {
		$appendMode = 1;
	} elsif ($_ eq "-L") {
		$localMode = 1;
	} elsif ($_ eq "-b") {
		$base = shift @ARGV;
		$base =~ s|/$||;
	} elsif ($_ eq "-w") {
		push @wgetUri, shift @ARGV;
	} elsif ($_ eq "--") {
		push @files, @ARGV;
		@ARGV = ();
	} else {
		push @files, $_;
	}
}

@input = ();

# wgetを使う場合
foreach (@wgetUri) {
	my @buf = `wget -q -O - $_`;
	push @input, @buf;
}
if ((@wgetUri == 1)&&($base eq "")) {
	$base = $wgetUri[0];
	$base =~ s|/[^/]*$||;
}

# ファイルからの読み込み
@ARGV = @files;
@buf = <>;
push @input, @buf;

# URIの抽出
@uri = ();
foreach (@input) {
	while (m|[-_\.\w&=\?/~%:;\[\]+]+|) {
		$uri = $&;
		$_ = $';
		if ($uri =~ m|^([^/]*)//|) {
			my $uri = $';
			my $head = $1;
			if ($uri !~ /\.[^.]/) {
				next;
			} elsif (($head eq "")||("http:" =~ $head)) {
				push @uri, "http://$uri";
				next;
			}
		}
		if ($appendMode) {
			push @uri, "http://$uri";
		} elsif ($uri !~ /\.[^.]/) {
			next;
		} elsif ($uri =~ /^[\d.]+$/) {
			next;
		} elsif ($base) {
			push @uri, "$base/$uri";
		} elsif (! $simpleMode) {
			push @uri, $uri;
		}
	}
}

# ソートと重複した項目や不適な項目の削除
@tmp = sort @uri;
@uri = ();
foreach (@tmp) {
	if ((@uri)&&($_ eq $uri[-1])) {
		next;
	} elsif ($localMode && m|^http://|) {
		next;
	} else {
		push @uri, $_;
	}
}

# 書き出し
$, = "\n";	$\ = "\n";
if ($htmlMode) {
	print "<html><head><title>\"Zaru\" Get Uri</title></head><body>";
	foreach (@uri) {
		print "<a href='$_'>$_</a><br>";
	}
	print "</body></html>";
} else {
	print @uri if (@uri);
}
