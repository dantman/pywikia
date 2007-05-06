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

Everything that needs customisation is indicated by comments.

Description of basic functionality:
* Request a list of new users every period (default: 3600 seconds)
* Check if new user has passed a threshold for a number of edits
  (default: 1 edit)
* Optional: check username for bad words in the username or if the username
  consists solely of numbers; log this somewhere on the wiki (default: False)
* If user has made any edits, check if user has an empty talk page
* If user had an empty talk page, add a welcome message
* Optional: Once the set number of users have been welcomed, add this to the
  configured log page, one for each day (default: True)
* If no log page exists, create a header for the log page first.

This script (by default not yet implemented) uses two templates that need to
be on the local wiki:
* {{WLE}}: contains mark up code for log entries (just copy it from Commons)
* {{welcome}}: contains the information for new users

This script understands the following command-line arguments:
    -edit[:#]      Define how many edits a new user needs to be welcomed
                   (default: 1)

    -time[:#]      Define how many seconds the bot sleeps before restart
                   (default: 3600)

    -break         Use it if you don't want that the Bot restart at the end
                   (it will break) (default: False)

    -nlog          Use this parameter if you do not want the bot to log all
                   welcomed users (default: False)

    -limit[:#]     Use this parameter to define how may users should be
                   checked (default:50)

    -numberlog[:#] The number of users to welcome before refreshing the
                   welcome log (default: 4)

    -filter        Enable the username checks for bad names (default: False)

    -ask           Use this parameter if you want to confirm each possible
                   bad username (default: False)

Known issues/FIXMEs:
* exits when wiki is down.
* user talk namespace name could be extracted from the framework somewhere
 (family files) (would eliminate need for customisation)
* username and contributions (plural) can probably be extracted from wiki
  (eliminates two customisations)
* add variable for how many users to skip (f.e. the 10 latest users, that
  may not have made any edits)
* use default pages if a wiki is not configured, so no configuration of
  the script would be required at all. Suggestion: use English language
  defaults.

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
# Skip it and go down to add you language's parameter
for arg in wikipedia.handleArgs():
    if arg.startswith('-edit'):
        if len(arg) == 5:
            number = int(wikipedia.input(u'After how many edits would you like to welcome new users? (0 is allowed)'))
        else:
            number = int(arg[6:])
    elif arg.startswith('-time'):
        if len(arg) == 5:
            time_variable = int(wikipedia.input(u'For how many seconds would you like to bot to sleep before checking again?'))
        else:
            time_variable = int(arg[6:])
    elif arg == '-break':
        recursive = False
    elif arg == '-nlog':
        log_variable = False
    elif arg == '-ask':
        ask = True
    elif arg == '-filter':
        filter_wp = True        
    elif arg.startswith('-limit'):
        if len(arg) == 6:
            limit = int(wikipedia.input(u'How many of the latest new users would you like to load?'))
        else:
            limit = int(arg[7:])
    elif arg.startswith('-numberlog'):
        if len(arg) == 10:
            numberlog = int(wikipedia.input(u'After how many welcomed users would you like to update the welcome log?'))
        else:
            numberlog = int(arg[11:])

# Find out what project and language the bot will use
lang = config.mylang
project = config.family

#This variable define in what project we are :-) (what language and what project)
welcomesite = wikipedia.Site(lang, project)

# Script users the class wikipedia.translate() to find the right
# page/user/summary/etc so the need to specify language and project have
# been eliminated.
# FIXME: Not all language/project combinations have been defined yet.
#       Add the following strings to customise for a language:
#       logbook, talk_page, summary, netext, summary2, user, con, report_page
#       comment, bad_pag, report_text, logt.

############################################################################
############################################################################
############################################################################

# The text below are dictionaries. Copy the 'en' line, change 'en' in your
# language (f.e. 'de') and modify/translate the text.

#The page where the bot will save the log (f.e. Wikipedia:Welcome log).
logbook = {
    'commons':str(project) + ":Welcome log" ,
    'de':str(project) + ":Willkommen log",
    'en':str(project) + ":Welcome log" ,
    'it':str(project) + ":Benvenuto log",
    'nl':str(project) + ':Logboek welkom',
    'no':str(project) + ':Velkomstlogg',
    }
#The edit summary for the welcome message (f.e. Welcome!)
summary = {
    'commons':'Welcome!',
    'de':'Herzlich Willkommen!',
    'en':'Welcome!',
    'it':'Benvenuto!',
    'nl':'Welkom!',
    'no':'Velkommen!',
    }
# The text for the welcome message (f.e. {{welcome}})
netext = {
    'commons':'{{subst:welcome}}',
    'de':'{{Benutzer:Filnik/Willkommen}}\nViele Grüsse --~~~~',
    'en':'{{subst:welcome}}--~~~~',
    'it':'{{subst:benve|~~~~}}',
    'nl':'{{Welkomstbericht}}',
    'no':'{{subst:bruker:jhs/vk}}',
    }
# The edit summary for updating the welcome log (f.e. Updating log)
summary2 = {
    'commons':'Updating log',
    'de':'Ich neu bearbeite den Logfile',
    'en':'Updating log',
    'it':'Aggiorno il log',
    'nl':'Logboek bijwerken',
    'no':'Oppdaterer logg',
    }
# Contributions in the wiki language (f.e. Contribs)
con = {
    'commons':'Contribs',
    'de':'Beitraege',
    'en':'Contribs',
    'it':'Contributi',
    'nl':'Bijdragen',
    'no':'Bidrag',
    }
# The page where the bot will report users with a possibly bad username.
report_page = {
    'commons':str(project) + ':Administrators\' noticeboard/User problems/Usernames to be checked',
    'de':'Benutzer:Filnik/Report',
    'en':str(project) + ':Administrator intervention against vandalism',
    'it':'Utente:Filbot/Report',
    'nl':str(project) + ':Verzoekpagina voor moderatoren/RegBlok/Te controleren gebruikersnamen',
    'no':'Bruker:JhsBot II/Rapport',
    }
# The edit summary for reporting a possibly bad username.
comment = {
    'commons':'Adding a username that needs to be checked',
    'de':'Adding a username that needs to be checked',
    'en':'Adding a username that needs to be checked',
    'it':'Aggiunto utente da controllare',
    'nl':'Te controleren gebruikersnaam toegevoegd',
    'no':'Legger til et brukernavn som må sjekkes',
    }
# The page where the bot reads the real-time bad words page.
bad_pag = {
    'commons':str(project) + ':Welcome log/Bad_names', 
    'en':str(project) + ':Welcome log/Bad_names',         
    'it':'Utente:Filbot/Bad_words',
    'nl':str(project) + ':Logboek_welkom/Bad_names',
    'no':'Bruker:JhsBot/Daarlige ord',
    }

# The text for reporting a possibly bad username (f.e. *[[Talk_page:Username|Username]])
report_text = {
        'commons':"\n*{{user3|%s}}" + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'de':'\n*[[Benutzer_Diskussion:%s]] ' + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'en':'\n*{{Userlinks|%s}} ' + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'it':"\n*[[Discussioni utente:%s]] " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'nl':'\n*{{linkgebruiker%s}} ' + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'no':'\n*{{bruker|%s}} ' + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()),
        }    

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = ['commons', 'de', 'en', 'it', 'nl', 'no']

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project ;)
################################################################################################################################################    
################################################################################################################################################   
################################################################################################################################################    

# A little block-statement to ensure that the bot won't start with en-parameters
if lang not in project_inserted:
    wikipedia.output(u"Your project is not supported by the framework. You have to edit the script and add it!")
    wikipedia.stopme()

# The follow lines translate the language's parameters.
contib = 'Special:Contributions'
usernam = welcomesite.namespace(2)
welcom = wikipedia.translate(wikipedia.getSite(), netext)
summ = wikipedia.translate(wikipedia.getSite(), summary)
logg = wikipedia.translate(wikipedia.getSite(), logbook)
summ2 = wikipedia.translate(wikipedia.getSite(), summary2)
contrib = wikipedia.translate(wikipedia.getSite(), con)
rep_page = wikipedia.translate(wikipedia.getSite(), report_page)
com = wikipedia.translate(wikipedia.getSite(), comment)
bad_page = wikipedia.translate(wikipedia.getSite(), bad_pag)
rep_text = wikipedia.translate(wikipedia.getSite(), report_text)

# There is the talk page ^__^ the talk_page's variable gives "Talk page" and i change it "Talk_page:"
talk_page = welcomesite.namespace(3)
talk = talk_page.replace(" ", "_") + ":"

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
                wikipedia.output(u"\nBad words loaded.")
                load_2 = False
                return list_loaded
            elif len(done) == 0:
                wikipedia.output(u"There was no input on the page with bad words.")
                load_2 = False
                continue
        pos = xl.end()
        badword = xl.group(2)
        if badword not in list_loaded:
             list_loaded.append(badword)
if filter_wp == True:
    # A standard list of bad username components
    elencoaf = [' ano', ' anus', 'anal ', 'babies', 'baldracca', 'balle', 'bastardo', 'bestiali', 'bestiale', 'bastarda', 'b.i.t.c.h.', 'bitch', 'boobie', 'bordello', 'breast', 'cacata', 'cacca', 'cachapera', 'cagata', 'cane', 'cazz', 'cazzo', 'cazzata', 'chiavare', 'chiavata', 'chick', 'christ ', 'cristo', 'clitoride', 'coione', 'cojdioonear', 'cojones', 'cojo', 'coglione', 'coglioni', 'cornuto', 'cula', 'culatone', 'culattone', 'culo', 'deficiente', 'deficente', 'dio', 'die ', 'died ', 'ditalino', 'ejackulate', 'enculer', 'eroticunt', 'fanculo', 'fellatio', 'fica ', 'ficken', 'figa', 'sfiga', 'fottere', 'fotter', 'fottuto', 'fuck', 'f.u.c.k.', "funkyass"]
    elencogz = ['gay', 'gaysex', 'hentai.com', 'horne', 'horney', 'hot', 'virgin', 'hot', 'hotties', 'idiot', '@alice.it', 'incest', 'jesus', 'gesu', 'gesù', 'kazzo', 'kill', 'leccaculo', 'lesbian', 'lesbica', 'lesbo', 'masturbazione', 'masturbare', 'masturbo', 'merda', 'merdata', 'merdoso', 'mignotta', 'minchia', 'minkia', 'minchione', 'mona', 'nudo', 'nuda', 'nudi', 'oral', 'sex', 'orgasmso', 'porc', 'pompa', 'pompino', 'porno', 'puttana', 'puzza', 'puzzone', "racchia", 'sborone', 'sborrone', 'sborata', 'sborolata', 'sboro', 'scopata', 'scopare', 'scroto', 'scrotum', 'sega', 'sex', 'sesso', 'shit', 'shiz', 's.h.i.t.', 'sadomaso', 'sodomist', 'stronzata', 'stronzo', 'succhiamelo', 'succhiacazzi', 'testicol', 'troia', 'universetoday.net', 'vaffanculo', 'vagina', 'vibrator', "vacca", 'yiddiot', "zoccola"]
    elenco_others = ['@', ".com", ".sex", ".org", ".uk", ".en", ".it", "admin", "administrator", "amministratore", '@yahoo.com', '@alice.com', "amministratrice", "burocrate", "checkuser", "developer", "http://", "jimbo", 'jimmy wales', 'jymmy wales', 'jymbo wales', 'jimbo waIes', "mediawiki", "on wheals", "on wheal", "on wheel", "on wheels", "planante", "razinger", "sysop", "troll", "vandal", " v.f. ", "v. fighter", "vandal f.", "vandal fighter", 'wales jimmy', "wheels", 'willy wheels', "wales", "www."]
    badword_page = wikipedia.Page(lang, bad_page)
    if badword_page.exists():
        wikipedia.output(u"Loading the bad words list from " + wikipedia.getSite().hostname() + u"...")
        text_bad = badword_page.get()
        list_loaded = badword_function(text_bad)
    else:
        wikipedia.output(u"         >>>WARNING: The bad word page does not exist!<<<")
        list_loaded = list()
    elencovarie = elenco_others + list_loaded
elif filter_wp == False:
    elencoaf = list()
    elencogz = list()
    elencovarie = list()
elenco = elencoaf + elencogz + elencovarie
block = ("B", "b", "Blocco", "blocco", "block", "bloc", "Block", "Bloc", 'Report', 'report')
say_hi = ("S", "s", "Saluto", "saluto", "Welcome", "welcome", 'w', 'W', 'say hi', 'Say hi', 'Hi', 'hi', 'h', 'hello', 'Hello')

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
        wikipedia.output(u"Server error. Pausing for 10 seconds before continuing. " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()))
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
        reg = '\(<a href=\"/w/index.php\?title=' + talk + '(.*?)&(amp;|)action=edit\"'
        p = re.compile(reg, re.UNICODE)
        x = p.search(raw, pos)
        if x == None:
            if len(done) >= 1:
                load = False
                wikipedia.output(u"\nLoaded all users...")
                continue
            elif len(done) == 0:
                load = False
                wikipedia.output(u"There is nobody to welcomed...")
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
            wikipedia.output( username + u" has enough edits to be welcomed")
            users.append([username, contribnum])
        elif contribnum < number:
            if contribnum == 0:
                wikipedia.output( username + u" has no contributions")
            else:
                wikipedia.output( username + u" has only " + str(contribnum) + u" contributions")
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
        rep_text = rep_text % username
        another_page.put(text_get + rep_text, comment = com, minorEdit = True)
        wikipedia.output(u"...Reported...")
    else:
        pos = y.end()
        wikipedia.output(u"The user is already in the report page.")
# Here there is the main loop
while 1:
    # Here there is the URL of the new users, i've find that this url below is the same for all the project, so it
    # mustn't be changed
    URL = "http://%s/w/index.php?title=Special:Log&type=newusers&user=&page=&limit=%d" % (wikipedia.getSite().hostname(), limit)
    log = pageText(URL).decode('utf-8', 'replace')
    wikipedia.output(u"Loading latest " + str(limit) + u" new users from " + (wikipedia.getSite().hostname()) + u"...\n")
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
                    wikipedia.output(u"%s hasn't got a valid nickname, what shall i do?" % username )
                    answer = wikipedia.input("[B]lock or [W]elcome?")
                    for w in block:
                        if w in answer:
                            report(lang, rep_page, username, com)
                            running = False
                    for w in say_hi:
                        if w in answer:
                            baduser = False
                            running = False
                elif ask == False:
                    wikipedia.output(u"%s is possibly not a wanted username. It will be reported." % username )
                    report(lang, rep_page, username, com)
                    running = False
        elif baduser == False:
            if not UNT.exists():
                try:
                    UNT.put(welcom, summ)
                    hechas.append(tablita)
                except wikipedia.EditConflict:
                    wikipedia.output(u"An edit conflict has occured, skipping this user.")
                    continue
        if log_variable == True:
            if len(hechas) == 1:
                wikipedia.output(u"One user has been welcomed.")
            elif len(hechas) == 0:
                wikipedia.output(u"No users have been welcomed.")
            else:
                wikipedia.output( str(len(hechas)) + u" users have been welcomed.")
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
                    elif lang == 'commons':
                        pl = wikipedia.Page(welcomesite, logg + '/' + month + '/' + day + '/' + year)
                    else:
                        pl = wikipedia.Page(welcomesite, logg + '/' + year + '/' + month + '/' + day)
                try:
                    safety.append(pl.get())
                except wikipedia.NoPage:
                    #Add the table heading each new period. See http://commons.wikimedia.org/wiki/Commons:Welcome_log
                    if lang == 'it':
                        safety.append('[[Categoria:Benvenuto log|{{subst:PAGENAME}}]]\n{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
                    elif lang == 'no':
                        safety.append('[[Kategori:Velkomstlogg|{{PAGENAME}}]]\n{| class="wikitable"')
                    else:
                        safety.append('{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')                        
                    # The string below show how the "Usernames" will be notified
                    safety.append('\n!' + usernam)
                    # The string below show how the "Contribs" will be notified
                    safety.append('\n!' + contrib)

                for tablita in hechas:
                    UPl = str(tablita[0])
                    cantidad = str(tablita[1])
                    logtext = '\n{{WLE|user=' + UPl + '|contribs=' + cantidad + '}}'
                    safety.append(logtext)
                try:
                    pl.put(''.join(safety), summ2)
                    hechas = list()
                except wikipedia.EditConflict:
                    wikipedia.output(u"An edit conflict has occured. Pausing for 10 seconds before continuing.")
                    time.sleep(10)
                    pl.put(''.join(safety), summ2)
                    hechas = list()
        elif log_variable == False:
            pass
    # If recursive, don't exit, repeat after one hour
    if recursive == True:
            wikipedia.output(u"Sleeping " +  str(time_variable) + u" seconds before rerun. " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()))
            time.sleep(time_variable)
    # If not recursive, break
    elif recursive == False:
            wikipedia.output(u"Stop!")
            wikipedia.stopme()
            break
