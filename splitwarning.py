# -*- coding: utf-8  -*-
"""Split a treelang.log file into chunks of warnings separated by language"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#

import wikipedia

wikipedia.stopme() # No need to have me on the stack - I don't contact the wiki
files={}
count={}
# TODO: Variable log filename
for line in open('logs/interwiki.log'):
    if line[:8] == 'WARNING:':
        code = line.split(':')[1]
        code = code.strip()
        if code in wikipedia.getSite().languages():
            if not files.has_key(code):
                files[code] = open('warning_%s.log' % code, 'w')
                count[code] = 0
            files[code].write(line)
            count[code] += 1
for code in files.keys():
    print '*%s (%d)' % (code, count[code])

