"""Split a treelang.log file into chunks of warnings separated by language"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#

import wikipedia

files={}
count={}
for line in open('treelang.log'):
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
    print '%s (%d)' % (code, count[code])

