# -*- coding: utf-8 -*-
"""
Program to (re)categorize images at commons.

The program uses commonshelper for category suggestions.
It takes the suggestions and the current categories. Put the categories through some filters and add the result

"""
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

category_blacklist = [u'Hidden categories',
                      u'Stub pictures']

def categorizeImages(generator):
    for page in generator:
        if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()):
            imagepage = wikipedia.ImagePage(page.site(), page.title())
            #imagepage.get()
            wikipedia.output(u'Working on ' + imagepage.title());
            currentCats = getCurrentCats(imagepage)
            commonshelperCats = getCommonshelperCats(imagepage)
            newcats = filterBlacklist(commonshelperCats+currentCats)
            newcats = filterDisambiguation(newcats)
            newcats = followRedirects(newcats)
            #newcats = filterCountries(newcats)
            newcats = filterParents(newcats)
            if len(newcats) > 0:
                for cat in newcats:
                    wikipedia.output(u' Found new cat: ' + cat);
                saveImagePage(imagepage, newcats)


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
    Get category suggestions from commonshelper. Parse them and return a list of suggestions.        
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


def filterBlacklist(categories):
    result = []
    for cat in categories:
        if (cat not in category_blacklist):
            result.append(cat)
    return list(set(result))


def filterDisambiguation(categories):
    result = []
    for cat in categories:
        if(not wikipedia.Page(wikipedia.getSite(), u'Category:' + cat).isDisambig()):
            result.append(cat)
    return result

def followRedirects(categories):
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
    result = []
    return result


def filterParents(categories):
    '''
    Remove the current categories from the suggestions and remove blacklisted cats.
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


def saveImagePage(imagepage, newcats):
    newtext = wikipedia.removeCategoryLinks(imagepage.get(), imagepage.site())
    newtext = removeTemplates(newtext) + u'{{subst:chc}}\n'
    for category in newcats:
        newtext = newtext + u'[[Category:' + category + u']]\n'
        
    wikipedia.showDiff(imagepage.get(), newtext)
    imagepage.put(newtext, u'Image is categorized by a bot using data from [[Commons:Tools#CommonSense|CommonSense]]')
    return


def removeTemplates(oldtext = u''):
    result = u''
    result = re.sub(u'\{\{\s*([Uu]ncat(egori[sz]ed( image)?)?|[Nn]ocat|[Nn]eedscategory)[^}]*\}\}', u'', oldtext)        
    result = re.sub(u'<!-- Remove this line once you have added categories -->', u'', result)
    result = re.sub(u'\{\{\s*[Cc]heck categories[^}]*\}\}', u'', result)
    return result         


def main(args):
    '''
    Main loop. Get a generator. Set up the 3 threads and the 2 queue's and fire everything up.
    '''
    generator = None;
    
    genFactory = pagegenerators.GeneratorFactory()

    site = wikipedia.getSite(u'commons', u'commons')
    wikipedia.setSite(site)
    for arg in wikipedia.handleArgs():
        if arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(site, wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(site, arg[6:])]
        else:
            generator = genFactory.handleArg(arg)
    if not generator:
        generator = pagegenerators.CategorizedPageGenerator(catlib.Category(site, u'Category:Media needing categories'), recurse=True)

    categorizeImages(generator)
        
    wikipedia.output(u'All done')    

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
