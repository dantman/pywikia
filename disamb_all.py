"""
This runs solve_disambiguation.py over a list of pages, which
can for example be gotten through extract_names.py. Its only
argument is the name of the file from which the list is taken.
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2003
#
# Distribute under the terms of the PSF license.
#
#
import os, sys

import wikipedia

file=[]
options=[]

for arg in sys.argv[1:]:
    if arg[0] == '-' and len(arg)>1:
        # Options are both for us and for the treelang robot itself
        wikipedia.argHandler(arg)
        options.append(arg)
    else:
        file.append(arg)

if options:
    options=' '.join(options)
else:
    options='-nil'

if sys.platform == 'win32':
    normalstatus = 0, 1
else:
    normalstatus = 0, 256

lst=[]

# if run without parameter, ask for the filename
if file==[]:
    file.append(raw_input('Please enter the list\'s filename: '))


for fn in file:
    f=open(fn)
    for line in f.readlines():
        lst.append(wikipedia.PageLink(wikipedia.mylang,line))
    f.close()
        
for pl in lst:
    f = pl.urlname()
    f = f.replace("'", r"'\''")
    if os.isatty(1):
        print
        print repr(f)
    hintstr=''
    if sys.platform=='win32':
        status = os.system("solve_disambiguation.py %s %s" % (options, f))
    else:
        status = os.system("python solve_disambiguation.py %s '%s'" % (options, f))
    if status not in normalstatus:
        print "Exit status ", status
        sys.exit(1)
