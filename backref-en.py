import os,wikipedia,sys

codefrom='nl'
codeto='de'

for f in wikipedia.allnlpages(start=sys.argv[1]):
    print f,wikipedia.link2url(f,incode=codefrom)
    sys.stdout.flush()
    xf=wikipedia.link2url(f,incode=codefrom)
    stdf=wikipedia.url2link(xf,code=codefrom,incode=codefrom)
    try:
        ll=wikipedia.getLanguageLinks(wikipedia.getPage(codefrom,wikipedia.link2url(f,code=codefrom)))
    except wikipedia.IsRedirectPage:
        continue
    except wikipedia.NoPage:
	print "ERROR: Yikes, does not exist"
        continue
    for code,name in ll.iteritems():
        if code==codeto:
            try:
                enll=wikipedia.getLanguageLinks(wikipedia.getPage(codeto,name))
            except wikipedia.NoPage:
                print >> sys.stderr, "%s:%s does not exist, referred from %s:%s"%(codeto,name,codefrom,f)
                sys.stderr.flush()
            except wikipedia.IsRedirectPage:
                print >> sys.stderr, "%s:%s is redirect, referred from %s:%s"%(codeto,name,codefrom,f)
                sys.stderr.flush()
            else:
                found=0
                for code2,name2 in enll.iteritems():
                    if code2==codefrom:
                        found+=1
                        xf=wikipedia.link2url(name2,code=code2)
                        stdname2=wikipedia.url2link(xf,code=code2,incode=code)
                        if stdname2!=stdf:
                            print >> sys.stderr, "%s:%s does not link to %s:%s but to %s:%s"%(codeto,name,codefrom,f,codefrom,name2)
                            sys.stderr.flush()
                if not found:
                    print >> sys.stderr, "%s:%s does not link to %s:%s"%(codeto,name,codefrom,f)
                    
