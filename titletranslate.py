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
    'januari':{  'sl':'%d. januar',    'it':'%d gennaio',   'en':'January %d',   'de':'%d. Januar',    'fr':'%d janvier',   'af':'01-%02d', 'ca':'%d de gener',       'oc':'%d de geni%%C3%%A8r',  },
    'februari':{ 'sl':'%d. februar',   'it':'%d febbraio',  'en':'February %d',  'de':'%d. Februar',   'fr':'%d fevrier',   'af':'02-%02d', 'ca':'%d de febrer',      'oc':'%d de febri%%C3%%A8r', },
    'maart':{    'sl':'%d. marec',     'it':'%d marzo',     'en':'March %d',     'de':'%d. M&auml;rz', 'fr':'%d mars',      'af':'03-%02d', 'ca':'%d de_mar%%C3%%A7', 'oc':'%d de_mar%%C3%%A7',    },
    'april':{    'sl':'%d. april',     'it':'%d aprile',    'en':'April %d',     'de':'%d. April',     'fr':'%d avril',     'af':'04-%02d', 'ca':'%d d\'abril',       'oc':'%d d\'abril',          },
    'mei':{      'sl':'%d. maj',       'it':'%d maggio',    'en':'May %d',       'de':'%d. Mai',       'fr':'%d mai',       'af':'05-%02d', 'ca':'%d de maig',        'oc':'%d de mai',            },
    'juni':{     'sl':'%d. junij',     'it':'%d giugno',    'en':'June %d',      'de':'%d. Juni',      'fr':'%d juin',      'af':'06-%02d', 'ca':'%d de juny',        'oc':'%d de junh',           },
    'juli':{     'sl':'%d. julij',     'it':'%d luglio',    'en':'July %d',      'de':'%d. Juli',      'fr':'%d juillet',   'af':'07-%02d', 'ca':'%d de juliol',      'oc':'%d de julhet',         },
    'augustus':{ 'sl':'%d. avgust',    'it':'%d agosto',    'en':'August %d',    'de':'%d. August',    'fr':'%d aout',      'af':'08-%02d', 'ca':'%d d\'agost',       'oc':'%d d\'agost',          },
    'september':{'sl':'%d. september', 'it':'%d settembre', 'en':'September %d', 'de':'%d. September', 'fr':'%d septembre', 'af':'09-%02d', 'ca':'%d de setembre',    'oc':'%d de setembre',       },
    'oktober':{  'sl':'%d. oktober',   'it':'%d ottobre',   'en':'October %d',   'de':'%d. Oktober',   'fr':'%d octobre',   'af':'10-%02d', 'ca':'%d d\'octubre',     'oc':'%d d\'octobre',        },
    'november':{ 'sl':'%d. november',  'it':'%d novembre',  'en':'November %d',  'de':'%d. November',  'fr':'%d novembre',  'af':'11-%02d', 'ca':'%d de novembre',    'oc':'%d de novembre',       },
    'december':{ 'sl':'%d. december',  'it':'%d dicembre',  'en':'December %d',  'de':'%d. Dezember',  'fr':'%d decembre',  'af':'12-%02d', 'ca':'%d de desembre',    'oc':'%d de decembre',       },
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
        dt='(\d+) (%s)' % ('|'.join(datetable[wikipedia.mylang].keys()))
        Rdate = re.compile(dt)
        m = Rdate.match(pl.linkname())
        if m:
            for newcode, fmt in datetable[wikipedia.mylang][m.group(2)].items():
                newname = fmt % int(m.group(1))
                x = wikipedia.PageLink(newcode,newname)
                if x not in arr:
                    arr[x] = None
            return

    # Autotranslate years A.D.
    Ryear = re.compile('^\d+$')
    m = Ryear.match(pl.linkname())
    if m:
        i=int(m.group(0))
        for newcode in wikipedia.seriouslangs:
            if newcode=='ja':
                fmt = '%d&#24180;'
            else:
                fmt = '%d'
            if newcode == 'ja' and i<1800:
                # ja pages before 1800 are redirects
                pass
            elif newcode == 'ia' and i<1980:
                # some ia pages are numbers
                pass
            elif newcode == 'la':
                # la pages are not years but numbers
                pass
            elif newcode == 'gl':
                # gl years do not exist
                pass
            elif newcode in ['eu', 'mr', 'id', 'lv', 'sw', 'tt']:
                # years do not exist
                pass
            elif newcode == 'nds' and i<2000 or i>2010:
                # nds years do not exist except for 2003
                pass
            else:
                newname = fmt%i 
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
