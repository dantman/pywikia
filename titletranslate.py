#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import re

import wikipedia

datetable = {'nl':
             {
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
    }}

yearBCfmt = {'da':'%d f.Kr.','de':'%d v. Chr.',
             'en':'%d BC','fr':'-%d','pl':'%d p.n.e.',
             'es':'%d adC','eo':'-%d','nl':'%d v. Chr.'} # No default
    
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

def translate(pl, arr, same = False, hints = None):
    if same:
        return sametranslate(pl, arr)
    if hints:
        for h in hints:
            codes, newname = h.split(':', 1)
            if codes == 'all':
                codes = wikipedia.seriouslangs
            elif codes == 'main':
                codes = wikipedia.biglangs
            else:
                codes = codes.split(',')
            for newcode in codes:
                x = wikipedia.PageLink(newcode, newname)
                if x not in arr:
                    arr[x] = None
    # Autotranslate dates into some other languages, the rest will come from
    # existing interwiki links.
    if datetable.has_key(wikipedia.mylang):
        Rdate = re.compile('(\d+)_(%s)' % ('|'.join(datetable[wikipedia.mylang].keys())))
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
        for newcode in wikipedia.seriouslangs:
            if newcode!='ja':
                fmt = '%d'
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
            for newcode in wikipedia.seriouslangs:
                fmt = yearBCfmt.get(newcode)
                if fmt:
                    newname = fmt % int(m.group(1))
                    x=wikipedia.PageLink(newcode, newname)
                    if x not in arr:
                        arr[x] = None
            return
