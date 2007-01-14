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

# Summary messages for deleting from a category.
msg_delete_category = {
    'de': u'Bot: Lösche alle Seiten in Kategorie %s',
    'en': u'Robot - Deleting all pages from category %s',
    'lt': u'robotas: Trinami visi puslapiai iš kategorijos %s',
    'pt': u'Bot: Apagando todas as páginas da categoria %s',
}
msg_delete_links = {
    'de': u'Bot: Lösche alle Seiten in %s verlinkten Seiten',
    'en': u'Robot - Deleting all pages linked from %s',
    'lt': u'robotas: Trinami visi puslapiai į kuriuos yra nuoroda iš %s',
    'pt': u'Bot: Apagando todas as páginas ligadas a %s',
}
msg_delete_ref = {
    'de': u'Bot: Lösche alle auf %s linkenden Seiten',
    'en': u'Robot - Deleting all pages referring from %s',
    'lt': u'robotas: Trinami visi puslapiai rodantys į %s',
    'pt': u'Bot: Apagando todas as páginas afluentes a %s',
}

class DeletionRobot:
    """
    This robot allows deletion of pages en masse.
    """
    
    def __init__(self, generator, summary, always = False):
        """
        Arguments:
            * generator - A page generator.
            * always - Delete without prompting?
        """
        self.generator = generator
        self.summary = summary
        self.always = always

    def run(self):
        """
        Starts the robot's action.
        """
        #Loop through everything in the page generator and delete it.
        for page in self.generator:
            wikipedia.output(u'Processing page %s' % page.title())
            page.delete(self.summary, not self.always, throttle = True)
    
def main():
    pageName = ''
    singlePage = ''
    summary = ''
    always = False
    doSinglePage = False
    doCategory = False
    doRef = False
    doLinks = False
    gen = None
    
    # read command line parameters
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                summary = wikipedia.input(u'Enter a reason for the deletion:')
            else:
                summary = arg[len('-summary:'):]
        elif arg.startswith('-category'):
            doCategory = True
            if len(arg) == len('-category'):
                pageName = wikipedia.input(u'Enter the category to delete from:')
            else:
                pageName = arg[len('-category:'):]
        elif arg.startswith('-links'):
            doLinks = True
            if len(arg) == len('-links'):
                pageName = wikipedia.input(u'Enter the page to delete from:')
            else:
                pageName = arg[len('-links:'):]
        elif arg.startswith('-ref'):
            doRef = True
            if len(arg) == len('-ref'):
                pageName = wikipedia.input(u'Enter the page to delete from:')
            else:
                pageName = arg[len('-ref:'):]
        elif arg.startswith('-page'):
            doSinglePage = True
            if len(arg) == len('-page'):
                pageName = wikipedia.input(u'Enter the page to delete:')
            else:
                pageName = arg[len('-page:'):]

    mysite = wikipedia.getSite()

    if doSinglePage:
        if not summary:
            summary = wikipedia.input(u'Enter a reason for the deletion:')
        page = wikipedia.Page(wikipedia.getSite(), pageName)
        gen = iter([page])
    elif doCategory:
        if not summary:
            summary = wikipedia.translate(mysite, msg_delete_category) % pageName
        ns = wikipedia.getSite().category_namespace()
        categoryPage = catlib.Category(wikipedia.getSite(), ns + ':' + pageName)
        gen = pagegenerators.CategorizedPageGenerator(categoryPage, recurse=True)
    elif doLinks:
        if not summary:
            summary = wikipedia.translate(mysite, msg_delete_links) % pageName
        wikipedia.setAction(summary)
        linksPage = wikipedia.Page(wikipedia.getSite(), pageName)
        gen = pagegenerators.LinkedPageGenerator(linksPage)
    elif doRef:
        if not summary:
            summary = wikipedia.translate(mysite, msg_delete_ref) % pageName
        refPage = wikipedia.Page(wikipedia.getSite(), pageName)
        gen = pagegenerators.ReferringPageGenerator(refPage)
    if gen:
        wikipedia.setAction(summary)
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = DeletionRobot(preloadingGen, summary, always)
        bot.run()
    else:
        wikipedia.showHelp(u'delete')

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
