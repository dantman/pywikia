# -*- coding: utf-8 -*-
"""
Program to add uncat template to images without categories at commons.
See imagerecat.py (still working on that one) to add these images to categories.

"""
#
#  (C) Multichill 2008
#
# Distributed under the terms of the MIT license.
#
#

import os, sys, re, codecs
import wikipedia, config, pagegenerators  

#Probably unneeded because these are hidden categories. Have to figure it out.
ignoreCategories = [u'[[Category:CC-BY-SA-3.0]]',
                    u'[[Category:GFDL]]',
                    u'[[Category:Media for cleanup]]',
                    u'[[Category:Media lacking a description]]',
                    u'[[Category:Media lacking author information]]',
                    u'[[Category:Media lacking a description]]',
                    u'[[Category:Self-published work]]']

#Dont bother to put the template on a image with one of these templates
ignoreTemplates = [u'Delete',
                   u'Nocat',
                   u'No license',
                   u'No permission since',
                   u'No source',
                   u'No source since',
                   u'Uncategorized',
                   u'Uncat']

puttext = u'\n{{Uncategorized|year={{subst:CURRENTYEAR}}|month={{subst:CURRENTMONTHNAME}}|day={{subst:CURRENTDAY}}}}'
putcomment = u'Please add categories to this image'

def isUncat(page):
    '''
    Do we want to skip this page?

    If we found a category which is not in the ignore list it means that the page is categorized so skip the page.
    If we found a template which is in the ignore list, skip the page.
    '''
    for category in page.categories():
        if category not in ignoreCategories:
            #if category.title().count("Unknown") > 0:
                #print "Iets unknown"
            #else:
                #print "false"
            return False            
    #print "true"
    for template in page.templates():
        if template in ignoreTemplates:
            return False
    return True

def addUncat(page):
    '''
    Add the uncat template to the page
    '''    
    newtext = page.get() + puttext
    wikipedia.showDiff(page.get(), newtext)
    try:
        page.put(newtext, putcomment)
    except wikipedia.EditConflict:
        # Skip this page
        pass
    return    

def main(args):
    '''
    Grab a bunch of images and tag them if they are not categorized.
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
        wikipedia.output('You have to specify the generator you want to use for the program!')
    else:    
        pregenerator = pagegenerators.PreloadingGenerator(generator)
        for page in pregenerator:
            if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()) :
                if isUncat(page):
                    addUncat(page)                        

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
