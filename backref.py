# Script to check pages referred to via interwiki links for the reverse link
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the PSF license

import os,wikipedia,sys

codefrom = wikipedia.mylang
codeto = None
mode=0
word=[]

for arg in sys.argv[1:]:
    if len(arg)==3 and arg[2]==':':
        codeto=arg[:2]
    elif arg=='-one':
        mode=1
    elif arg=='-file':
        mode=2
    elif arg=='-start':
        mode=3
    else:
        word.append(arg)

files={}

word=' '.join(word)
if mode==1:
    pages=[word]
elif mode==2:
    pages=open(word).readlines()
elif mode==3:
    pages=wikipedia.allpages(start=word)
else:
    raise "Please specify one of -one -file or -start"

for f in pages:
    pl=wikipedia.PageLink(codefrom,name=f)
    print pl
    sys.stdout.flush()
    try:
        ll=pl.interwiki()
    except wikipedia.IsRedirectPage:
        continue
    except wikipedia.LockedPage: # Can't do anythinh with a locked page
        continue
    except wikipedia.NoPage:
	print "ERROR: Yikes, does not exist"
        continue
    #print "ll",ll
    for pl2 in ll:
        #print "pl2=",pl2
        if codeto is None or pl2.code()==codeto:
            # Select file
            if codeto is None and mode!=1:
                if not files.has_key(pl2.code()):
                    print "opening file for",pl2.code()
                    files[pl2.code()]=open("%s-backref.log"%pl2.code(),"a")
                fil=files[pl2.code()]
            else:
                fil=sys.stderr
            try:
                ll2=pl2.interwiki()
            except wikipedia.NoPage:
                print >> fil , "%s does not exist, referred from %s"%(pl2,pl)
                fil.flush()
            except wikipedia.IsRedirectPage:
                print >> fil , "%s is redirect, referred from %s"%(pl2,pl)
                fil.flush()
            except wikipedia.LockedPage:
                print >> fil , "%s is locked, can't check whether it links %s"%(pl2,pl)
                fil.flush()
            else:
                found=0
                for pl3 in ll2:
                    if pl3.code()==codefrom:
                        found+=1
                        #print "compare",pl,pl3
                        if pl3!=pl:
                            print >> fil, "%s does not link to %s but to %s"%(pl2,pl,pl3)
                            fil.flush()
                if not found:
                    print >> fil, "%s does not link to %s"%(pl2,pl)
                    fil.flush()
