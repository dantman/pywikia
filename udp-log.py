#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) Misza13 <misza1313@gmail.com>, 2007
#
# Distributed under the terms of the MIT license.
#
import sys, re, socket

TARGET_HOST = 'tools.wikimedia.de'
TARGET_PORT = 31338

input = sys.stdin.read()
log = re.search('Versions: (?P<ver>.*?)\n.*Log Message:\n(?P<logmsg>.*)',input,re.DOTALL)

if log:
    print 'Routing commit data via UDP...'
    ver = log.group('ver')
    logmsg = log.group('logmsg').replace('\n',' ')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((TARGET_HOST,TARGET_PORT))
    sock.send('commited: \002%s\002 * \0032%s\003' % (ver,logmsg))
    sock.close()
