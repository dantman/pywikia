# Script to solve disambiguations
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the PSF license
import wikipedia,re,sys


mylang = wikipedia.mylang

def getreferences(pl):
    host = wikipedia.langs[pl.code()]
    url="/w/wiki.phtml?title=Speciaal:Whatlinkshere&target=%s"%(pl.urlname())
    txt,charset=wikipedia.getUrl(host,url)
    Rref=re.compile('<li><a href.* title="([^"]*)"')
    return Rref.findall(txt)

wrd=[]
alternatives=[]
getalternatives=1

for arg in sys.argv[1:]:
    if arg.startswith('-pos:'):
        alternatives.append(arg[5:])
    elif arg=='-just':
        getalternatives=0
    else:
        wrd.append(arg)

wrd=' '.join(wrd)

wikipedia.setAction('Robot-assisted disambiguation '+wrd)

thispl=wikipedia.PageLink(mylang,wrd)

if getalternatives:
    thistxt=thispl.get()

    w=r'([^\]\|]*)'
    Rlink=re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')

    for a in Rlink.findall(thistxt):
        alternatives.append(a[0])

for i in range(len(alternatives)):
    print "%3d"%i,alternatives[i]

exps=[]
zz='\[\[(%s)(\|[^\]]*)?\]\]'
Rthis=re.compile(zz%thispl.linkname())
exps.append(Rthis)
uln=wikipedia.html2unicode(thispl.linkname(),language=mylang)
aln=wikipedia.addEntity(uln)
Rthis=re.compile(zz%aln)
exps.append(Rthis)
Rthis=re.compile(zz%thispl.linkname().lower())
exps.append(Rthis)
Rthis=re.compile(zz%aln.lower())
exps.append(Rthis)

for ref in getreferences(thispl):
    refpl=wikipedia.PageLink(mylang,ref)
    try:
        reftxt=refpl.get()
    except wikipedia.IsRedirectPage:
        pass
    else:
        for Rthis in exps:
            m=Rthis.search(reftxt)
            if m:
                break
        else:
            print "Not found in %s"%refpl
            continue
        context=30
        while 1:
            print "== %s =="%(refpl)
            print reftxt[max(0,m.start()-context):m.end()+context]
            choice=raw_input("Which replacement (n=none,q=quit,m=more context,l=list,a=add new):")
            if choice=='n':
                choice=-1
                break
            elif choice=='a':
                ns=raw_input('New alternative:')
                alternatives.append(ns)
            elif choice=='q':
                sys.exit(0)
                break
            elif choice=='m':
                context*=2
            elif choice=='l':
                for i in range(len(alternatives)):
                    print "%3d"%i,alternatives[i]
            else:
                try:
                    choice=int(choice)
                except ValueError:
                    pass
                else:
                    break
        if choice<0:
            continue
        g1=m.group(1)
        g2=m.group(2)
        if g2:
            g2=g2[1:]
        else:
            g2=g1
        reptxt="%s|%s"%(alternatives[choice],g2)
        newtxt=reftxt[:m.start()+2]+reptxt+reftxt[m.end()-2:]
        print newtxt[max(0,m.start()-30):m.end()+30]
        refpl.put(newtxt)
