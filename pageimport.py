#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This is a script to import pages from a certain wiki to another.

This requires administrator privileges.

Here there is an example of how to use it:

from pageimport import *
def main():
    # Defing what page to load..
    pagetoload = 'Apple'
    site = wikipedia.getSite()
    importerbot = Importer(site) # Inizializing
    importerbot.Import(pagetoload, prompt = True)
try:
    main()
finally:
    wikipedia.stopme()
"""
#
# (C) Filnik, 2007
#
# Greetings:
# Lorenzo Paulatto and Misza13
#
# Distributed under the terms of the MIT license.
#

__version__ = '$Id$'

import urllib
import wikipedia, login, config

class Importer(wikipedia.Page):
    def __init__(self, site):
        self.importsite = site
        wikipedia.Page.__init__(self, site, 'Special:Import', None, 0)

    def Import(self, target, project = 'w', crono = '1', namespace = '', prompt = True):
        """Import the page from the wiki. Requires administrator status.
        If prompt is True, asks the user if he wants to delete the page.
        """
        if project == 'w':
            site = wikipedia.getSite(fam = 'wikipedia')
        elif project == 'b':
            site = wikipedia.getSite(fam = 'wikibooks')
        elif project == 'wikt':
            site = wikipedia.getSite(fam = 'wiktionary')
        elif project == 's':
            site = wikipedia.getSite(fam = 'wikisource')
        elif project == 'q':
            site = wikipedia.getSite(fam = 'wikiquote')
        else:
            site = wikipedia.getSite()
        # Fixing the crono value...
        if crono == True:
            crono = '1'
        elif crono == False:
            crono = '0'
        # Fixing namespace's value.
        if namespace == '0':
            namespace == ''
        answer = 'y'
        if prompt:
            answer = wikipedia.inputChoice(u'Do you want to import %s?' % target, ['Yes', 'No'], ['y', 'N'], 'N')
        if answer == 'y':
            host = self.site().hostname()
            address = self.site().path() + '?title=%s&action=submit' % self.urlname()
            # You need to be a sysop for the import.
            self.site().forceLogin(sysop = True)
            # Getting the token.
            token = self.site().getToken(self, sysop = True)
            # Defing the predata.
            predata = {
                'action' : 'submit',
                'source' : 'interwiki',
                # from what project do you want to import the page?
                'interwiki' : project,
                # What is the page that you want to import?
                'frompage' : target,
                # The entire history... or not?
                'interwikiHistory' : crono,
                # What namespace do you want?
                'namespace': '',
            }
            response, data = self.site().postForm(address, predata, sysop = True)
            if data:
                wikipedia.output(u'Page imported, checking...')
                if wikipedia.Page(self.importsite, target).exists():
                    wikipedia.output(u'Import success!')
                    return True
                else:
                    wikipedia.output(u'Import failed!')
                    return False

if __name__=='__main__':
    wikipedia.output(u'This is just a module! Read the documentation and write your own script!')
    wikipedia.stopme()
