"""
Script to extract all wiki page names a certain HTML file points to

This can be used to run another script over a series of wikipedia pages
that is mentioned in a list.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import sys,re
R=re.compile('/wiki/(.*?)" *')
fn=sys.argv[1]
f=open(fn)
text=f.read()
f.close()
for hit in R.findall(text):
    if not ':' in hit:
        if not hit in ['Hoofdpagina','In_het_nieuws']:
            print hit
