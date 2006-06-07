# -*- coding: utf-8  -*-
#
# (C) Rob W.W. Hooft, 2003
# (C) Yuri Astrakhan, 2005
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#
import re

import wikipedia, date

def sametranslate(pl, arr, same):
    site = pl.site()
    for newcode in site.family.languages_by_size:
        newsite = wikipedia.Site(newcode, site.family)
        if pl.namespace() == 0:
            newname = pl.title()
        else:
            # Translate the namespace
            newname = '%s:%s' % (newsite.namespace(pl.namespace()), pl.titleWithoutNamespace())
        # On the Esperanto Wikipedia given names are written in all-capital
        # letters.
        if newcode == 'eo' and same == 'name':
            newname = newname.split(' ')
            newname[-1] = newname[-1].upper()
            newname = ' '.join(newname)
        x=wikipedia.Page(wikipedia.getSite(code=newcode, fam=site.family), newname)
        try:
            x2=wikipedia.Page(wikipedia.getSite(code=newcode, fam=site.family), newname[0].lower() + newname[1:])
        except IndexError:
            x2=wikipedia.Page(wikipedia.getSite(code=newcode, fam=site.family), newname)
        if x not in arr:
            if same == "wiktionary":
                if site.language() in site.family.nocapitalize:
                    if newcode in site.family.nocapitalize:
                        arr[x] = None
                    elif pl.title()[0].upper() == pl.title()[0]:
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
                newname = pl.title()
            try:
                number = int(codes)
                codes = site.family.languages_by_size[:number]
            except ValueError:
                if codes == 'all':
                    codes = site.family.languages_by_size
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
        dictName, value = date.getAutoFormat( pl.site().language(), pl.title() )
        if dictName:
            if not (dictName == 'yearsBC' and date.maxyearBC.has_key(pl.site().language()) and value > date.maxyearBC[pl.site().language()]) or (dictName == 'yearsAD' and date.maxyearAD.has_key(pl.site().language()) and value > date.maxyearAD[pl.site().language()]):
                wikipedia.output(u'TitleTranslate: %s was recognized as %s with value %d' % (pl.title(),dictName,value))
                for entryLang, entry in date.formats[dictName].iteritems():
                    if entryLang != pl.site().language():
                        if dictName == 'yearsBC' and date.maxyearBC.has_key(entryLang) and value > date.maxyearBC[entryLang]:
                            pass
                        elif dictName == 'yearsAD' and date.maxyearAD.has_key(entryLang) and value > date.maxyearAD[entryLang]:
                            pass
            else:
                            newname = entry(value)
                            x = wikipedia.Page( wikipedia.getSite(code=entryLang, fam=site.family), newname )
                            if x not in arr:
                                arr[x] = None   # add new page

bcDateErrors = [u'[[ko:%d년]]']

def appendFormatedDates( result, dictName, value ):
    for code, func in date.formats[dictName].iteritems():
        result.append( u'[[%s:%s]]' % (code,func(value)) )
    
def getPoisonedLinks(pl):
    """Returns a list of known corrupted links that should be removed if seen
    """
    result = []
    
    wikipedia.output( u'getting poisoned links for %s' % pl.title() )

    dictName, value = date.getAutoFormat( pl.site().language(), pl.title() )
    if dictName is not None:
        wikipedia.output( u'date found in %s' % dictName )
        
        # errors in year BC
        if dictName in date.bcFormats:
            for fmt in bcDateErrors:
                result.append( fmt % value )

        # i guess this is like friday the 13th for the years
        if value == 398 and dictName == 'yearsBC':
            appendFormatedDates( result, dictName, 399 )
        
        if dictName == 'yearsBC':
            appendFormatedDates( result, 'decadesBC', value )
            appendFormatedDates( result, 'yearsAD', value )

        if dictName == 'yearsAD':
            appendFormatedDates( result, 'decadesAD', value )
            appendFormatedDates( result, 'yearsBC', value )

        if dictName == 'centuriesBC':
            appendFormatedDates( result, 'decadesBC', value*100+1 )

        if dictName == 'centuriesAD':
            appendFormatedDates( result, 'decadesAD', value*100+1 )

    return result
