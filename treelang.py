# Script to check language links for general pages
#
# $Id$
#
# (C) Rob W.W. Hooft, 2003
# Distribute under the terms of the GPL.

import sys,copy,wikipedia,re

# language to check for missing links and modify
mylang = 'nl'

# Summary used in the modification request
wikipedia.setAction('%s: semi-automatic interwiki script'%wikipedia.username)

debug = 1
forreal = 1

datetable={
    'januari':{'en':'January %d','de':'%d. Januar','fr':'%d janvier','af':'01-%02d'},
    'februari':{'en':'February %d','de':'%d. Februar','fr':'%d fevrier','af':'02-%02d'},
    'maart':{'en':'March %d','de':'%d. M&auml;rz','fr':'%d mars','af':'03-%02d'},
    'april':{'en':'April %d','de':'%d. April','fr':'%d avril','af':'04-%02d'},
    'mei':{'en':'May %d','de':'%d. Mai','fr':'%d mai','af':'05-%02d'},
    'juni':{'en':'June %d','de':'%d. Juni','fr':'%d juin','af':'06-%02d'},
    'juli':{'en':'July %d','de':'%d. Juli','fr':'%d juillet','af':'07-%02d'},
    'augustus':{'en':'August %d','de':'%d. August','fr':'%d aout','af':'08-%02d'},
    'september':{'en':'September %d','de':'%d. September','fr':'%d septembre','af':'09-%02d'},
    'oktober':{'en':'October %d','de':'%d. Oktober','fr':'%d octobre','af':'10-%02d'},
    'november':{'en':'November %d','de':'%d. November','fr':'%d novembre','af':'11-%02d'},
    'december':{'en':'December %d','de':'%d. Dezember','fr':'%d decembre','af':'12-%02d'},
}

yearADfmt={'ja':'%d&#24180;'} # Others default to '%d'

yearBCfmt={'de':'%d v. Chr.','en':'%d BC','fr':'-%d','pl':'%d p.n.e.',
           'es':'%d adC','eo':'-%d'} # No default

def autonomous_problem(pl):
    if autonomous:
        f=open('autonomous_problem.dat','a')
        f.write("%s\n"%pl)
        f.close()
        sys.exit(1)
    
def sametranslate(pl,arr):
    for newcode in wikipedia.langs:
        # Put as suggestion into array
        newname=pl.linkname()
        if newcode=='eo' and same=='name':
            newname=newname.split('_')
            newname[-1]=newname[-1].upper()
            newname='_'.join(newname)
        x=wikipedia.PageLink(newcode,newname)
        if x not in arr:
            arr[x]=None
    
def autotranslate(pl,arr,same=0):
    if same:
        return sametranslate(pl,arr)
    if hints:
        for h in hints:
            newcode,newname=h.split(':')
            x=wikipedia.PageLink(newcode,newname)
            if x not in arr:
                arr[x]=None
    # Autotranslate dates into some other languages, the rest will come from
    # existing interwiki links.
    Rdate=re.compile('(\d+)_(%s)'%('|'.join(datetable.keys())))
    m=Rdate.match(pl.linkname())
    if m:
        for newcode,fmt in datetable[m.group(2)].items():
            newname=fmt%int(m.group(1))
            x=wikipedia.PageLink(newcode,newname)
            if x not in arr:
                arr[x]=None
        return

    # Autotranslate years A.D.
    Ryear=re.compile('^\d+$')
    m=Ryear.match(pl.linkname())
    if m:
        for newcode in wikipedia.langs:
            fmt = yearADfmt.get(newcode,'%d')
            newname = fmt%int(m.group(0)) 
            x=wikipedia.PageLink(newcode,newname)
            if x not in arr:
                arr[x]=None
        return

    # Autotranslate years B.C.
    Ryear=re.compile('^(\d+)_v._Chr.')
    m=Ryear.match(pl.linkname())
    if m:
        for newcode in wikipedia.langs:
            fmt = yearBCfmt.get(newcode)
            if fmt:
                newname = fmt%int(m.group(1))
                x=wikipedia.PageLink(newcode,newname)
                if x not in arr:
                    arr[x]=None
        return
    
def compareLanguages(old,new):
    global confirm
    removing=[]
    adding=[]
    modifying=[]
    for code in old.keys():
        if code not in new.keys():
            confirm+=1
            removing.append(code)
        elif old[code]!=new[code]:
            modifying.append(code)

    for code2 in new.keys():
        if code2 not in old.keys():
            adding.append(code2)
    s=""
    if adding:
        s=s+" Adding:"+",".join(adding)
    if removing:
        s=s+" Removing:"+",".join(removing)
    if modifying:
        s=s+" Modifying:"+",".join(modifying)
    return s
    
def treestep(arr,pl,abort_on_redirect=0):
    assert arr[pl] is None
    print "Getting %s"%pl
    n=0
    try:
        text=pl.get()
    except wikipedia.NoPage:
        print "---> Does not actually exist"
        arr[pl]=''
        return 0
    except wikipedia.LockedPage:
        print "---> Locked"
        arr[pl]=1
        return 0
    except wikipedia.IsRedirectPage,arg:
        if abort_on_redirect and pl.code()==mylang:
            raise
        newpl=wikipedia.PageLink(pl.code(),str(arg))
        arr[pl]=''
        print "NOTE: %s is a redirect to %s"%(pl,newpl)
        if not newpl in arr:
            arr[newpl]=None
            return 1
        return 0
    arr[pl]=text
    for newpl in pl.interwiki():
        if newpl not in arr:
            print "NOTE: from %s we got the new %s"%(pl,newpl)
            arr[newpl]=None
            n+=1
    return n
    
def treesearch(pl):
    arr={pl:None}
    # First make one step based on the language itself
    try:
        n=treestep(arr,pl,abort_on_redirect=1)
    except wikipedia.IsRedirectPage:
        print "Is redirect page"
        return
    if n==0 and not arr[pl]:
        print "Mother doesn't exist"
        return
    if untranslated:
        if len(arr)>1:
            print "Already has translations"
            return
        else:
            newhint=raw_input("Hint:")
            if not newhint:
                return
            hints.append(newhint)
    # Then add translations if we survived.
    autotranslate(pl,arr,same=same)
    modifications=1
    while modifications:
        modifications=0
        for newpl in arr.keys():
            if arr[newpl] is None:
                modifications+=treestep(arr,newpl)
    return arr

inname=[]

bell=1
ask=1
same=0
only_if_status=1
confirm=0
autonomous=0
untranslated=0
hints=[]

for arg in sys.argv[1:]:
    if arg=='-force':
        ask=0
    elif arg=='-always':
        only_if_status=0
    elif arg=='-same':
        same=1
    elif arg=='-untranslated':
        untranslated=1
    elif arg.startswith('-hint:'):
        hints.append(arg[6:])
    elif arg=='-name':
        same='name'
    elif arg=='-confirm':
        confirm=1
    elif arg=='-autonomous':
        autonomous=1
        bell=0
    else:
        inname.append(arg)
    
inname='_'.join(inname)
if not inname:
    inname=raw_input('Which page to check:')

inpl=wikipedia.PageLink(mylang,inname)

m=treesearch(inpl)
if not m:
    print "No matrix"
    sys.exit(1)
print "==Result=="
new={}
k=m.keys()
k.sort()
for pl in k:
    if pl.code()==mylang:
        if pl!=inpl:
            print "ERROR: %s refers back to %s"%(inpl,pl)
            confirm+=1
            autonomous_problem(inpl)
    elif m[pl]:
        print pl
        if new.has_key(pl.code()) and new[pl.code()]!=None and new[pl.code()]!=pl:
            print "ERROR: '%s' as well as '%s'"%(new[pl.code()],pl)
            while 1:
                if bell:
                    sys.stdout.write('\07')
                confirm+=1
                autonomous_problem(inpl)
                answer=raw_input("Use (f)ormer or (l)atter or (n)either or (q)uit?")
                if answer.startswith('f'):
                    break
                elif answer.startswith('l'):
                    new[pl.code()]=pl
                    break
                elif answer.startswith('n'):
                    new[pl.code()]=None
                    break
                elif answer.startswith('q'):
                    sys.exit(1)
        elif pl.code() not in new or new[pl.code()]!=None:
            new[pl.code()]=pl
print "==status=="
old={}
for pl in inpl.interwiki():
    old[pl.code()]=pl
if not old:
    print "No old languages found. Does the dutch page not exist?"
    sys.exit(1)
####
mods=compareLanguages(old,new)
if not mods and only_if_status:
    print "No changes"
    sys.exit(1)
print mods
print "==upload=="
oldtext=m[inpl]
s=wikipedia.interwikiFormat(new)
s2=wikipedia.removeLanguageLinks(oldtext)
newtext=s+s2
if debug:
    if not autonomous and not sys.platform=='win32':
        f=open('/tmp/wik.in','w')
        f.write(oldtext)
        f.close()
        f=open('/tmp/wik.out','w')
        f.write(newtext)
        f.close()
        import os
        f=os.popen('diff -u /tmp/wik.in /tmp/wik.out','r')
        print f.read()
    else:
        print s
if newtext!=oldtext:
    print "NOTE: Replacing %s: %s"%(mylang,inname)
    if forreal:
        if ask:
            if confirm:
                if bell:
                    sys.stdout.write('\07')
                autonomous_problem(inname)
                answer=raw_input('submit y/n ?')
            else:
                answer='y'
        else:
            answer='y'
        if answer=='y':
            status,reason,data=wikipedia.putPage(mylang,inname,newtext,comment='%s: robot '%wikipedia.username+mods)
            if str(status)!='302':
                print status,reason
