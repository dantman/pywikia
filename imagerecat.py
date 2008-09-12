# -*- coding: utf-8 -*-
"""
Program to (re)categorize images at commons.

The program uses commonshelper for category suggestions.
It takes the suggestions and the current categories. Put the categories through some filters and add the result

"""
__version__ = '$Id$'
#
#  (C) Multichill 2008
#  (tkinter part loosely based on imagecopy.py)
# Distributed under the terms of the MIT license.
#
#
import os, sys, re, codecs
import urllib, httplib, urllib2
import catlib
import time
import wikipedia, config
import pagegenerators, StringIO
import socket

category_blacklist = []
countries = []

def initLists():
    '''
    Get the list of countries & the blacklist from Commons.
    '''
    global category_blacklist
    global countries

    blacklistPage = wikipedia.Page(wikipedia.getSite(), u'User:Multichill/Category_blacklist')
    for cat in blacklistPage.linkedPages():
        category_blacklist.append(cat.titleWithoutNamespace())

    countryPage = wikipedia.Page(wikipedia.getSite(), u'User:Multichill/Countries')
    for country in countryPage.linkedPages():
        countries.append(country.titleWithoutNamespace())
    return

def categorizeImages(generator, onlyfilter):
    '''
    Loop over all images in generator and try to categorize them. Get category suggestions from CommonSense.
    '''
    for page in generator:
        if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()):
            imagepage = wikipedia.ImagePage(page.site(), page.title())
            #imagepage.get()
            wikipedia.output(u'Working on ' + imagepage.title());
            currentCats = getCurrentCats(imagepage)
            if(onlyfilter):
                commonshelperCats = []
            else:
                commonshelperCats = getCommonshelperCats(imagepage)
            newcats = applyAllFilters(commonshelperCats+currentCats)

            if (len(newcats) > 0 and not(set(currentCats)==set(newcats))):
                for cat in newcats:
                    wikipedia.output(u' Found new cat: ' + cat);
                saveImagePage(imagepage, newcats, onlyfilter)


def getCurrentCats(imagepage):
    '''
    Get the categories currently on the image
    '''
    result = []
    for cat in imagepage.categories():
        result.append(cat.titleWithoutNamespace())
    return list(set(result))


def getCommonshelperCats(imagepage):
    '''
    Get category suggestions from CommonSense. Parse them and return a list of suggestions.
    '''
    result = []
    parameters = urllib.urlencode({'i' : imagepage.titleWithoutNamespace().encode('utf-8'), 'r' : 'on', 'go-clean' : 'Find+Categories', 'cl' : 'li'})
    commonsenseRe = re.compile('^#COMMONSENSE(.*)#USAGE(\s)+\((?P<usage>(\d)+)\)(.*)#KEYWORDS(\s)+\((?P<keywords>(\d)+)\)(.*)#CATEGORIES(\s)+\((?P<catnum>(\d)+)\)\s(?P<cats>(.*))\s#GALLERIES(\s)+\((?P<galnum>(\d)+)\)(.*)#EOF$', re.MULTILINE + re.DOTALL)

    gotInfo = False;

    while(not gotInfo):
        try:
            commonsHelperPage = urllib.urlopen("http://toolserver.org/~daniel/WikiSense/CommonSense.php?%s" % parameters)
            matches = commonsenseRe.search(commonsHelperPage.read().decode('utf-8'))
            gotInfo = True
        except IOError:
            wikipedia.output(u'Got an IOError, let\'s try again')
        except socket.timeout:
            wikipedia.output(u'Got a timeout, let\'s try again')

    if matches:
        if(matches.group('catnum') > 0):
            categories = matches.group('cats').splitlines()
            for cat in categories:
                result.append(cat.replace('_',' '))

    return list(set(result))


def applyAllFilters(categories):
    result = []
    result = filterBlacklist(categories)
    result = filterDisambiguation(result)
    result = followRedirects(result)
    result = filterCountries(result)
    result = filterParents(result)
    return result


def filterBlacklist(categories):
    '''
    Filter out categories which are on the blacklist.
    '''
    result = []
    for cat in categories:
        if (cat not in category_blacklist):
            result.append(cat)
    return list(set(result))


def filterDisambiguation(categories):
    '''
    Filter out disambiguation categories.
    '''
    result = []
    for cat in categories:
        if(not wikipedia.Page(wikipedia.getSite(), u'Category:' + cat).isDisambig()):
            result.append(cat)
    return result

def followRedirects(categories):
    '''
    If a category is a redirect, replace the category with the target.
    '''
    result = []
    for cat in categories:
        categoryPage = wikipedia.Page(wikipedia.getSite(), u'Category:' + cat)
        if u'Category redirect' in categoryPage.templates() or u'Seecat' in categoryPage.templates():
            for template in categoryPage.templatesWithParams():
                if ((template[0]==u'Category redirect' or template[0]==u'Seecat') and (len(template[1]) > 0)):
                    result.append(template[1][0])
        else:
            result.append(cat)
    return result


def filterCountries(categories):
    '''
    Try to filter out ...by country categories.
    First make a list of any ...by country categories and try to find some countries.
    If a by country category has a subcategoy containing one of the countries found, add it.
    The ...by country categories remain in the set and should be filtered out by filterParents.
    '''
    result = categories
    listByCountry = []
    listCountries = []
    for cat in categories:
        if (cat.endswith(u'by country')):
            listByCountry.append(cat)

        #If cat contains 'by country' add it to the list
        #If cat contains the name of a country add it to the list
        else:
            for country in countries:
                if not(cat.find(country)==-1):
                    listCountries.append(country)

    if(len(listByCountry) > 0):
        for bc in listByCountry:
            category = catlib.Category(wikipedia.getSite(), u'Category:' + bc)
            for subcategory in category.subcategories():
                for country in listCountries:
                    if (subcategory.titleWithoutNamespace().endswith(country)):
                        result.append(subcategory.titleWithoutNamespace())

    return list(set(result))


def filterParents(categories):
    '''
    Remove all parent categories from the set to prevent overcategorization.
    '''
    result = []
    toFilter = u''

    for cat in categories:
        cat = cat.replace('_',' ')
        toFilter = toFilter + "[[Category:" + cat + "]]\n"
    #try:
    parameters = urllib.urlencode({'source' : toFilter.encode('utf-8'), 'bot' : '1'})
    filterCategoriesPage = urllib.urlopen("http://toolserver.org/~multichill/filtercats.php?%s" % parameters)
    #print filterCategoriesPage.read().decode('utf-8')
    filterCategoriesRe = re.compile('\[\[Category:([^\]]*)\]\]')
    result = filterCategoriesRe.findall(filterCategoriesPage.read().decode('utf-8'))
    #except:

    return result


def saveImagePage(imagepage, newcats, onlyfilter):
    '''
    Remove the old categories and add the new categories to the image.
    '''
    newtext = wikipedia.removeCategoryLinks(imagepage.get(), imagepage.site())    

    if not(onlyfilter):
        newtext = removeTemplates(newtext)
        newtext = newtext + u'{{subst:chc}}\n'
    for category in newcats:
        newtext = newtext + u'[[Category:' + category + u']]\n'

    if(onlyfilter):
        comment = u'Filtering categories'
    else:
        comment = u'Image is categorized by a bot using data from [[Commons:Tools#CommonSense|CommonSense]]'

    wikipedia.showDiff(imagepage.get(), newtext)
    imagepage.put(newtext, comment)
    return


def removeTemplates(oldtext = u''):
    '''
    Remove {{Uncategorized}} and {{Check categories}} templates
    '''
    result = u''
    result = re.sub(u'\{\{\s*([Uu]ncat(egori[sz]ed( image)?)?|[Nn]ocat|[Nn]eedscategory)[^}]*\}\}', u'', oldtext)
    result = re.sub(u'<!-- Remove this line once you have added categories -->', u'', result)
    result = re.sub(u'\{\{\s*[Cc]heck categories[^}]*\}\}', u'', result)
    return result


def main(args):
    '''
    Main loop. Get a generator. Set up the 3 threads and the 2 queue's and fire everything up.
    '''
    generator = None
    onlyfilter = False
    genFactory = pagegenerators.GeneratorFactory()

    site = wikipedia.getSite(u'commons', u'commons')
    wikipedia.setSite(site)
    for arg in wikipedia.handleArgs():
        if arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(site, wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(site, arg[6:])]
        elif arg == '-onlyfilter':
            onlyfilter = True
        else:
            generator = genFactory.handleArg(arg)
    if not generator:
        generator = pagegenerators.CategorizedPageGenerator(catlib.Category(site, u'Category:Media needing categories'), recurse=True)

    initLists()
    categorizeImages(generator, onlyfilter)

    wikipedia.output(u'All done')

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
