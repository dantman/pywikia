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

if sys.platform=='win32':
    normalstatus=0,1
else:
    normalstatus=0,256
    
for pl in wikipedia.allpages(start=sys.argv[1]):
    f=pl.urlname()
    wikipedia.throttle()
    f=f.replace("'",r"'\''")
    if os.isatty(1):
        print
        print repr(f)
    if sys.platform=='win32':
        status=os.system("python treelang.py -backlink -autonomous %s"%f)
    else:
        status=os.system("python treelang.py -backlink -autonomous '%s'"%f)
    if status not in normalstatus:
        print "Exit status ",status
        sys.exit(1)
