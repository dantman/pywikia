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

debug = 0

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
        newname=newname[0].upper()+newname[1:]
        if not (newcode,newname) in arr:
            try:
                print "NOTE: from %s:%s we got the new %s:%s"%(code,name,newcode,newname)
            except ValueError: 
                print "NOTE: new:", (code,name,newcode,newname)
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
    
name=raw_input('Which page to check:')

m=treesearch(mylang,name)
