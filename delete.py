# -*- coding: utf-8 -*-
"""
This script can be used to delete pages en masse.  Of course, you will need an admin
account on the relevant wiki.

Syntax: python delete.py [-category categoryName]

Command line options:

-category:   Delete all pages in the given category.
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
    }

    def __init__(self, generator, categoryName, summary, always = False):
        """
        Arguments:
            * generator - A page generator.
            * categoryName - The name of the category the pages are collected from.
            * summary - A custom edit summary.
        """
        self.generator = generator
        self.categoryName = categoryName
        self.summary = summary
        self.always = always

        # get edit summary message
        mysite = wikipedia.getSite()
        if self.summary:
            wikipedia.setAction(self.summary)
        else:
            self.summary = wikipedia.translate(mysite, self.msg_delete_category) % self.categoryName
            wikipedia.setAction(self.summary)

    def run(self):
        """
        Starts the robot's action.
        """
        #Loop through everything in the page generator and delete it.
        for page in self.generator:
            wikipedia.output(u'Processing page %s' % page.title())
            page.delete(self.summary, not self.always)
    
def main():
    categoryName = ''
    summary = ''
    always = False
    # read command line parameters
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                summary = wikipedia.input(u'Input an edit summary: ')
            else:
                summary = arg[len('-summary:'):]
        elif arg.startswith('-category'):
            if len(arg) == len('-category'):
                categoryName = wikipedia.input(u'Input the category to delete from: ')
            else:
                categoryName = arg[len('-category:'):]

    if not categoryName:
        wikipedia.output(u'You did not give me anything to do, quitting.')
    else:
        ns = wikipedia.getSite().category_namespace()

        categoryPage = catlib.Category(wikipedia.getSite(), ns + ':' + categoryName)

        gen = pagegenerators.CategorizedPageGenerator(categoryPage, recurse=True)
        preloadingGen = pagegenerators.PreloadingGenerator(gen)

        bot = DeletionRobot(preloadingGen, categoryName, summary, always)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
