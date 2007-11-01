#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This is a script to import pages from a certain wiki to another.

This requires administrator privileges.
"""
#
# (C) Filnik, 2007
#
# Greetings:
# Lorenzo Paulatto and Misza13
#
# Distributed under the terms of the MIT license.
#
 
__version__='$Id:'
 
import wikipedia
 
# Global variables
site = wikipedia.getSite()
# ################################################################ #
def main():
    # Defing what page to load..
    pagetoload = 'Apple'
    importerbot = Importer(site) # Inizializing
    importerbot.Import(pagetoload, prompt = True)
 
"""
****************************************************************************
System functions follow: no changes should be necessary!
****************************************************************************
"""
 
import urllib
import login, config
 
class Importer(wikipedia.Page):
    def __init__(self, site):
        wikipedia.Page.__init__(self, site, 'Special:Import', None, 0)
 
    def Import(self, target, project = 'w', crono = '1', namespace = '', prompt = True):
        """Import the page from the wiki. Requires administrator status.
        If prompt is True, asks the user if he wants to delete the page.
        """
        # Fixing the crono value...
        if crono == True:
            crono = '1'
        elif crono == False:
            crono = '0'
        elif crono == '0':
            pass
        elif crono == '1':
            pass
        else:
            wikipedia.output(u'Crono value set wrongly.')
            wikipedia.stopme()
        # Fixing namespace's value.
        if namespace == '0':
            namespace == ''        
        answer = 'y'
        if prompt:
            answer = wikipedia.inputChoice(u'Do you want to import %s?' % target, ['Yes', 'No'], ['y', 'N'], 'N')
        if answer in ['y', 'Y']:
            host = self.site().hostname()
            address = '/w/index.php?title=%s&action=submit' % self.urlname()
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
            if self.site().hostname() in config.authenticate.keys():
                predata['Content-type'] = 'application/x-www-form-urlencoded'
                predata['User-agent'] = useragent
                data = self.site().urlEncode(predata)
                response = urllib2.urlopen(urllib2.Request('http://' + self.site().hostname() + address, data))
                data = u''
            else:
                response, data = self.site().postForm(address, predata, sysop = True)
            if data:
                wikipedia.output(u'Page imported, checking...')
                if wikipedia.Page(site, target).exists():
                    wikipedia.output(u'Import success!')
                    return True
                else:
                    wikipedia.output(u'Import failed!')
                    return False
if __name__=='__main__':
    try:
        main()
    finally:
        wikipedia.stopme()