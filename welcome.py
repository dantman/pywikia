#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to welcome new users. This script does not work out of the box. It needs
to be tailored to the needs on the wiki it will be run on. It is currently
users on the Dutch Wikipedia and Wikimedia Commons.

Ensure you have community support before running this bot!

URLs to current implementations:
Wikimedia Commons: http://commons.wikimedia.org/wiki/Commons:Welcome_log
Dutch Wikipedia: http://nl.wikipedia.org/wiki/Wikipedia:Logboek_welkom

Everything that needs customisation is preceeded by three lines of comments.
In those comments you will find what you need to add and what the current
settings are on Commons and the Dutch Wikipedia.

Description of basic functionality:
* Request a list of new users every hour
* Check if new user has made any edits
* If user has made any edits, check if user has an empty talk page
* If user had an empty talk page, add a welcome message
* Once 5 users have been welcomed, add this to a log page, one for each day
* If no log page exists, create a header for the log page first.
*The script will repeat itself every hour until forced to stop.

This script uses one templates that needs to be on the local wiki. In this script
it is called {{WLE}}. It contains mark up code for log entries.

This script understands no command-line arguments.

Known issues. Please fix these if you are capable and motivated:
* exits when wiki is down.
* exits on reporting an edit conflict (had this on Commons where 2 bots are using this script)
* script contains some duplicate code. Refactoring might be nice.
* script contains variable names in Spanish that might make code harder to read. They could be renamed.
* automatic user talk namespace name could be extracted from the wiki itself (would save customisation in three places).
* username and contributions (plural) can probably also be extracted from wiki (saves 2 customisations)
* script does not take any parameters. Might be nice to add some, so it requires less customisation
** how many users to skip
** how many users to check
** which project code to run on
** which language code to run on
** user welcome summary
** log summary
"""
#
# (C) Kyle/Orgullomoore, 2006-2007
# (C) Siebrand Mazeland, 2006-2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import urllib2
import wikipedia
import time

##This variable should be changed for whatever project it is to be used on.
##For Wikimedia, for example, wikipedia.Site('commons', 'commons')
##For Dutch Wikipedia, for example welcomesite=wikipedia.Site('nl', 'wikipedia')

def pageText(url):
	request=urllib2.Request(url)
	user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
	print url
	request.add_header("User-Agent", user_agent)
	response=urllib2.urlopen(request)
	text=response.read()
	response.close()
	return text

done=[]
def parselog(raw):
    users=[]
    ##On a new line below you need to add the user talk namespace name of the wiki
    ##For Dutch Wikimedia, for example, tabla=raw.split('class="new" title="Overleg gebruiker:')
    ##For Wikimedia Commons, for example, tabla=raw.split('class="new" title="User talk:')
    tabla.remove(tabla[0])
    for cerca in tabla:
        username=cerca.split('"')[0]
        if username not in done:
            done.append(username)
            UN=wikipedia.Page(welcomesite, username)
            ##On a new line below you need to add the user talk namespace name of the wiki
            ##For Dutch Wikimedia, for example, UNT=wikipedia.Page(welcomesite, 'Overleg gebruiker:'+username)
            ##For Wikimedia Commons, for example, UNT=wikipedia.Page(welcomesite, 'User talk:'+username)

            ##On a new line below you need to add the user talk namespace name of the wiki
            ##For Dutch Wikimedia, for example, contribs=pageText('http://nl.wikipedia.org/wiki/Speciaal:Contributions/'+UN.urlname()).decode('utf-8', 'replace')
            ##For Wikimedia Commons, for example, contribs=pageText('http://commons.wikimedia.org/wiki/Special:Contributions/'+UN.urlname()).decode('utf-8', 'replace')
            contribnum=contribs.count('<li>') #This is not an accurate count, it just counts the first
	                                      #50 contributions
            if contribnum != 0:
                users.append([username, contribnum])
    return users
hechas=[]
while 2==2:
    ##On a new line below you need to add the correct URL for retreiving the selection of new users of the wiki.
    ##Take into account how many new users per period you are expecting. This example runs every hour and checks
    ##newest users 11-70.
    ##For Dutch Wikimedia, for example, URL='http://nl.wikipedia.org/w/index.php?title=Speciaal:Log&limit=60&offset=10&type=newusers'
    ##For Wikimedia Commons, for example, URL='http://nl.wikipedia.org/w/index.php?title=Speciaal:Log&limit=60&offset=10&type=newusers'
    log=pageText(URL).decode('utf-8', 'replace')
    parsed=parselog(log)
    for tablita in parsed:
        ##On a new line below you need to add the user talk namespace name of the wiki
        ##For Dutch Wikimedia, for example, UNT=wikipedia.Page(welcomesite, 'Overleg gebruiker:'+tablita[0])
        ##For Wikimedia Commons, for example, UNT=wikipedia.Page(welcomesite, 'User talk:'+tablita[0])
        if not UNT.exists():
            ##On a new line below you need to add the message to place on each qualifying user talk page and the edit summary
            ##For Dutch Wikimedia, for example, UNT.put('{{Gebruiker:SieBot/Logboek welkom/Welkomstbericht}} [[Overleg gebruiker:Siebrand|Siebrand]] ~~~~~', "Welkom op de Nederlandstalige Wikipedia!")
            ##For Wikimedia Commons, for example, UNT.put('{{subst:welcome}}', "Welcome to the Commons!")
            hechas.append(tablita)
        print len(hechas)
        # update the welcome log each fifth welcome message
        if len(hechas)>4:
            safety=[]
            #deduct the correct sub page name form the current date.
            rightime=time.localtime(time.time())
	    year=str(rightime[0])
            month=str(rightime[1])
            day=str(rightime[2])
            if len(month)==1:
                month='0'+month
            ##On a new line below you need to add base page for the welcome logs.
            ##For Dutch Wikimedia, for example, pl=wikipedia.Page(welcomesite, 'Wikipedia:Logboek welkom/'+year+'/'+month+'/'+day)
            ##For Wikimedia Commons, for example, pl=wikipedia.Page(commons, 'Commons:Welcome log/'+month+'/'+day+'/'+year)
	    try:
                safety.append(pl.get())
            except wikipedia.NoPage:
                #Add the table heading each new period. See http://commons.wikimedia.org/wiki/Commons:Welcome_log
                safety.append('{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
                # change the string below to "Username" in your wiki's language. The example is in Dutch.
                safety.append('\n! Gebruikersnaam')
                # change the string below to "Contribs" in your wiki's language. The example is in Dutch.
                safety.append('\n! Bijdragen')

            for tablita in hechas:
                UPl=wikipedia.Page(welcomesite, tablita[0])
                cantidad=str(tablita[1])

                ##On a new line below, the the template used for adding lines to the welcome log.
                ##For Dutch Wikimedia, for example, safety.append('\n{{Gebruiker:SieBot/WLE|user='+UPl.title()+'|contribs='+cantidad+'}}')
                ##For Wikimedia Commons, for example, safety.append('\n{{WLE|user='+UPl.title()+'|contribs='+cantidad+'}}')

            ##On a new line below, add the edit summary when updating the welcome log.
            ##For Dutch Wikimedia, for example, pl.put(''.join(safety), 'Logboek bijwerken')
            ##For Wikimedia Commons, for example, pl.put(''.join(safety), 'Updating log')
            hechas=[]
    #do not exit, repeat after one hour
    time.sleep(3600)
