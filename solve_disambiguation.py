import wikipedia,re,sys

wikipedia.action = wikipedia.username+': Robot-assisted disambiguation '

mylang='nl'


def getreferences(pl):
    host = wikipedia.langs[pl.code()]
    url="/w/wiki.phtml?title=Speciaal:Whatlinkshere&target=%s"%(pl.urlname())
    txt,charset=wikipedia.getUrl(host,url)
    Rref=re.compile('<li><a href.* title="([^"]*)"')
    return Rref.findall(txt)

wrd=[]
for arg in sys.argv[1:]:
    wrd.append(arg)

wrd=' '.join(wrd)

thispl=wikipedia.PageLink(mylang,wrd)

thistxt=thispl.get()

w=r'([^\]\|]*)'
Rlink=re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')

alternatives=[]

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
            print "== %s =="%(refpl),m.start(),m.end()
            print reftxt[max(0,m.start()-context):m.end()+context]
            choice=raw_input("Which replacement (n=none,q=quit,m=more context,l=list):")
            if choice=='n':
                choice=-1
                break
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
