import sys,re
R=re.compile('/wiki/(.*?)" *class=[\'\"]internal')
fn=sys.argv[1]
f=open(fn)
text=f.read()
f.close()
for hit in R.findall(text):
    if not ':' in hit:
        if not hit in ['Hoofdpagina','In_het_niews']:
            print hit
