import os,wikipedia,sys

codefrom='nl'
codeto='en'
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

word=' '.join(word)
if mode==1:
    pages=[word]
elif mode==2:
    pages=open(word).readlines()
elif mode==3:
    pages=wikipedia.allnlpages(start=word)
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
    except wikipedia.NoPage:
	print "ERROR: Yikes, does not exist"
        continue
    #print "ll",ll
    for pl2 in ll:
        #print "pl2=",pl2
        if pl2.code()==codeto:
            try:
                ll2=pl2.interwiki()
            except wikipedia.NoPage:
                print >> sys.stderr, "%s does not exist, referred from %s"%(pl2,pl)
                sys.stderr.flush()
            except wikipedia.IsRedirectPage:
                print >> sys.stderr, "%s is redirect, referred from %s"%(pl2,pl)
                sys.stderr.flush()
            else:
                found=0
                for pl3 in ll2:
                    if pl3.code()==codefrom:
                        found+=1
                        #print "compare",pl,pl3
                        if pl3!=pl:
                            print >> sys.stderr, "%s does not link to %s but to %s"%(pl2,pl,pl3)
                            sys.stderr.flush()
                if not found:
                    print >> sys.stderr, "%s does not link to %s"%(pl2,pl)
                    
