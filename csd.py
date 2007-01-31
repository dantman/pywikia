# -*- coding: utf-8 -*-
"""
This bot is used to quickly trawl through candidates for speedy deletion in a fast
and semi-automated fashion.  The bot displays the contents of each page one at a
time and provides a prompt for the user to skip or delete the page.  Of course, this
will require a sysop account.

Future upcoming options include the ability to untag a page as not being eligible
for speedy deletion, as well as the option to commute its sentence to Proposed
Deletion (see [[en:WP:PROD]] for more details).  Also, if the article text is long,
to prevent terminal spamming, it might be a good idea to truncate it just to the
first so many bytes.

WARNING: This tool shows the contents of the top revision only.  It is possible that
a vandal has replaced a perfectly good article with nonsense, which has subsequently
been tagged by someone who didn't realize it was previously a good article.  The onus
is on you to avoid making these mistakes.

Syntax: python csd.py

Command line options:

    none yet

Examples:

    none needed yet
    
"""
#
# Distributed under the terms of the MIT license.
#
import wikipedia, config
import replace, pagegenerators
import re, sys, string, catlib

class CSDRobot:
    """
    This robot will load a list of pages from [[CAT:CSD]] and give the user an
    interactive prompt to decide whether each should be deleted or not.
    """

    csd_cat={
        'de': u'Kategorie:Wikipedia:Schnelllöschen',
        'en': u'Category:Candidates for speedy deletion',
    }

    deletion_msg={
        'de':u'Lösche Artikel mit [[Wikipedia:Schnelllöschantrag|Schnelllöschantrag]]',
        'en':u'Deleting candidate for speedy deletion per [[WP:CSD]]',
    }

    def __init__(self):
        """
        Arguments:
            none yet
        """
        self.mySite = wikipedia.getSite()
        self.csdCat = catlib.Category(self.mySite, wikipedia.translate(self.mySite, self.csd_cat))
        self.savedProgress = '!'
        self.generator = None
        self.preloadingGen = None

    def run(self):
        """
        Starts the robot's action.
        """

        keepGoing = True
        startFromBeginning = True
        while keepGoing:
            if startFromBeginning:
                self.savedProgress = '!'
            self.refreshGenerator()
            for page in self.preloadingGen:
                try:
                    pageText = page.get()
                except wikipedia.NoPage:
                    wikipedia.output(u'Page appears to have already been deleted, skipping.')
                    continue
                colors = [None] * 5 + [13] * len(page.title()) + [None] * 4
                wikipedia.output(u'\n>>> %s <<<' % page.title(), colors = colors)
                wikipedia.output(u'-  -  -  -  -  -  -  -  -  ')
                wikipedia.output(pageText)
                wikipedia.output(u'-  -  -  -  -  -  -  -  -  ')
                choice = wikipedia.inputChoice(u'Input action?', ['delete', 'skip', 'update'], ['d', 'S', 'u', 'q'], 'S')
                if choice == 'q':
                    keepGoing = False
                    break
                elif choice == 'u':
                    wikipedia.output(u'Updating from CSD category.')
                    self.savedProgress = page.title()
                    startFromBeginning = False
                    break
                elif choice == 'd':
                    reason = wikipedia.input(u'Please enter the reason for deletion, or press enter for the default message:')
                    if not reason:
                        reason = wikipedia.translate(self.mySite, self.deletion_msg)
                    page.delete(reason, prompt = False)
                elif choice == 's' or True:
                    wikipedia.output(u'Skipping page %s' % page.title())
                startFromBeginning = True
        wikipedia.output(u'Quitting program.')
        
    def refreshGenerator(self):
        self.generator = pagegenerators.CategoryPartPageGenerator(self.csdCat, start = self.savedProgress)
        self.preloadingGen = pagegenerators.PreloadingGenerator(self.generator, pageNumber = 20)
    
def main():
    # read command line parameters
    for arg in wikipedia.handleArgs():
        pass #No args yet

    bot = CSDRobot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
