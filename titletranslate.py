# -*- coding: utf-8  -*-
#
# (C) Rob W.W. Hooft, 2003
# (C) Yuri Astrakhan, 2005
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
        x=wikipedia.Page(wikipedia.getSite(code=newcode, fam=site.family), newname)
        x2=wikipedia.Page(wikipedia.getSite(code=newcode, fam=site.family), newname[0].lower() + newname[1:])
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
                        x = wikipedia.Page(site.getSite(code=newcode), newname)
                        if x not in arr:
                            arr[x] = None
                else:
                    wikipedia.output(u"Ignoring unknown language code %s"%newcode)

    # Autotranslate dates into all other languages, the rest will come from existing interwiki links.
    if auto:
        # search inside all dictionaries for this link
        dictName, year = getDictionaryYear( pl.site().language(), pl.linkname() )
        if dictName:
            for entryLang, entry in date.dateFormats[dictName].iteritems():
                try:
                    if entryLang != pl.site().language():
                        if dictName == 'yearsBC' and date.maxyearBC.has_key(pl.site().language()) and year > date.maxyearBC[pl.site().language()]:
                            pass
                        newname = entry(year)
                        x = wikipedia.Page( wikipedia.getSite(code=newcode, fam=site.family), newname )
                        if x not in arr:
                            arr[x] = None   # add new page
                except:
                    pass

def getDictionaryYear( lang, linkname ):
    for dictName, dict in date.dateFormats.iteritems():
        try:
            year = dict[ lang ]( linkname )
            return (dictName,year)
        except:
            pass

    return (None,None)



bcDateErrors = [u'[[ko:%d년]]']
bcFormats = ['centuriesBC', 'decadesBC', 'milleniumsBC', 'yearsBC']
adFormats = ['centuriesAD','decadesAD','milleniumsAD','yearsAD']
monthFormats = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
decadeFormats = ['decadesAD','decadesBC']


def appendFormatedDates( result, dictName, year ):
    for code, value in date.dateFormats[dictName].iteritems():
        result.append( u'[[%s:%s]]' % (code,value(year)) )
    
def getPoisonedLinks(pl):
    """Returns a list of known corrupted links that should be removed if seen
    """
    result = []
    
    wikipedia.output( u'getting poisoned links for %s' % pl.linkname() )

    dictName, year = getDictionaryYear( pl.site().language(), pl.linkname() )
    if dictName != None:
        wikipedia.output( u'date found in %s' % dictName )
        
        # errors in year BC
        if dictName in bcFormats:
            for fmt in bcDateErrors:
                result.append( fmt % year )

        # i guess this is like friday the 13th for the years
        if year == 398 and dictName == 'yearsBC':
            appendFormatedDates( result, dictName, 399 )
        
        if dictName == 'yearsBC':
            appendFormatedDates( result, 'decadesBC', year )
            appendFormatedDates( result, 'yearsAD', year )

        if dictName == 'yearsAD':
            appendFormatedDates( result, 'decadesAD', year )
            appendFormatedDates( result, 'yearsBC', year )

        if dictName == 'centuriesBC':
            appendFormatedDates( result, 'decadesBC', year*100+1 )

        if dictName == 'centuriesAD':
            appendFormatedDates( result, 'decadesAD', year*100+1 )

    return result
    
def isDateBC( pl ):
    """Guesses if the name of this link matches with the date format
    """
    try:
        dt = date.yearBCfmt[ pl.site().lang ]
        Ryear = date.escapePattern( dt )
        m = Ryear.match(pl.linkname())
        if m:
            year = int(m.group(1))
            if dt % year == pl.linkname():
                return year
    except:
        pass
    return None


def isSpecialYear( pl, yearMapName ):
    """Guesses if the name of this link matches with the date format
    """
    year = None
    try:
        year = dateFormats[yearMapName][ pl.site().lang ]( pl.linkname() )
    except:
        pass
    return year

def isDecadesAD( pl ):
    return isSpecialYear( pl, 'decadesAD' )
    
def isDecadesBC( pl ):
    return isSpecialYear( pl, 'decadesBC' )

def isCenturiesBC( pl ):
    return isSpecialYear( pl, 'centuriesBC' )
