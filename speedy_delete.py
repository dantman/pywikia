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

Syntax: python speedy-delete.py

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

class SpeedyRobot:
    """
    This robot will load a list of pages from the category of candidates for speedy
    deletion on the language's wiki and give the user an interactive prompt to decide
    whether each should be deleted or not.
    """

    csd_cat={
        'de': u'Kategorie:Wikipedia:Schnelllöschen',
        'en': u'Category:Candidates for speedy deletion',
    }

    deletion_messages = {
        'de': {
            u'_default': u'Lösche Artikel mit [[Wikipedia:Schnelllöschantrag|Schnelllöschantrag]]',
        },
        'en': {
            u'_default':     u'Deleting candidate for speedy deletion per [[WP:CSD]]',
            u'Db-nonsense':  u'Nonsense',
            u'Db-test':      u'Test page',
            u'Db-vandalism': u'Vandalism',
        },
    }

    talk_deletion_msg={
        'en':u'Verwaiste Diskussionsseite von gelöschter Seite',
        'en':u'Orphaned talk page of deleted page',
    }

    delete_reasons = {
        'de': {
            'mist':  u'Unsinn',
            'asdf':  u'Tastaturtest',
            'spam':  u'Spam',
            'web':   u'Nur ein Weblink',
            'egal':  u'Eindeutig irrelevant',
            'pfui':  u'Beleidigung',
            'redir': u'Unnötiger Redirect',
        },
        'en': {
            # just for testing
            '1':  u'Reason 1',
            '2':  u'Reason 2',
        },
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

    def guessReasonForDeletion(self, page):
        templateNames = page.templates()
        reason = None
        reasons = wikipedia.translate(self.mySite, self.deletion_messages)
        
        for templateName in templateNames:
            print templateName
            if templateName in reasons.keys():
                
                reason = reasons[templateName]
        if not reason:
            reason = reasons[u'_default']
        return reason

    def getReasonForDeletion(self, page):
        suggestedReason = self.guessReasonForDeletion(page)
        wikipedia.output(u'The suggested reason is: %s\n' % suggestedReason)

        if self.delete_reasons.has_key(page.site().lang):
            localReasons = self.delete_reasons[page.site().lang]
            for key, reason in localReasons.iteritems():
                wikipedia.output(u'%s: %s' % (key, reason))
            reason = wikipedia.input(u'Please enter the reason for deletion, choose a default reason, or press enter for the suggested message:')
            if localReasons.has_key(reason):
                reason = localReasons[reason]
        else:
            reason = wikipedia.input(u'Please enter the reason for deletion, or press enter for the suggested message:')

        if not reason:
            reason = suggestedReason
        return reason

    def handleTalkPage(self, page):
        if not page.isTalkPage():
            talkPage = page.switchTalkPage()
            if talkPage.exists():
                choiceTalk = wikipedia.inputChoice('Delete associated talk page?', ['yes', 'no'], ['y', 'n'], default='y')
                if choiceTalk == 'y':
                    talkPage.delete(wikipedia.translate(self.mySite, self.talk_deletion_msg), prompt = False)
        
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
                    reason = self.getReasonForDeletion(page)
                    wikipedia.output(u'Selected reason is: %s' % reason)
                    page.delete(reason, prompt = False)
                    self.handleTalkPage(page)
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

    bot = SpeedyRobot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
