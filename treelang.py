#coding: iso-8859-1
"""
Script to check language links for general pages. This works by downloading the
page, and using existing translations plus hints from the command line to
download the equivalent pages from other languages. All of such pages are
downloaded as well and checked for interwiki links recursively until there are
no more links that are encountered. A rationalization process then selects the
right interwiki links, and if this is unambiguous, the interwiki links in the
original page will be automatically updated and the modified page uploaded.

This script understands various command-line arguments:
    -force: do not ask permission to make "controversial" changes, like
            removing a language because none of the found alternatives actually
            exists.
    -always: make changes even when a single byte is changed in the page,
             not only when one of the links has a significant change.
    -same: try to translate the page to other languages by testing whether
           a page with the same name exists on each of the other known 
           wikipedias
    -hint: used as -hint:de:Anweisung to give the robot a hint where to
           start looking for translations
    -name: similar to -same, but UPPERCASE the last name for eo:
    -untranslated: untranslated pages are not skipped; instead in those
                   cases interactively a translation hint is asked of the user.
    -confirm: ask for confirmation in all cases. Without this argument, 
              additions and unambiguous modifications are made without
              confirmation.
    -autonomous: run automatically, do not ask any questions. If a question
                 to an operator is needed, write the name of the page
                 to autonomous_problems.dat and terminate.
    -backlink: check for references between the foreign pages as well, list 
              all those that are missing as WARNINGs.
    -log: log to the file treelang.log as well as printing to the screen.

    Arguments that are interpreted by more bot:

    -lang: specifies the language the bot is run on (e.g. -lang:de).
           Overwrites the settings in username.dat
    
     All other arguments are words that make up the page name.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import sys, copy, wikipedia, re

# Summary used in the modification request
wikipedia.setAction('semi-automatic interwiki script')

debug = 1
forreal = 1

datetablelang = 'nl'
datetable = {
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

yearADfmt = {'ja':'%d&#24180;'} # Others default to '%d'

yearBCfmt = {'da':'%d f.Kr.','de':'%d v. Chr.',
             'en':'%d BC','fr':'-%d','pl':'%d p.n.e.',
             'es':'%d adC','eo':'-%d','nl':'%d v. Chr.'} # No default

msg = {
    'en':('Adding','Removing','Modifying'),
    'nl':('Erbij','Eraf','Anders'),
    'da':('Tilføjer','Fjerner','Ændrer'),
    'fr':('Ajoute','Retire','Modifie')
    }

class Logger:
    """A class that replaces a standard output file by a logfile PLUS the
       standard output. This is used by the "log" option."""
    def __init__(self, original, filename='treelang.log'):
        self.original = original
        self.f = open(filename, 'a')

    def write(self, s):
        self.f.write(s)
        self.original.write(s)
        self.flush()
        
    def flush(self):
        self.f.flush()
        self.original.flush()
        
def autonomous_problem(pl, reason = ''):
    if autonomous:
        f=open('autonomous_problem.dat', 'a')
        f.write("%s {%s}\n" % (pl, reason))
        f.close()
        sys.exit(1)
    
def sametranslate(pl, arr):
    for newcode in wikipedia.seriouslangs:
        # Put as suggestion into array
        newname = pl.linkname()
        if newcode in ['eo','cs'] and same == 'name':
            newname = newname.split(' ')
            newname[-1] = newname[-1].upper()
            newname = ' '.join(newname)
        x=wikipedia.PageLink(newcode, newname)
        if x not in arr:
            arr[x] = None
    
def autotranslate(pl, arr, same=0):
    if same:
        return sametranslate(pl, arr)
    if hints:
        for h in hints:
            codes, newname=h.split(':')
            if codes == 'all':
                codes = wikipedia.biglangs
            else:
                codes = codes.split(',')
            for newcode in codes:
                x = wikipedia.PageLink(newcode, newname)
                if x not in arr:
                    arr[x] = None
    # Autotranslate dates into some other languages, the rest will come from
    # existing interwiki links.
    if wikipedia.mylang == datetablelang:
        Rdate = re.compile('(\d+)_(%s)' % ('|'.join(datetable.keys())))
        m = Rdate.match(pl.linkname())
        if m:
            for newcode, fmt in datetable[m.group(2)].items():
                newname = fmt % int(m.group(1))
                x = wikipedia.PageLink(newcode,newname)
                if x not in arr:
                    arr[x] = None
            return

    # Autotranslate years A.D.
    Ryear = re.compile('^\d+$')
    m = Ryear.match(pl.linkname())
    if m:
        for newcode in wikipedia.langs:
            fmt = yearADfmt.get(newcode, '%d')
            newname = fmt%int(m.group(0)) 
            x=wikipedia.PageLink(newcode, newname)
            if x not in arr:
                arr[x] = None
        return

    # Autotranslate years B.C.
    if wikipedia.mylang == 'nl':
        Ryear = re.compile('^(\d+)_v._Chr.')
        m = Ryear.match(pl.linkname())
        if m:
            for newcode in wikipedia.langs:
                fmt = yearBCfmt.get(newcode)
                if fmt:
                    newname = fmt % int(m.group(1))
                    x=wikipedia.PageLink(newcode, newname)
                    if x not in arr:
                        arr[x] = None
            return
    
def compareLanguages(old, new):
    global confirm
    removing = []
    adding = []
    modifying = []
    for code in old.keys():
        if code not in new.keys():
            confirm += 1
            removing.append(code)
        elif old[code] != new[code]:
            modifying.append(code)

    for code2 in new.keys():
        if code2 not in old.keys():
            adding.append(code2)
    s = ""
    if adding:
        s = s + " %s:" % (msg[msglang][0]) + ",".join(adding)
    if removing: 
        s = s + " %s:" % (msg[msglang][1]) + ",".join(removing)
    if modifying:
        s = s + " %s:" % (msg[msglang][2]) + ",".join(modifying)
    return s

#===========
exceptions = []

Re = re.compile(r'\[\[(.*)\]\] *< *\[\[(.*)\]\]')
try:
    f = open('%s-exceptions.dat' % wikipedia.mylang)
except IOError:
    pass
else:
    for line in f:
        m = Re.match(line)
        if not m:
            raise ValueError("Do not understand %s"%line)
        exceptions.append((m.group(1),m.group(2)))

def bigger(pl):
    if pl.hashname():
        # If we refer to part of the page, it is bigger
        return True
    x1 = str(inpl)
    x2 = str(pl)
    for small,big in exceptions:
        if small == x1 and big == x2:
            return True
    return False
        
#===========
    
def treestep(arr, pl, abort_on_redirect = 0):
    assert arr[pl] is None
    print "Getting %s"%pl
    n = 0
    try:
        text = pl.get()
    except wikipedia.NoPage:
        print "---> Does not actually exist"
        arr[pl] = ''
        return 0
    except wikipedia.LockedPage:
        print "---> Locked"
        arr[pl] = 1
        return 0
    except wikipedia.IsRedirectPage,arg:
        if abort_on_redirect and pl.code() == wikipedia.mylang:
            raise
        newpl = wikipedia.PageLink(pl.code(), str(arg))
        arr[pl] = ''
        print "NOTE: %s is a redirect to %s" % (pl, newpl)
        if not newpl in arr:
            arr[newpl] = None
            return 1
        return 0
    arr[pl] = text
    if bigger(pl):
        print "NOTE: %s is bigger than %s, not following references" % (pl, inpl)
    else:
        for newpl in pl.interwiki():
            if newpl not in arr:
                print "NOTE: from %s we got the new %s"%(pl,newpl)
                arr[newpl] = None
                n += 1
    return n
    
def treesearch(pl):
    arr = {pl:None}
    # First make one step based on the language itself
    try:
        n = treestep(arr, pl, abort_on_redirect = 1)
    except wikipedia.IsRedirectPage:
        print "Is redirect page"
        return
    if n == 0 and not arr[pl]:
        print "Mother doesn't exist"
        return
    if untranslated:
        if len(arr) > 1:
            print "Already has translations"
        else:
            if bell:
                sys.stdout.write('\07')
            newhint = raw_input("Hint:")
            if not newhint:
                return
            hints.append(newhint)
    # Then add translations if we survived.
    autotranslate(pl, arr, same = same)
    modifications = 1
    while modifications:
        modifications = 0
        for newpl in arr.keys():
            if arr[newpl] is None:
                modifications += treestep(arr, newpl)
    return arr

inname = []

bell = 1
ask = 1
same = 0
log = 0
only_if_status = 1
confirm = 0
autonomous = 0
untranslated = 0
backlink = 0
hints = []

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg == '-force':
        ask = False
    elif arg == '-always':
        only_if_status = False
    elif arg == '-backlink':
        backlink = True
    elif arg == '-same':
        same = True
    elif arg == '-untranslated':
        untranslated = True
    elif arg.startswith('-hint:'):
        hints.append(arg[6:])
    elif arg == '-name':
        same = 'name'
    elif arg == '-confirm':
        confirm = True
    elif arg == '-autonomous':
        autonomous = True
        bell = 0
    elif arg=='-log':
        log = 1
    else:
        inname.append(arg)

if msg.has_key(wikipedia.mylang):
    msglang = wikipedia.mylang
else:
    msglang = 'en'

if log:
    sys.stdout = Logger(sys.stdout)
    
inname = '_'.join(inname)
if not inname:
    inname = raw_input('Which page to check:')

inpl = wikipedia.PageLink(wikipedia.mylang, inname)

m = treesearch(inpl)
if not m:
    print "No matrix"
    sys.exit(1)
print "==Result=="
new = {}
k = m.keys()
k.sort()
for pl in k:
    if pl.code() == wikipedia.mylang and m[pl]:
        if pl!=inpl:
            print "ERROR: %s refers back to %s" % (inpl, pl)
            confirm += 1
            autonomous_problem(inpl, 'Someone refers to %s with us' % pl)
    elif m[pl]:
        print pl
        if new.has_key(pl.code()) and new[pl.code()] != None and new[pl.code()]!=pl:
            print "ERROR: '%s' as well as '%s'" % (new[pl.code()], pl)
            autonomous_problem(inpl,"'%s' as well as '%s'" % (new[pl.code()], pl))
            while 1:
                if bell:
                    sys.stdout.write('\07')
                confirm += 1
                answer = raw_input("Use (f)ormer or (l)atter or (n)either or (q)uit?")
                if answer.startswith('f'):
                    break
                elif answer.startswith('l'):
                    new[pl.code()] = pl
                    break
                elif answer.startswith('n'):
                    new[pl.code()] = None
                    break
                elif answer.startswith('q'):
                    sys.exit(1)
        elif pl.code() not in new or new[pl.code()] != None:
            new[pl.code()] = pl

# Remove the neithers
for k,v in new.items():
    if v is None:
        del new[k]
        
print "==status=="
old={}
for pl in inpl.interwiki():
    old[pl.code()] = pl
####
mods=compareLanguages(old, new)
if not mods and only_if_status:
    print "No changes"
else:
    print mods
    print "==changes should be made=="
    oldtext = m[inpl]
    s = wikipedia.interwikiFormat(new, incode = wikipedia.mylang)
    s2 = wikipedia.removeLanguageLinks(oldtext)
    newtext = s + s2
    if debug:
        if not autonomous and not sys.platform == 'win32':
            f = open('/tmp/wik.in', 'w')
            f.write(wikipedia.forCode(oldtext, 'ascii'))
            f.close()
            f = open('/tmp/wik.out', 'w')
            f.write(wikipedia.forCode(newtext, 'ascii'))
            f.close()
            import os
            f=os.popen('diff -u /tmp/wik.in /tmp/wik.out', 'r')
            print f.read()
        else:
            print s
    if newtext != oldtext:
        print "NOTE: Replace %s: %s" % (wikipedia.mylang, inname)
        if forreal:
            if ask:
                if confirm:
                    if bell:
                        sys.stdout.write('\07')
                    autonomous_problem(inpl, 'removing a language')
                    answer = raw_input('submit y/n ?')
                else:
                    answer = 'y'
            else:
                answer = 'y'
            if answer == 'y':
                status, reason, data = wikipedia.putPage(wikipedia.mylang, inname, newtext,
                                                         comment='robot '+mods)
                if str(status) != '302':
                    print status, reason

if backlink:
    for code in new.keys():
        pl = new[code]
        if not bigger(pl):
            shouldlink = new.values() + [inpl]
            linked = pl.interwiki()
            for xpl in shouldlink:
                if xpl != pl and not xpl in linked:
                    for l in linked:
                        if l.code() == xpl.code():
                            print "WARNING:", pl.asselflink(), "does not link to", xpl.aslink(), "but to", l.aslink()
                            break
                    else:
                        print "WARNING:", pl.asselflink(), "does not link to", xpl.aslink()
            # Check for superfluous links
            for xpl in linked:
                if not xpl in shouldlink:
                    # Check whether there is an alternative page on that language.
                    for l in shouldlink:
                        if l.code() == xpl.code():
                            # Already reported above.
                            break
                    else:
                        # New warning
                        print "WARNING:", pl.asselflink(), "links to incorrect", xpl.aslink()
