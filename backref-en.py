import os,wikipedia,sys

codefrom='nl'
codeto='eo'

#pages=open('nltode.dat').readlines()
#for ff in pages:
#    f=ff.strip()
for f in wikipedia.allnlpages(start=sys.argv[1]):
    print f
    sys.stdout.flush()
    xf=wikipedia.link2url(f,code=codefrom)
    stdf=wikipedia.url2link(xf,code=codefrom,incode=codefrom)
    try:
        urlname=wikipedia.link2url(f,code=codefrom)
        txt=wikipedia.getPage(codefrom,urlname)
        ll=wikipedia.getLanguageLinks(txt,incode=codefrom)
    except wikipedia.IsRedirectPage:
        continue
    except wikipedia.NoPage:
	print "ERROR: Yikes, does not exist"
        continue
    for code,name in ll.iteritems():
        if code==codeto:
            try:
                ftxt=wikipedia.getPage(codeto,name)
                enll=wikipedia.getLanguageLinks(ftxt,incode=codeto)
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
                    
