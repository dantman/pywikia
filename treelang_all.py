"""
Loop over all pages in the home wikipedia, calling treelang for each

This script accepts all options that treelang.py accepts. Command line options
that do not start with -, or that consist of only a - are taken as words of the
first page name that should be checked; except if they give an existing file
name, in which case the file will be treated as a list of pages to check.

If no first page is specified nor a file of pagenames is given, the procedure
starts at A (and therefore skips everything that starts with e.g. digits).

If no options are specified at all, treelang is run with the options
-autonomous.

A complete alternative is to run on a file of warnings that are coming from a
treelang_all run on another wikipedia. Just select the lines from the backlink
log file that represent omissions on your home wikipedia, and then run

treelang_all.py -warnfile:xxxxxx

specifying the name of the file on the xxxxx. This will parse the warnings, and
give them as hints to treelang in a special run that is optimized to solve the
warnings.

This script also read the treelang_backlink and treelang_log variables 
(see treelang.py for more informations) your configuration file user-config.py .

"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import os,sys

import wikipedia

options=[]
start=[]
file=[]
hints={}

debug = 0

for arg in sys.argv[1:]:
    if arg.startswith('-warnfile:'):
        import re
        R=re.compile(r'WARNING: ([^\[]*):\[\[([^\[]+)\]\][^\[]+\[\[([^\[]+):([^\[]+)\]\]')
        fn=arg[10:]
        f=open(fn)
        for line in f.readlines():
            m=R.search(line)
            if m:
                if m.group(1)==wikipedia.mylang:
                    #print m.group(1), m.group(2), m.group(3), m.group(4)
                    if not hints.has_key(m.group(2)):
                        hints[m.group(2)]=[]
                    hints[m.group(2)].append('%s:%s'%(m.group(3),wikipedia.link2url(m.group(4),m.group(3))))
        f.close()
    elif arg[0] == '-' and len(arg)>1:
        # Options are both for us and for the treelang robot itself
        wikipedia.argHandler(arg)
        options.append(arg)
    elif os.path.exists(arg):
        file.append(arg)
    else:
        start.append(arg)

if options:
    options=' '.join(options)
else:
    options='-autonomous'

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
elif hints:
    lst=[]
    for key in hints.iterkeys():
        lst.append(wikipedia.PageLink(wikipedia.mylang,linkname=key))
    lst.sort()
else:
    lst=wikipedia.allpages(start = start)
        
for pl in lst:
    f = pl.urlname()
    wikipedia.get_throttle()
    f = f.replace("'", r"'\''")
    if os.isatty(1):
        print
        print repr(f)
    hintstr=''
    if hints.has_key(pl.linkname()):
        for hint in hints[pl.linkname()]:
            hintstr += ' -hint:%s'%hint
    if sys.platform=='win32':
        status = os.system("treelang.py %s %s %s" % (options, hintstr, f))
    else:
        if debug:
            print ("python treelang.py %s %s '%s'" % (options, hintstr, f))
            status = 0
        else:
            status = os.system("python treelang.py %s %s '%s'" % (options, hintstr, f))
    if status not in normalstatus:
        print "Exit status ", status
        sys.exit(1)
