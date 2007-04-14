#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to welcome new users. This script works out of the box for wikis that
have been defined in the script. It is currently used on the Dutch and
Italian Wikipedia and Wikimedia Commons.

Ensure you have community support before running this bot!

URLs to current implementations:
* Wikimedia Commons: http://commons.wikimedia.org/wiki/Commons:Welcome_log
* Dutch Wikipedia: http://nl.wikipedia.org/wiki/Wikipedia:Logboek_welkom

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

This script uses one templates that needs to be on the local wiki. In this script
it is called {{WLE}}. It contains mark up code for log entries.

This script understands the following command-line arguments:
-edit           - Define how many edits a new user needs to be welcomed (default: 1).

-time           - Define how long the bot must sleep before restart (default: 1 hour).

-break          - Use it if you don't want that the Bot restart at the end (it will break).

-nlog           - Use this parameter if you don't want that the Bot will add a log (default: not defined)

-limit          - Use this parameter to define how may users should be checked (default:50)

-numberlog      - The number of users to welcome before refreshing the welcome log (default: 4)

-ask or -askme  - Use this parameter if you want that the Bot asks you if report an user or not.

-filter         - Use this parameter to enable the nickname filter.

Known issues. Please fix these if you are capable and motivated:
* exits when wiki is down.
* script contains some duplicate code. Refactoring might be nice.
* automatic user talk namespace name could be extracted from the framwork somewhere (family files) (would save customisation)
Done but it might be done better
* username and contributions (plural) can probably also be extracted from wiki (saves 2 customisations)
* add variable for how many users to skip (f.e. the 10 latest users, that may not have made any edits)

"""
#
# (C) Alfio, 2005
# (C) Kyle/Orgullomoore, 2006-2007
# (C) Siebrand Mazeland, 2006-2007
# (C) Filnik, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import urllib2, config
import wikipedia, codecs
import time, re

# I use this trick to understand what project and language the bot will use
c = str(wikipedia.getSite())
k = c.split(":")
project = k[0]
lang = k[1]

# Using the wikipedia.translate() class i could use the right page/user/summary
# ecc. without specify what project the bot will use :)
# FIXME: There isn't all the project, so, if it's not the right project you have to
# add it :) I think that's simple if you look at the other languages ;)
# N.B. The parameters below aren't the only one that needs to be fixed, search
# the other dictionary delimeted in the same way :-) (it's only one) or search
# "FIXME" :-)

####################################################################################
####################################################################################
####################################################################################

# The text below are dictionaries, you have only to copy the en line, change 'en' in
# your language (for example 'de') and modify the text between "" that follow.

#This is the page where the bot will save the log (for example: Wikipedia:Welcome log).
logbook = {
    'commons':str(project) + ":Welcome log" ,
    'de':str(project) + ":Willkommen log",
    'en':str(project) + ":Welcome log" ,
    'it':str(project) + ":Benvenuto log",
    'nl':str(project) + ':Logboek welkom',
    }
#The user talk namespace name, for example User_talk:
talkpage = {
    'commons':'User_talk:',
    'de':'Benutzer_Diskussion:',
    'en':'User_talk:',
    'it':'Discussioni_utente:',
    'nl':'Overleg_gebruiker:',
    }
summary = {
    'commons':'Welcome!',
    'de':'Herzlich Willkommen!',
    'en':'Welcome!',
    'it':'Benvenuto!',
    'nl':'Welkom!',
    }
# The text for the welcome message
netext = {
    'commons':'{{subst:welcome}}',
    'de':'{{Benutzer:Filnik/Willkommen}}\nViele Grüsse --~~~~',
    'en':'{{subst:welcome}}--~~~~',
    'it':'{{subst:benve|~~~~}}',
    'nl':'{{Welkomstbericht}}',
    }
# The edit summary for updating the welcome log.
summary2 = {
    'commons':'Updating log',
    'de':'Ich neu bearbeite den Logfile',
    'en':'Updating log',
    'it':'Aggiorno il log',
    'nl':'Logboek bijwerken',
    }
# Username in the wiki language.
user = {
    'commons':'Username',
    'de':'Benutzer',
    'en':'Username',
    'it':'Utente',
    'nl':'Gebruikersnaam',
    }
# Contributions in the wiki language.
con = {
    'commons':'Contribs',
    'de':'Beitraege',
    'en':'Contribs',
    'it':'Contributi',
    'nl':'Bijdragen',
    }
# The page where the bot will report users with a possibly bad username.
report_page = {
    'commons':'Commons:Administrators\' noticeboard/User problems/Usernames to be checked',
    'de':'Benutzer:Filnik/Report',
    'en':'Wikipedia:Administrator intervention against vandalism',
    'it':'Utente:Filbot/Report',
    'nl':'Wikipedia:Verzoekpagina voor moderatoren/RegBlok/Te controleren gebruikersnamen',
    }
# The edit summary for reporting a possibly bad username.
comment = {
    'commons':'Adding a username that needs to be checked',
    'de':'Adding a username that needs to be checked',
    'en':'Adding a username that needs to be checked',
    'it':'Aggiunto utente da controllare',
    'nl':"Te controleren gebruikersnaam toegevoegd",
    }
# The page where the bot reads the real-time bad-word page. (that' parameter is optional :) ).
bad_pag = {
    'commons':str(project) + ':Welcome log/Bad_names', 
    'en':str(project) + ':Welcome log/Bad_names',         
    'it':'Utente:Filbot/Bad_words',
    'nl':str(project) + ':Logboek_welkom/Bad_names',
    }

# The two blocks that follows are functions, the part of text the you have to change is between the "#" lines.
# I've used these two functions to put the text to change at the top and not in the code below :-)
 
def rep(username):
                                        #Change below!!!       
################################################################################################################################################
    # The text that you'll add when you report a bad username (for example: *[[Talk_page:Username|Username]])
    report_text = {
        'commons':"\n*{{user3|" + Username + "}}" + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()),
        'de':'\n*[[Benutzer_Diskussion:' + username + "|" + username + "]] " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()),
        'en':'\n*{{Userlinks|' + username + '}} ' + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()),
        'it':"\n*[[Discussioni utente:" + username + "|" + username + "]] " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()),
        'nl':'\n*{{linkgebruiker|' + username + '}} ' + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()),                  
        }
################################################################################################################################################
                                        #Change above!!!    
    rep_text = wikipedia.translate(wikipedia.getSite(), report_text)
    return rep_text

def logfunction(UPl, cantidad):
                                        #Change below!!!    
################################################################################################################################################
    # My suggest is only to copy the en line (and change en to your language), copy the WLE template from en-wiki (or commons).
    logt = {    
        'commons':'\n{{WLE|user=' + UPl + '|contribs=' + cantidad + '}}',
        'de':'\n{{WLE|user=' + UPl + '|contribs=' + cantidad + '}}',
        'en':'\n{{WLE|user=' + UPl + '|contribs=' + cantidad + '}}',
        'it':'\n{{WLE|user=' + UPl + '|contribs=' + cantidad + '}}',
        'nl':'\n{{WLE|user='+ UPl + '|contribs=' + cantidad + '}}',
        }
################################################################################################################################################
                                        #Change above!!!
    logtext = wikipedia.translate(wikipedia.getSite(), logt)
    return logtext

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = ['commons', 'de', 'en', 'it', 'nl']

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project ;)
################################################################################################################################################    
################################################################################################################################################   
################################################################################################################################################    

# A little block-statement to ensure that the bot won't start with en-parameters
if lang not in project_inserted:
    print "Your project is not supported by the framework. You have to edit the script and add it!"
    wikipedia.stopme()
    exit()

# The follow lines translate the language's parameters.
welcom = wikipedia.translate(wikipedia.getSite(), netext)
talk = wikipedia.translate(wikipedia.getSite(), talkpage)
contib = u'Special:Contributions'
summ = wikipedia.translate(wikipedia.getSite(), summary)
logg = wikipedia.translate(wikipedia.getSite(), logbook)
summ2 = wikipedia.translate(wikipedia.getSite(), summary2)
usernam = wikipedia.translate(wikipedia.getSite(), user)
contrib = wikipedia.translate(wikipedia.getSite(), con)
rep_page = wikipedia.translate(wikipedia.getSite(), report_page)
com = wikipedia.translate(wikipedia.getSite(), comment)
bad_page = wikipedia.translate(wikipedia.getSite(), bad_pag)

# Number = number of edits that an user required to be welcomed
number = 1
# Numberlog = number of users that are required to add the log :)
numberlog = 4
# limit = number of users that the bot load to check
limit = 50
# recursive = define if the Bot is recursive or not
recursive = True
# time_variable = how much time the Bot sleeps before restart
time_variable = 3600
# log_variable = to define if you want to create the log or not
log_variable = True
# ask = Variable to define if you want that the bot ask you between put the
# welcome or to write his name in the bad-nick list
ask = False
# filter_wp = A filter to check if the username is ok or not
filter_wp = False

# The block below is used for the parameter
for arg in wikipedia.handleArgs():
    if arg.startswith('-edit'):
        if len(arg) == 5:
            number = int(wikipedia.input(u'How many edits will need a user to be welcomed?'))
        else:
            number = int(arg[6:])
    elif arg.startswith('-time'):
        if len(arg) == 5:
            time_variable = int(wikipedia.input(u'How long do you want that the Bot sleeps?'))
        else:
            time_variable = int(arg[6:])
    elif arg == '-break':
        recursive = False
    elif arg == '-nlog':
        log_variable = False
    elif arg == '-askme':
        ask = True
    elif arg == '-ask':
        ask = True
    elif arg == '-filter':
        filter_wp = True        
    elif arg.startswith('-limit'):
        if len(arg) == 6:
            limit = int(wikipedia.input(u'How many users do you want to load?'))
        else:
            limit = int(arg[7:])
    elif arg.startswith('-numberlog'):
        if len(arg) == 10:
            numberlog = int(wikipedia.input(u'How many users do you want that the bot welcomed, before refresh the log?'))
        else:
            numberlog = int(arg[11:])

def badword_function(raw):
    list_loaded = list()
    pos = 0
    load_2 = True
    # I search with a regex how many user have not the talk page
    # and i put them in a list (i find it more easy and secure)
    while load_2 == True:
        regl = "(\"|\')(.*?)(\"|\')(, |\))"
        pl = re.compile(regl, re.UNICODE)
        xl = pl.search(raw, pos)
        if xl == None:
            if len(list_loaded) >= 1:
                print "\nBadwords loaded."
                load_2 = False
                return list_loaded
            elif len(done) == 0:
                print "I've not found badwords in the default page."
                load_2 = False
                continue
        pos = xl.end()
        badword = xl.group(2)
        if badword not in list_loaded:
             list_loaded.append(badword)
if filter_wp == True:
    # What follow below are the standard list of badusernames. (elenco in italian means list :) )
    elencoaf = [' ano', ' anus', 'anal ', 'babies', 'baldracca', 'balle', 'bastardo', 'bestiali', 'bestiale', 'bastarda', 'b.i.t.c.h.', 'bitch', 'boobie', 'bordello', 'breast', 'cacata', 'cacca', 'cachapera', 'cagata', 'cane', 'cazz', 'cazzo', 'cazzata', 'chiavare', 'chiavata', 'chick', 'christ ', 'cristo', 'clitoride', 'coione', 'cojdioonear', 'cojones', 'cojo', 'coglione', 'coglioni', 'cornuto', 'cula', 'culatone', 'culattone', 'culo', 'deficiente', 'deficente', 'dio', 'die ', 'died ', 'ditalino', 'ejackulate', 'enculer', 'eroticunt', 'fanculo', 'fellatio', 'fica ', 'ficken', 'figa', 'sfiga', 'fottere', 'fotter', 'fottuto', 'fuck', 'f.u.c.k.', "funkyass"]
    elencogz = ['gay', 'gaysex', 'hentai.com', 'horne', 'horney', 'hot', 'virgin', 'hot', 'hotties', 'idiot', '@alice.it', 'incest', 'jesus', 'gesu', 'gesù', 'kazzo', 'kill', 'leccaculo', 'lesbian', 'lesbica', 'lesbo', 'masturbazione', 'masturbare', 'masturbo', 'merda', 'merdata', 'merdoso', 'mignotta', 'minchia', 'minkia', 'minchione', 'mona', 'nudo', 'nuda', 'nudi', 'oral', 'sex', 'orgasmso', 'porc', 'pompa', 'pompino', 'porno', 'puttana', 'puzza', 'puzzone', "racchia", 'sborone', 'sborrone', 'sborata', 'sborolata', 'sboro', 'scopata', 'scopare', 'scroto', 'scrotum', 'sega', 'sex', 'sesso', 'shit', 'shiz', 's.h.i.t.', 'sadomaso', 'sodomist', 'stronzata', 'stronzo', 'succhiamelo', 'succhiacazzi', 'testicol', 'troia', 'universetoday.net', 'vaffanculo', 'vagina', 'vibrator', "vacca", 'yiddiot', "zoccola"]
    elenco_others = ['@', ".com", ".sex", ".org", ".uk", ".en", ".it", "admin", "administrator", "amministratore", '@yahoo.com', '@alice.com', "amministratrice", "burocrate", "checkuser", "developer", "http://", "jimbo", 'jimmy wales', 'jymmy wales', 'jymbo wales', 'jimbo waIes', "mediawiki", "on wheals", "on wheal", "on wheel", "on wheels", "planante", "razinger", "sysop", "troll", "vandal", " v.f. ", "v. fighter", "vandal f.", "vandal fighter", 'wales jimmy', "wheels", 'willy wheels', "wales", "www."]
    badword_page = wikipedia.Page(lang, bad_page)
    if badword_page.exists():
        print "Loading the badwords list from Wikipedia..."
        text_bad = badword_page.get()
        list_loaded = badword_function(text_bad)
    else:
        print "         >>>WARNING: The badword-page doesn't exist!<<<"
        list_loaded = list()
    elencovarie = elenco_others + list_loaded
elif filter_wp == False:
    elencoaf = list()
    elencogz = list()
    elencovarie = list()
elenco = elencoaf + elencogz + elencovarie
block = ("B", "b", "Blocco", "blocco", "block", "bloc", "Block", "Bloc", 'Report', 'report')
say_hi = ("S", "s", "Saluto", "saluto", "Welcome", "welcome", 'w', 'W', 'say hi', 'Say hi', 'Hi', 'hi', 'h', 'hello', 'Hello')

#This variable define in what project we are :-) (what language and what project)
welcomesite = wikipedia.Site(lang, project)

# The function used to load the url where the is the new users
def pageText(url):
    try:
	request = urllib2.Request(url)
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
	request.add_header("User-Agent", user_agent)
	response = urllib2.urlopen(request)
	text = response.read()
	response.close()
    # When you load to many users, urllib2 can give this error.
    except urllib2.HTTPError:
        print "Server error. Pausing for 10 seconds before continuing. " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
        time.sleep(10)
	request = urllib2.Request(url)
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
	request.add_header("User-Agent", user_agent)
	response = urllib2.urlopen(request)
	text = response.read()
	response.close()
    return text

done = list()
# The function to load the users (only users who have a certain number of edits)
def parselog(raw):
    users = list()
    pos = 0
    load = True
    # I search with a regex how many user have not the talk page
    # and i put them in a list (i find it more easy and secure)
    while load == True:
        reg = '</a> \(<a href=\"/w/index.php\?title=' + talk + '(.*?)&amp;action=edit'
        p = re.compile(reg, re.UNICODE)
        x = p.search(raw, pos)
        if x == None:
            if len(done) >= 1:
                load = False
                print "\nLoaded all users..."
                continue
            elif len(done) == 0:
                load = False
                print "There is nobody to welcomed..."
                continue
        pos = x.end()
        username = x.group(1)
        if username not in done:
            done.append(username)
        UN = wikipedia.Page(welcomesite, username)
        UNT = wikipedia.Page(welcomesite, talk + username)
        con = 'http://' + wikipedia.getSite().hostname() + '/wiki/' + contib + '/'+ UN.urlname()
        contribs = pageText(con)
        contribnum = contribs.count('<li>') #This is not an accurate count, it just counts the first
                                            #50 contributions
        if contribnum >= number:
            print username + " has enough edits to be welcomed"
            users.append([username, contribnum])
        elif contribnum < number:
            print username + "has only " + str(contribnum) + " contributions"
    return users
hechas = list()

# I've used a function to report the username to a wiki-page
def report(lang, rep_page, username, com):
    another_page = wikipedia.Page(lang, rep_page)
    if another_page.exists():      
        text_get = another_page.get()
    else:
        text_get = ''
    pos = 0
    # The talk page includes "_" between the two names, in this way i replace them to " "
    regex = talk.replace('_', ' ') + username
    n = re.compile(regex, re.UNICODE)
    y = n.search(text_get, pos)
    if y == None:
        # Adding the log :)
        rep_text = rep(username)
        another_page.put(text_get + rep_text, comment = com, minorEdit = True)
        print "...Reported..."
    else:
        pos = y.end()
        print "The user is already in the report page."
# Here there is the main loop
while 1:
    # Here there is the URL of the new users, i've find that this url below is the same for all the project, so it
    # mustn't be changed
    URL = "http://%s/w/index.php?title=Special:Log&type=newusers&user=&page=&limit=%d" % (wikipedia.getSite().hostname(), limit)
    log = pageText(URL).decode('utf-8', 'replace')
    print "I'm going to load the new users (latest " + str(limit) + " users)...\n"
    parsed = parselog(log)
    for tablita in parsed:
        username = str(tablita[0])
        UNT = wikipedia.Page(welcomesite, talk + username)
        baduser = False
        # A check to ensure that the username isn't only composed by numbers.
        try:
            int(username)
            baduser = True
        except ValueError:
            pass
        for word in elenco:
            if word.lower() in username.lower():
                baduser = True                
        if baduser == True:
            running = True
            while running:
                if ask == True:
                    print "%s hasn't got a valid nickname, what shall i do?" % username
                    answer = wikipedia.input(u"[B]lock or [W]elcome?")
                    for w in block:
                        if w in answer:
                            report(lang, rep_page, username, com)
                            running = False
                    for w in say_hi:
                        if w in answer:
                            baduser = False
                            running = False
                elif ask == False:
                    print "%s is possibly not a wanted username. It will be reported." % username
                    report(lang, rep_page, username, com)
                    running = False
        elif baduser == False:
            if not UNT.exists():
                try:
                    UNT.put(welcom, summ)
                    hechas.append(tablita)
                except wikipedia.EditConflict:
                    print "An edit conflict has occured, skipping this edit."
                    continue
        if log_variable == True:
            if len(hechas) == 1:
                print "One user has been welcomed."
            elif len(hechas) == 0:
                print "No users have been welcomed."
            else:
                print str(len(hechas)) + " users have been welcomed."
            if len(hechas) < numberlog:
                continue
            # update the welcome log each fifth welcome message
            elif len(hechas) >= numberlog:
                safety = list()
                #deduct the correct sub page name form the current date.
                rightime = time.localtime(time.time())
                year = str(rightime[0])
                month = str(rightime[1])
                day = str(rightime[2])
                if len(month)==1:
                    month = '0' + month
                    if lang == 'it':
                        pl = wikipedia.Page(welcomesite, logg + '/' + day + '/' + month + '/' + year)
                    if lang == 'commons':
                        pl = wikipedia.Page(welcomesite, logg + '/' + month + '/' + day + '/' + year)
                    else:
                        pl = wikipedia.Page(welcomesite, logg + '/' + year + '/' + month + '/' + day)
                try:
                    safety.append(pl.get())
                except wikipedia.NoPage:
                    #Add the table heading each new period. See http://commons.wikimedia.org/wiki/Commons:Welcome_log
                    if lang == 'it':
                        safety.append('[[Categoria:Benvenuto log|{{subst:PAGENAME}}]]\n{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
                    else:
                        safety.append('{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')                        
                    # The string below show how the "Usernames" will be notified
                    safety.append('\n!' + usernam)
                    # The string below show how the "Contribs" will be notified
                    safety.append('\n!' + contrib)

                for tablita in hechas:
                    UPl = str(tablita[0])
                    cantidad = str(tablita[1])
                    logtext = logfunction(UPl, cantidad)
                    safety.append(logtext)
                try:
                    pl.put(''.join(safety), summ2)
                    hechas = list()
                except wikipedia.EditConflict:
                    print "An edit conflict has occured. Pausing for 10 seconds before continuing."
                    time.sleep(10)
                    pl.put(''.join(safety), summ2)
                    hechas = list()
        elif log_variable == False:
            pass
    # If recursive, don't exit, repeat after one hour
    if recursive == True:
            print "Sleeping " +  str(time_variable) + " seconds before rerun. " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
            time.sleep(time_variable)
    # If not recursive, break
    elif recursive == False:
            print "Stop!"
            wikipedia.stopme()
