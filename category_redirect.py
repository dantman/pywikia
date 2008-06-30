#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to clean up http://commons.wikimedia.org/wiki/Category:Non-empty_category_redirects

Moves all images, pages and categories in redirect categories to the target category.

"""

#
# (C) Multichill, 2008
#
# Distributed under the terms of the MIT license.
#

import wikipedia, config, catlib
from category import *

redirect_templates = [u'Category redirect', u'Categoryredirect', u'See cat', u'Seecat', u'Catredirect', u'Cat redirect', u'CatRed', u'Catredir']
move_message = u'Moving from [[%s|%s]] to [[%s|%s]] (following [[Template:Category redirect|category redirect]])'

def get_redirect_cat(category=None):
    '''
    Return the target category
    '''
    destination = None
    site = wikipedia.getSite(u'commons', u'commons')
    for template in category.templatesWithParams():
        if ((template[0] in redirect_templates) and (len(template[1]) > 0)):
            #destination = template[1][0];
            destination =catlib.Category(site, template[1][0])
            if not destination.exists():
                return None
    return destination
    

def main():
    '''
    Main loop. Loop over all categories of Category:Non-empty_category_redirects and move all content.
    '''    

    site = wikipedia.getSite(u'commons', u'commons')
    dirtycat = catlib.Category(site, u'Category:Non-empty category redirects')
    destination = None
    catbot = None
    
    for old_category in dirtycat.subcategories():
        destination = get_redirect_cat(old_category)
        if destination:
            wikipedia.output(destination.title())
            for page in old_category.articles():
                try:                                
                    catlib.change_category(page, old_category, destination, move_message % (old_category.title(), old_category.titleWithoutNamespace(), destination.title(), destination.titleWithoutNamespace()))
                except wikipedia.IsRedirectPage:
                    wikipedia.output(page.title() + u' is a redirect!')
            for cat in old_category.subcategories():
                try:                
                    catlib.change_category(cat, old_category, destination, move_message % (old_category.title(), old_category.titleWithoutNamespace(), destination.title(), destination.titleWithoutNamespace()))
                except wikipedia.IsRedirectPage:
                    wikipedia.output(page.title() + u' is a redirect!')
        #Dummy edit to refresh the page, shouldnt show up in any logs.
        try:
            old_category.put(old_category.get())
        except:
            wikipedia.output(u'Dummy edit at ' + old_category.title() + u' failed')        

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
