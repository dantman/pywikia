# Loop over all pages, calling treelang for each
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.

import os,wikipedia,sys

if sys.platform=='win32':
    normalstatus=0,1
else:
    normalstatus=0,256
    
for f in wikipedia.allpages(start=sys.argv[1]):
    f=f.replace("'",r"'\''")
    print
    print repr(f)
    if sys.platform=='win32':
        status=os.system("python treelang.py -backlink -autonomous %s"%f)
    else:
        status=os.system("python treelang.py -backlink -autonomous '%s'"%f)
    if status not in normalstatus:
        print "Exit status ",status
        sys.exit(1)
