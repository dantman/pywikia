"""
Loop over all pages in the home wikipedia, calling treelang for each

This script accepts all options that treelang.py accepts. Command line options
that do not start with -, or that consist of only a - are taken as words of the
first page name that should be checked; except if they give an existing file
name, in which case the file will be treated as a list of pages to check.

If no first page is specified nor a file of pagenames is given, the procedure
starts at A (and therefore skips everything that starts with e.g. digits).

If no options are specified at all, treelang is run with the options
-backlink -autonomous.
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
file=[]

for arg in sys.argv[1:]:
    if arg[0] == '-' and len(arg)>1:
        options.append(arg)
    elif os.path.exists(arg):
        file.append(arg)
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

if file:
    lst=[]
    for fn in file:
        f=open(fn)
        for line in f.readlines():
            lst.append(wikipedia.PageLink(wikipedia.mylang,line))
        f.close()
else:
    lst=wikipedia.allpages(start = start)
        
for pl in lst:
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
