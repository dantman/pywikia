# Script to check language links for general pages
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.

import sys,copy,wikipedia

# language to check for missing links and modify
mylang = 'nl'

# Summary used in the modification request
wikipedia.setAction('Rob Hooft: semi-automatic interwiki script')

debug = 1
forreal = 1

def compareLanguages(old,new):
    removing=[]
    adding=[]
    for code,name in old.iteritems():
        if not new.has_key(code):
            removing.append(code)
    for code,name in new.iteritems():
        if not old.has_key(code):
            adding.append(code)
    s=""
    if adding:
        s=s+" Adding:"+",".join(adding)
    if removing:
        s=s+" Removing:"+",".join(removing)
    return s
    
def treestep(arr,code,name):
    assert arr[code,name] is None
    try:
        print "Getting %s:%s"%(code,name)
    except ValueError:
        print "Getting",(code,name)
    n=0
    try:
        text=wikipedia.getPage(code,name)
    except wikipedia.NoPage:
        print "---> Does not actually exist"
        arr[code,name]=''
        return 0
    arr[code,name]=text
    for newcode,newname in wikipedia.getLanguageLinks(text).iteritems():
        # Recognize and standardize for Wikipedia
        newname=newname[0].upper()+newname[1:]
        newname=newname.strip()
        newname=wikipedia.link2url(newname)
        if not (newcode,newname) in arr:
            lname=wikipedia.url2link(newname)
            print "NOTE: from %s:%s we got the new %s:%s"%(code,name,newcode,lname)
            arr[newcode,newname]=None
            n+=1
    return n
    
def treesearch(code,name):
    arr={(code,name):None}
    modifications=1
    while modifications:
        modifications=0
        for newcode,newname in arr.keys():
            if arr[newcode,newname] is None:
                modifications+=treestep(arr,newcode,newname)
    return arr
    
name=raw_input('Which page to check:')

name=wikipedia.link2url(name)

m=treesearch(mylang,name)
print "==Result=="
new={}
k=m.keys()
k.sort()
for code,cname in k:
    if code==mylang:
        if m[code,cname]:
            old=wikipedia.getLanguageLinks(m[code,cname])
            oldtext=m[code,cname]
    elif m[(code,cname)]:
        print "%s:%s"%(code,wikipedia.url2link(cname))
        if new.has_key(code):
            print "ERROR: %s has '%s' as well as '%s'"%(code,new[code],wikipedia.url2link(cname))
            while 1:
                answer=raw_input("Use former (f) or latter (l)?")
                if answer.startswith('f'):
                    break
                elif answer.startswith('l'):
                    new[code]=wikipedia.url2link(cname)
                    break
        else:
            new[code]=wikipedia.url2link(cname)
print "==status=="
#print old
print compareLanguages(old,new)
print "==upload=="
s=wikipedia.interwikiFormat(new)
newtext=s+wikipedia.removeLanguageLinks(oldtext)
if debug:
    print s
if newtext!=oldtext:
    print "NOTE: Replacing %s: %s"%(mylang,name)
    if forreal:
        answer=raw_input('submit y/n ?')
        if answer=='y':
            status,reason,data=wikipedia.putPage(mylang,name,newtext)
            if str(status)!='302':
                print status,reason
