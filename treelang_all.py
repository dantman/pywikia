"""
Loop over all pages in the home wikipedia, calling treelang for each
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import os,wikipedia,sys

options=[]
start=[]

for arg in sys.argv[1:]:
    if arg[0] == '-' and len(arg)>1:
        options.append(arg)
    else:
        start.append(arg)

if options:
    options=' '.join(options)
else:
    options='-backlink -autonomous'

if start:
    start='_'.join(start)
else:
    start='A'
    
if sys.platform == 'win32':
    normalstatus = 0, 1
else:
    normalstatus = 0, 256
    
for pl in wikipedia.allpages(start = start):
    f = pl.urlname()
    wikipedia.throttle()
    f = f.replace("'", r"'\''")
    if os.isatty(1):
        print
        print repr(f)
    if sys.platform=='win32':
        status = os.system("python treelang.py %s %s" % (options, f))
    else:
        status = os.system("python treelang.py %s '%s'" % (options, f))
    if status not in normalstatus:
        print "Exit status ", status
        sys.exit(1)
