#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import re

import wikipedia, date

def sametranslate(pl, arr, same):
    site = pl.site()
    for newcode in site.family.seriouslangs:
        # Put as suggestion into array
        newname = pl.linkname()
        if newcode in ['eo','cs'] and same == 'name':
            newname = newname.split(' ')
            newname[-1] = newname[-1].upper()
            newname = ' '.join(newname)
        x=wikipedia.PageLink(wikipedia.getSite(code=newcode, fam=site.family), newname)
        x2=wikipedia.PageLink(wikipedia.getSite(code=newcode, fam=site.family), newname[0].lower() + newname[1:])
        if x not in arr:
            if same == "wiktionary":
                if site.language() in site.family.nocapitalize:
                    if newcode in site.family.nocapitalize:
                        arr[x] = None
                    elif pl.linkname()[0].upper() == pl.linkname()[0]:
                        arr[x] = None
                else:
                    arr[x] = None
                    if newcode in site.family.nocapitalize:
                        arr[x2] = None
            else:
                arr[x] = None

def translate(pl, arr, same = False, hints = None, auto = True):
    site = pl.site()
    if same:
        return sametranslate(pl, arr, same)
    if hints:
        for h in hints:
            if h.find(':') == -1:
                # argument given as -hint:xy where xy is a language code
                codes = h
                newname = ''
            else:
                codes, newname = h.split(':', 1)
            if newname == '':
                # if given as -hint:xy or -hint:xy:, assume that there should
                # be a page in language xy with the same title as the page 
                # we're currently working on
                newname = pl.linkname()
            if codes == 'all':
                codes = site.family.seriouslangs
            elif codes == '10' or codes == 'main': # names 'main' and 'more' kept for backward compatibility
                codes = site.family.biglangs
            elif codes == '20' or codes == 'more':
                codes = site.family.biglangs2
            elif codes == '30':
                codes = site.family.biglangs3
            elif codes == '50':
                codes = site.family.biglangs4
            elif codes == 'cyril':
                codes = site.family.cyrilliclangs
            else:
                codes = codes.split(',')
            for newcode in codes:
                if newcode in site.languages():
                    if newcode != site.language():
                        x = wikipedia.PageLink(site.getSite(code=newcode), newname)
                        if x not in arr:
                            arr[x] = None
                else:
                    wikipedia.output(u"Ignoring unknown language code %s"%newcode)
    # Autotranslate dates into some other languages, the rest will come from
    # existing interwiki links.
    if date.datetable.has_key(site.lang) and auto:
        dt='(\d+) (%s)' % ('|'.join(date.datetable[site.lang].keys()))
        Rdate = re.compile(dt)
        m = Rdate.match(pl.linkname())
        if m:
            for newcode, fmt in date.date_format[date.datetable[site.lang][m.group(2)]].items():
                newname = fmt % int(m.group(1))
                x = wikipedia.PageLink(wikipedia.getSite(code=newcode, fam=site.family),newname)
                if x not in arr:
                    arr[x] = None
            return

    # Autotranslate years A.D.
    Ryear = re.compile('^\d+$')
    m = Ryear.match(pl.linkname())
    if m and auto:
        i=int(m.group(0))
        if i==0:
            return
        if site.lang in date.yearADfmt:
            # These have different texts for years
            return
        if site.lang in ['ia','la'] and i<1400:
            return
        if site.lang in ['simple','lt'] and i<200:
            return
        for newcode in site.family.seriouslangs:
            if newcode in date.yearADfmt:
                fmt = date.yearADfmt[newcode]
            else:
                fmt = '%d'
            if newcode == 'ja' and i<1900:
                # ja pages before 1900 are redirects
                pass
            elif newcode in ['ia','la'] and i<1400:
                # some ia pages are numbers
                pass
            elif newcode in ['simple','lt'] and i<200:
                # some simple pages are numbers
                # lt:69 has yet another meaning
                pass
            elif newcode=='es' and i>2005:
                # es: redirects future years to a single page
                pass
            elif newcode=='no' and i>2010:
                # no: redirects far future years to the century
                pass
            elif newcode=='ja' and i>2015:
                # ja: redirects far future years to decades
                pass
            elif newcode=='pl' and i>2019:
                # pl: redirects far future years to decades
                pass
            elif newcode=='fi' and i==666:
                # Yet another case of a number with another meaning
                pass
            else:
                newname = fmt%i 
                x=wikipedia.PageLink(wikipedia.getSite(code=newcode, fam=site.family), newname)
                if x not in arr:
                    arr[x] = None
        return

    # Autotranslate years B.C.
    if date.yearBCfmt.has_key(site.lang) and auto:
        dt=date.yearBCfmt[site.lang]
        dt = re.compile('%d').sub('(\d+)',dt)
        Ryear = re.compile(dt)
        m = Ryear.match(pl.linkname())
        if m:
            m = int(m.group(1))
            for newcode in site.family.seriouslangs:
                include = True
                if date.maxyearBC.has_key(newcode):
                    if m > date.maxyearBC[newcode]:
                        include = False
                if include:
                    fmt = date.yearBCfmt.get(newcode)
                    if fmt:
                        newname = fmt % m
                        x=wikipedia.PageLink(wikipedia.getSite(code=newcode, fam=site.family), newname)
                        if x not in arr:
                            arr[x] = None
            return
