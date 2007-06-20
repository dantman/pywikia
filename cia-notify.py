#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) Misza13 <misza1313@gmail.com>, 2007
#
# Distributed under the terms of the MIT license.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import sys, re, time

params = {
        'version'   : '1.0',
        'url'       : 'http://example.com/',
        'timestamp' : int(time.time()),
        }

params['module'] = sys.argv[1]
params['project'] = sys.argv[-1]
params['user'] = sys.argv[-2]
#files = sys.argv[2:-3]

input = sys.stdin.read()

MESSAGE = """
<message>
    <generator>
        <name>CIA Python client for CVS</name>
        <version>%(version)s</version>
        <url>%(url)s</url>
    </generator>
    <source>
        <project>%(project)s</project>
        <module>%(module)s</module>
"""

tag = re.search('Tag: (?P<tag>[a-zA-Z0-9_-]+)',input)
if tag:
    MESSAGE += """
        <branch>%s</branch>""" % tag.group('tag')

MESSAGE += """
   </source>
   <timestamp>
       %(timestamp)s
   </timestamp>
   <body>
       <commit>
           <author>%(user)s</author>
           <files>"""

files = re.search('Modified Files:\n\s+(?P<files>.*)',input)
if files:
    for f in files.group('files').split(' '):
        if f:
            MESSAGE += """
               <file>%s</file>""" % f

MESSAGE += """
           </files>
           <log>
%(logmsg)s
           </log>
       </commit>
   </body>
</message>"""

logmsg = re.search('Log Message:(?P<logmsg>.*)',input,re.DOTALL)
if logmsg:
    params['logmsg'] = re.sub('\s+',' ',logmsg.group('logmsg'))
else:
    params['logmsg'] = 'Error parsing log message'

try:
    from xmlrpclib import ServerProxy
    server = ServerProxy('http://cia.vc/RPC2')
    server.hub.deliver(MESSAGE % params)
finally:
    pass
