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

Rlink=re.compile('\[\[([^\]]*)\]\]')

alternatives=Rlink.findall(thistxt)

for i in range(len(alternatives)):
    print "%3d"%i,alternatives[i]

Rthis=re.compile('\[\[%s(\|[^\]]*)?\]\]'%thispl.linkname())
uln=wikipedia.html2unicode(thispl.linkname(),language=mylang)
aln=wikipedia.addEntity(uln)
Rthis2=re.compile('\[\[%s(\|[^\]]*)?\]\]'%aln)

for ref in getreferences(thispl):
    refpl=wikipedia.PageLink(mylang,ref)
    try:
        reftxt=refpl.get()
    except wikipedia.IsRedirectPage:
        pass
    else:
        m=Rthis.search(reftxt)
        if not m:
            m=Rthis2.search(reftxt)
        if not m:
            print "Not found in %s"%refpl
            continue
        context=30
        while 1:
            print "== %s =="%(refpl)
            print reftxt[m.start()-context:m.end()+context]
            choice=raw_input("Which replacement (n=none,q=quit,m=more context,l=list):")
            if choice=='n':
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
        if not g1:
            g1=thispl.linkname()
        reptxt="%s|%s"%(alternatives[choice],g1)
        newtxt=reftxt[:m.start()+2]+reptxt+reftxt[m.end()-2:]
        print newtxt[m.start()-30:m.end()+30]
        refpl.put(newtxt)
