#coding: iso-8859-1
"""
This is a wikipedia robot.

Script to check language links for years A.D.

This uses the fact that almost all wikipedias have the years as plain number
page names and can be trivially translated to check if the equivalent exists in
another language. The exception for the Japanese wikipedia is hard-coded.

The range of years that is checked defaults to 1 through 2040. It can be changed
using the command line arguments -start:X and -end:Y. Like many other robots, the
home wikipedia can be changed using the -lang:XX argument.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import sys,copy,wikipedia

# Set to 1 to actually change the pages
forreal = 1

# Summary used in the modification request
wikipedia.setAction('automatic interwiki script for years')

debug = 0

def findlangs(year):
    matrix={}
    text={}
    print year,"=",
    missing=0
    for code in wikipedia.languages((wikipedia.mylang,)):
        print code+":", ; sys.stdout.flush()
        try:
            if code=='ja':
                t=wikipedia.getPage(code,year+'%E5%B9%B4')
            else:
                t=wikipedia.getPage(code,year)
        except wikipedia.NoPage:
            if code==wikipedia.mylang:
                missing+=1
                if missing==1:  #len(mylangs):
                    # None of the mylangs has this page. Doesn't make sense.
                    print
                    return None,None
        except wikipedia.IsRedirectPage,arg:
            if code==wikipedia.mylang:
                missing+=1
                if missing==1: #len(mylangs):
                    # None of the mylangs has this page. Doesn't make sense.
                    print
                    return None,None
        else:
            text[code]=t
            l=wikipedia.getLanguageLinks(t,incode=code)
            if code=='ja':
                l[code]=year+'&#24180;' # Add self-reference
            else:
                l[code]=year # Add self-reference
            matrix[code]=l
    print
    return text,matrix

def assemblelangmatrix(m):
    result={}
    for dum,line in m.iteritems():
        for code,name in line.iteritems():
            if not code in m:
                pass
                #print "WARNING: Ignore %s from %s; did not see actual page there"%(code,dum)
            elif code in result:
                if result[code]!=name:
                    print "WARNING: Name %s is either %s or (in %s) %s"%(code,result[code],dum,name)
            else:
                result[code]=name
    return result

def missingLanguages(m,line,thiscode):
    # Figure out whether any references in the assembled references mentioned in
    # line are missing from the language page referred by thiscode.
    result={}
    for code,name in line.iteritems():
        if code==thiscode:
            pass
        elif code in m[thiscode]:
            pass
        else:
            result[code]=name
    for code,name in m[thiscode].iteritems():
        if not code in line:
            print "WARNING: %s contains reference to unknown %s:%s"%(thiscode,code,name)
        elif line[code]!=name:
            print "WARNING: %s reference to %s is %s and not %s"%(thiscode,code,name,line[code])
    return result


msg = {
    'en':('Adding','Removing','Modifying'),
    'nl':('Erbij','Eraf','Anders'),
    'da':('Tilføjer','Fjerner','Ændrer'),
    'fr':('Ajoute','Retire','Modifie')
    }
    
def compareLanguages(old, new):
    """This is a copy of a routine from treelang.py"""
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

starty = 1
endy = 2040

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg.startswith('-start:'):
        starty = int(arg[7:])
    elif arg.startswith('-end:'):
        endy = int(arg[5:])
    else:
        print "Unknown argument",arg
        sys.exit(1)

if msg.has_key(wikipedia.mylang):
    msglang = wikipedia.mylang
else:
    msglang = 'en'

for year in range(starty, endy + 1):
    text,m=findlangs(str(year))
    if m is None:
        # None of the mylangs has this page
        continue
    proper=assemblelangmatrix(m)
    for mycode in (wikipedia.mylang,):
        if mycode in m: # Page must be present in this language
            ml=copy.copy(proper)
            status=compareLanguages(m[mycode],ml)
            if status:
                print mycode,str(year),":",status
            del ml[mycode]
            s=wikipedia.interwikiFormat(ml)
            newtext=s+wikipedia.removeLanguageLinks(text[mycode])
            if debug:
                print newtext
            if newtext!=text[mycode]:
                print "NOTE: Replacing %s: %s"%(mycode,s)
                if forreal:
                    status,reason,data=wikipedia.putPage(mycode,str(year),newtext,"Robot"+status)
                    if str(status)!='302':
                        print status,reason
