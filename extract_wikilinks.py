"""
Script to extract all wiki page names a certain HTML file points to in
interwiki-link format

The output can be used as input to interwiki.py.

This script takes a single file name argument, the file should be a HTML file
as captured from one of the wikipedia servers.
"""
#
# (C) Rob W.W. Hooft, Andre Engels, 2003-2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import sys,re,wikipedia
R=re.compile('/wiki/(.*?)" *')
fn=sys.argv[1]
f=open(fn)
text=f.read()
f.close()
for hit in R.findall(text):
    if not ':' in hit:
        if not hit in ['Hoofdpagina','In_het_nieuws']:
            print "[[%s:%s]]" %(wikipedia.mylang,hit)
