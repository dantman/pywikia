"""
Script to help a human solve disambiguations by presenting a set of options.

Specify the disambiguation page on the command line. The program will
pick up the page, and look for all alternative links, and show them with
a number adjacent to them. It will then automatically loop over all pages
referring to the disambiguation page, and show 30 characters on each side
of the reference to help you make the decision between the
alternatives. It will ask you to type the number of the appropriate
replacement, and perform the change robotically.

Command line options:

   -pos:XXXX adds XXXX as an alternative disambiguation

   -just     only use the alternatives given on the command line, do not 
             read the page for other possibilities

Options that are accepted by more robots:

   -lang:XX  set your home wikipedia to XX instead of the one given in
             username.dat
             
To complete a move of a page, one can use:

    python solve_disambiguation.py -just -pos:New_Name Old_Name
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia,re,sys

if not wikipedia.special.has_key(wikipedia.mylang):
    print "Please add the translation for the Special: namespace in"
    print "Your home wikipedia to the wikipedia.py module"
    import sys
    sys.exit(1)

msg={
    'en':'Robot-assisted disambiguation ',
    'da':'Retter flertydigt link til '
    }
if msg.has_key(wikipedia.mylang):
    msglang=wikipedia.mylang
else:
    msglang='en'

def getreferences(pl):
    host = wikipedia.langs[pl.code()]
    url="/w/wiki.phtml?title=%s:Whatlinkshere&target=%s"%(wikipedia.special[wikipedia.mylang], pl.urlname())
    txt,charset=wikipedia.getUrl(host,url)
    Rref=re.compile('<li><a href.* title="([^"]*)"')
    return Rref.findall(txt)

wrd=[]
alternatives=[]
getalternatives=1

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg.startswith('-pos:'):
        alternatives.append(arg[5:])
    elif arg=='-just':
        getalternatives=0
    else:
        wrd.append(arg)

wrd=' '.join(wrd)

wikipedia.setAction(msg[msglang]+wrd)

thispl=wikipedia.PageLink(wikipedia.mylang, wrd)

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
uln=wikipedia.html2unicode(thispl.linkname(),language = wikipedia.mylang)
aln=wikipedia.addEntity(uln)
Rthis=re.compile(zz%aln)
exps.append(Rthis)
Rthis=re.compile(zz%thispl.linkname().lower())
exps.append(Rthis)
Rthis=re.compile(zz%aln.lower())
exps.append(Rthis)

for ref in getreferences(thispl):
    refpl=wikipedia.PageLink(wikipedia.mylang, ref)
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
