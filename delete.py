# -*- coding: utf-8 -*-
"""
This script can be used to delete pages en masse.  Of course, you will need an admin
account on the relevant wiki.

Syntax: python delete.py [-category categoryName]

Command line options:

-category:   Delete all pages in the given category.
-links:      Delete all pages linked from a given page.
-ref:        Delete all pages referring from a given page.
-always      Don't prompt to delete pages, just do it.
-summary:    Supply a custom edit summary.

Examples:

Delete everything in the category "To delete" without prompting.

    python delete.py -category:"To delete" -always
"""
#
# Distributed under the terms of the MIT license.
#
import wikipedia, config, catlib
import pagegenerators
#import re, sys, string

class DeletionRobot:
    """
    This robot allows deletion of pages en masse.
    """
    # Summary messages for deleting from a category.
    msg_delete_category={
        'en':u'Robot - Deleting all pages from category %s',
        'pt':u'Bot: Apagando todas as páginas da categoria %s',
        }
    msg_delete_links={
        'en':u'Robot - Deleting all pages linked from %s',
        'pt':u'Bot: Apagando todas as páginas ligadas a %s',
        }
    msg_delete_ref={
        'en':u'Robot - Deleting all pages referring from %s',
        'pt':u'Bot: Apagando todas as páginas afluentes a %s',
        }
    
    def __init__(self, generator, pageName, summary, always = False, doCategory = False, doLinks = False, doRef = False):
        """
        Arguments:
            * generator - A page generator.
            * pageName - The name of the page the pages to be deleted are collected from.
            * summary - A custom edit summary.
        """
        self.generator = generator
        self.pageName = pageName
        self.summary = summary
        self.always = always
        self.doCategory = doCategory
        self.doLinks = doLinks
        self.doRef = doRef

        # get edit summary message
        mysite = wikipedia.getSite()
        if self.summary:
            wikipedia.setAction(self.summary)
        else:
            if self.doCategory:
                self.summary = wikipedia.translate(mysite, self.msg_delete_category) % self.pageName
            elif self.doLinks:
                self.summary = wikipedia.translate(mysite, self.msg_delete_links) % self.pageName
            elif self.doRef:
                self.summary = wikipedia.translate(mysite, self.msg_delete_ref) % self.pageName
            wikipedia.setAction(self.summary)

    def run(self):
        """
        Starts the robot's action.
        """
        #Loop through everything in the page generator and delete it.
        for page in self.generator:
            wikipedia.output(u'Processing page %s' % page.title())
            page.delete(self.summary, not self.always, throttle=True)
    
def main():
    pageName = ''
    summary = ''
    always = False
    doCategory = doRef = doLinks = False
    # read command line parameters
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                summary = wikipedia.input(u'Input an edit summary:')
            else:
                summary = arg[len('-summary:'):]
        elif arg.startswith('-category'):
            doCategory = True
            if len(arg) == len('-category'):
                pageName = wikipedia.input(u'Input the category to delete from:')
            else:
                pageName = arg[len('-category:'):]
        elif arg.startswith('-links'):
            doLinks = True
            if len(arg) == len('-links'):
                pageName = wikipedia.input(u'Input the page to delete from:')
            else:
                pageName = arg[len('-links:'):]
        elif arg.startswith('-ref'):
            doRef = True
            if len(arg) == len('-ref'):
                pageName = wikipedia.input(u'Input the page to delete from:')
            else:
                pageName = arg[len('-ref:'):]
        #elif arg.startswith('-page'):
            # TODO: Delete only one page

    if not pageName:
        wikipedia.showHelp(u'delete')
    elif doCategory:
        ns = wikipedia.getSite().category_namespace()
        categoryPage = catlib.Category(wikipedia.getSite(), ns + ':' + pageName)
        gen = pagegenerators.CategorizedPageGenerator(categoryPage, recurse=True)
    elif doLinks:
        linksPage = wikipedia.Page(wikipedia.getSite(), pageName)
        gen = pagegenerators.LinkedPageGenerator(linksPage)
    elif doRef:
        refPage = wikipedia.Page(wikipedia.getSite(), pageName)
        gen = pagegenerators.ReferringPageGenerator(refPage)
        
    if pageName:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = DeletionRobot(preloadingGen, pageName, summary, always, doCategory=doCategory, doLinks=doLinks, doRef=doRef)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
