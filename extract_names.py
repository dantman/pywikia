#
# Script to extract all wiki page names a certain HTML file points to
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the PSF license.
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
