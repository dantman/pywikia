#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to welcome new users. This script works out of the box for Wikis that
have been defined in the script. It is currently used on the Dutch, Norwegian,
Arabian, Albanian, Italian Wikipedia, Wikimedia Commons and English Wikiquote.

Note: You can download the latest version available
from here: http://botwiki.sno.cc/wiki/Python:Welcome.py

Ensure you have community support before running this bot!

URLs to current implementations:
* Arabic Wikipedia: http://ar.wikipedia.org/wiki/ويكيبيديا:سجل الترحيب
* Wikimedia Commons: http://commons.wikimedia.org/wiki/Commons:Welcome_log
* Dutch Wikipedia: http://nl.wikipedia.org/wiki/Wikipedia:Logboek_welkom
* Italian Wikipedia: http://it.wikipedia.org/wiki/Wikipedia:Benvenuto_log
* English Wikiquote: http://en.wikiquote.org/wiki/Wikiquote:Welcome_log

Everything that needs customisation to support additional projects is
indicated by comments.

Description of basic functionality:
* Request a list of new users every period (default: 3600 seconds)
  You can choose to break the script after the first check (see arguments)
* Check if new user has passed a threshold for a number of edits
  (default: 1 edit)
* Optional: check username for bad words in the username or if the username
  consists solely of numbers; log this somewhere on the wiki (default: False)
  Update: Added a whitelist (explanation below).
* If user has made enough edits (it can be also 0), check if user has an empty
  talk page
* If user has an empty talk page, add a welcome message.
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

    -random        Use a random signature, taking the signatures from a wiki
                   page (for istruction, see below).

********************************* GUIDE ***********************************

Report, Bad and white list guide:

1)  Set in the code which page it will use to load the badword, the
    whitelist and the report
2)  In these page you have to add a "tuple" with the names that you want to
    add in the two list. For example: ('cat', 'mouse', 'dog')
    You can write also other text in the page, it will work without problem.
3)  What will do the two pages? Well, the Bot will check if a badword is in
    the username and set the "warning" as True. Then the Bot check if a word
    of the whitelist is in the username. If yes it remove the word and
    recheck in the bad word list to see if there are other badword in the
    username.
    Example:
        * dio is a badword
        * Claudio is a normal name
        * The username is "Claudio90 fuck!"
        * The Bot find dio and set "warning"
        * The Bot find Claudio and set "ok"
        * The Bot find fuck at the end and set "warning"
        * Result: The username is reported.
4)  When a user is reported you have to check him and do:
        * If he's ok, put the {{welcome}}
        * If he's not, block him
        * You can decide to put a "you are blocked, change another username"
          template or not.
        * Delete the username from the page.
        IMPORTANT : The Bot check the user in this order:
            * Search if he has a talkpage (if yes, skip)
            * Search if he's blocked, if yes he will be skipped
            * Search if he's in the report page, if yes he will be skipped
            * If no, he will be reported.

Random signature guide:

Some welcomed users will answer to the one who has signed the welcome message.
When you welcome many new users, you might be overwhelmed with such answers.
Therefore you can define usernames of other users who are willing to receive
some of these messages from newbies.

1) Set the page that the bot will load
2) Add the signatures in this way:

*<white space>SIGNATURE
<new line>

Example:
<pre>
* [[User:Filnik|Filnik]]
* [[User:Rock|Rock]]
</pre>

NOTE: The white space and <pre></pre> aren't required but I suggest you to
      use them.

*************************** Known issues/FIXMEs ****************************
* exits when wiki is down.
* add variable for how many users to skip (e.g. the 10 latest users, that
  may not have made any edits)
* use default pages if a wiki is not configured, so no configuration of
  the script would be required at all. Suggestion: use English language
  defaults.
* The regex to load the user might be slightly different from project to project.
  (in this case, write to Filnik for help...)
* If the User talk: translation has non-standard character it won't work.
* Add in the report, the badword used to detect the user.
* Add the template, without subst:
* Make object-oriented
"""
#
# (C) Alfio, 2005
# (C) Kyle/Orgullomoore, 2006-2007
# (C) Siebrand Mazeland, 2006-2007
# (C) Filnik, 2007
# (C) Daniel Herding, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: welcome.py,v 1.4 2007/04/14 18:05:42 siebrand Exp'
#

import wikipedia
import time, re, config

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
# welcome or to write his name in the bad-username list
ask = False
# filter_wp = A filter to check if the username is ok or not
filter_wp = False
# Setting the default sign.
sign = '--~~~~'
# Setting if the sign must be random or not
random = False

# Script users the class wikipedia.translate() to find the right
# page/user/summary/etc so the need to specify language and project have
# been eliminated.
# FIXME: Not all language/project combinations have been defined yet.
#       Add the following strings to customise for a language:
#       logbook, talk_page, summary, netext, summary2, user, con, report_page
#       comment, bad_pag, report_text, logt, random_sign and whitelist_pg.

############################################################################
############################################################################
############################################################################

# The text below are dictionaries. Copy the 'en' line, change 'en' in your
# language (e.g. 'de') and modify/translate the text.

#The page where the bot will save the log (e.g. Wikipedia:Welcome log).
logbook = {
    'commons': u"Project:Welcome log" ,
    'ar': u'Project:سجل الترحيب',
    # no welcome log on de:
    'de': None,
    'en': u'Project:Welcome log',
    'it': u'Project:Benvenuto log',
    'nl': u'Project:Logboek welkom',
    'no': u'Project:Velkomstlogg',
    'sq': u'Project:Tung log',
    }
#The edit summary for the welcome message (e.g. Welcome!).
summary = {
    'commons':u'Welcome!',
    'ar':u'مرحبا!',
    'de':u'Herzlich willkommen!',
    'en':u'Welcome!',
    'it':u'Benvenuto!',
    'nl':u'Welkom!',
    'no':u'Velkommen!',
    'sq':u'Tung'
    }
# The text for the welcome message (e.g. {{welcome}}) and %s at the end
# that is your signature (the bot has a random parameter to add different
# sign, so in this way it will change according to your parameters).
netext = {
    'commons':u'{{subst:welcome}}%s',
    'ar':u'{{نسخ:مستخدم:Alnokta/ترحيب}}%s',
    'de':u'{{subst:Hallo}} %s',
    'en':u'{{subst:welcome}}%s',
    'it':u'{{Template:Benvebot}} %s',
    'nl':u'{{Welkomstbericht}}%s',
    'no':u'{{subst:bruker:jhs/vk}}%s',
    'sq':u'{{subst:tung}}%s',
    }
# The edit summary for updating the welcome log (e.g. Updating log).
summary2 = {
    'commons':u'Updating log',
    'ar':u'تحديث السجل',
    'de':u'Aktualisiere Logdatei',
    'en':u'Updating log',
    'it':u'Aggiorno il log',
    'nl':u'Logboek bijwerken',
    'no':u'Oppdaterer logg',
    'sq':u'Rifreskoj log',
    }
# Contributions in the wiki language (e.g. Contribs).
con = {
    'commons':u'Contribs',
    'ar':u'مساهمات',
    'de':u'Beiträge',
    'en':u'Contribs',
    'it':u'Contributi',
    'nl':u'Bijdragen',
    'no':u'Bidrag',
    'sq':u'Kontribute',
    }
# The page where the bot will report users with a possibly bad username.
report_page = {
    'commons': u'Project:Administrators\' noticeboard/User problems/Usernames to be checked',
    'ar': 'Project:إخطار الإداريين/أسماء مستخدمين للفحص',
    'de': u'Benutzer:Filnik/Report',
    'en': u'Project:Administrator intervention against vandalism',
    'it': u'Utente:Filbot/Report',
    'nl': u'Project:Verzoekpagina voor moderatoren/RegBlok/Te controleren gebruikersnamen',
    'no': u'Bruker:JhsBot II/Rapport',
    'sq': u'User:EagleBot/Report',
    }
# The edit summary for reporting a possibly bad username.
comment = {
    'commons':u'Adding a username that needs to be checked',
    'ar':u'إضافة اسم مستخدم يحتاج للفحص',
    'de':u'Ergänze zu überprüfenden Benutzernamen',
    'en':u'Adding a username that needs to be checked',
    'it':u'Aggiunto utente da controllare',
    'nl':u'Te controleren gebruikersnaam toegevoegd',
    'no':u'Legger til et brukernavn som m? sjekkes',
    'sq':u'Added username to be checked',
    }
# The page where the bot reads the real-time bad words page
# (this parameter is optional).
bad_pag = {
    'commons': u'Project:Welcome log/Bad_names',
    'ar': u'Project:سجل الترحيب/أسماء سيئة',
    'en': u'Project:Welcome log/Bad_names',
    'it': u'Utente:Filbot/Bad_words',
    'nl': u'Project:Logboek_welkom/Bad_names',
    'no': u'Bruker:JhsBot/Daarlige ord',
    'sq': u'User:Eagleal/Bad_names',
    }

# The text for reporting a possibly bad username (e.g. *[[Talk_page:Username|Username]]).
# TODO: don't get the time at initialization, but when the template is used.
report_text = {
        'commons':u"\n*{{user3|%s}}" + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'ar':u"\n*{{user13|%s}}" + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'de':u'\n*[[Benutzer Diskussion:%s]] ' + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'en':u'\n*{{Userlinks|%s}} ' + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'it':u"\n{{Reported|%s|",
        'nl':u'\n*{{linkgebruiker%s}} ' + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        'no':u'\n*{{bruker|%s}} ' + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()),
        u'sq':'\n*[[User:%s]] ' + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.localtime()),
        }

# Set where you load your list of signs that the bot will load if you use
# the random argument (this parameter is optional).
random_sign = {
        'ar': u'ويكيبيديا:سجل الترحيب/توقيعات',
        'en': u'User:Filnik/Sign',
        'it': u'Project:Benvenuto log/User',
        }
# The page where the bot reads the real-time whitelist page.
# (this parameter is optional).
whitelist_pg = {
        'ar':u'ويكيبيديا:سجل الترحيب/قائمةبيضاء',
        'en':u'User:Filnik/whitelist',
        'it':u'Utente:Filbot/whitelist',
        }

# Add your project (in alphabetical order) if you want that the bot start.
project_inserted = ['ar', 'commons', 'de', 'en', 'it', 'nl', 'no', 'sq']

# Ok, that's all. What is below, is the rest of code, now the code is fixed
# and it will run correctly in your project ;)
############################################################################
############################################################################
############################################################################

def load_word_function(wsite, raw):
    # This is a function used to load the badword and the whitelist.
    list_loaded = list()
    pos = 0
    # I search with a regex how many user have not the talk page
    # and i put them in a list (i find it more easy and secure)
    while 1:
        regl = "(\"|\')(.*?)(\"|\')(, |\))"
        page = re.compile(regl, re.UNICODE)
        xl = page.search(raw, pos)
        if xl == None:
            if len(list_loaded) >= 1:
                wikipedia.output(u"\nReal-time list loaded.")
                return list_loaded
                break
            elif len(done) == 0:
                wikipedia.output(u"There was no input on the real-time page.")
                load_2 = False
                continue
        pos = xl.end()
        badword = xl.group(2)
        if badword not in list_loaded:
             list_loaded.append(badword)

def parselog(wsite, raw):
    # The function to load the users (only users who have a certain number of edits)
    done = list()
    users = list()
    load = list()
    pos = 0
    # I search with a regex how many user have not the talk page
    # and i put them in a list (i find it more easy and secure)
    while 1:
        # FIXME: That's the regex, if there are problems, take a look here.
        reg = '\(<a href=\"/w/index.php\?title=' + talk + '(.*?)&(amp;|)action=edit\"'
        p = re.compile(reg, re.UNICODE)
        x = p.search(raw, pos)
        if x == None:
            if len(done) >= 1:
                wikipedia.output(u"\nLoaded all users...")
                break
            elif len(done) == 0:
                wikipedia.output(u"There is nobody to be welcomed...")
                break
        pos = x.end()
        username = x.group(1)
        if username not in done:
            done.append(username)
        userpage = wikipedia.Page(wsite, username)
        usertalkpage = wikipedia.Page(wsite, talk + username)
        # Defing the contrib's page of the user
        # TODO: Doesn't work if path is not /wiki/
        con = '/wiki/Special:Contributions/'+ userpage.urlname()
        # Getting the contribs...
        contribs = wsite.getUrl(con)
        contribnum = contribs.count('<li>') #This is not an accurate count, it just counts the first
                                            #50 contributions (but it works ^__^)
        # That's a little trick to wait some times before continue to
        # load users. It won't stress to much the servers.
        if len(load) != 0:
            res = len(load) / 10.0
            resq = str(res).split('.')
            if resq[1] == '0':
                wikipedia.output(u"Sleeping for 10 seconds, %s...\n" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                time.sleep(10)
        if contribnum >= number:
            wikipedia.output(username + u" has enough edits to be welcomed")
            users.append([username, contribnum])
            load.append([username, contribnum])
        elif contribnum < number:
            if contribnum == 0:
                wikipedia.output(username + u" has no contributions")
                load.append([username, contribnum])
            else:
                wikipedia.output(username + u" has only " + str(contribnum) + u" contributions")
                load.append([username, contribnum])
    return users

def report(wsite, rep_page, username, com, rep):
    # I've used a function to report the username to a wiki-page.
    another_page = wikipedia.Page(wsite, rep_page)
    if another_page.exists():
        text_get = another_page.get()
    else:
        text_get = "This is a report page for the Bad-username, please translate me. --[[User:%s|%s]]" % (config.usernames[project], config.usernames[project])
    pos = 0
    # The talk page includes "_" between the two names, in this way i replace them to " "
    username = wikipedia.url2link(username, wsite, wsite)
    regex = username
    n = re.compile(regex, re.UNICODE)
    y = n.search(text_get, pos)
    if y == None:
        # Adding the log :)
        rep_text = rep % username
        another_page.put(text_get + rep_text, comment = com, minorEdit = True)
        wikipedia.output(u"...Reported...")
    else:
        pos = y.end()
        wikipedia.output(username + u" is already in the report page.")

def blocked(wsite, username):
    #A little function to check if the user has already been blocked (to skip him).
    reg = """<li>[0-9][0-9]:[0-9][0-9], [0-9]([0-9])? (.*?) [0-9][0-9][0-9][0-9] <a href=\"/wiki/(.*?)\" title=\"(.*?)\">(.*?)</a> \(<a href=\"/wiki/(.*?)\" title=\"(.*?)\">(.*?)</a>"""
    block_text = wsite.getUrl('/w/index.php?title=Special:Log/block&page=User:' + username)
    numblock = re.findall(reg, block_text)
    # If the bot doesn't find block-line, it will return False otherwise True.
    if len(numblock) == 0:
        return False
    else:
        return True

def defineSign(wsite, signPageTitle):
    #A little function to load the random signs.
    signPage = wikipedia.Page(wsite, signPageTitle)
    signText = signPage.get()
    reg = "\* ?(.*?)\n"
    listSign = re.findall(reg, signText)
    return listSign

if __name__ == "__main__":
    # The block below is used for the parameters
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
        elif arg == '-random':
            random = True
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
    # The site
    wsite = wikipedia.getSite()
    # A little block-statement to ensure that the bot won't start with en-parameters
    if wsite.lang not in project_inserted:
        wikipedia.output(u"Your project is not supported by the framework. You have to edit the script and add it!")
        wikipedia.stopme()

    # The follow lines translate the language's parameters.
    usernam = wsite.namespace(2)
    welcomer = wikipedia.translate(wsite, netext)
    summ = wikipedia.translate(wsite, summary)
    logg = wikipedia.translate(wsite, logbook)
    summ2 = wikipedia.translate(wsite, summary2)
    contrib = wikipedia.translate(wsite, con)
    rep_page = wikipedia.translate(wsite, report_page)
    com = wikipedia.translate(wsite, comment)
    bad_page = wikipedia.translate(wsite, bad_pag)
    rep_text = wikipedia.translate(wsite, report_text)
    signPageTitle = wikipedia.translate(wsite, random_sign)
    wtlpg = wikipedia.translate(wsite, whitelist_pg)

    # There is the talk page ^__^ the talk_page's variable gives "Talk page" and
    # i change it "Talk_page:"
    talk_page = wsite.namespace(3)
    talk = talk_page.replace(" ", "_") + ":"

    # If your User talk in your language has a special charachter the script won't work, that
    # block fix this bug. (i will find a better way to resolve this problem, as soon as possible).

    if wsite.lang == 'ar':
        talk = '%D9%86%D9%82%D8%A7%D8%B4_%D8%A7%D9%84%D9%85%D8%B3%D8%AA%D8%AE%D8%AF%D9%85:'
    elif wsite.lang == 'sq':
        talk = 'P%C3%ABrdoruesi_diskutim:'

    # A parameter for different projects of the same language...
    if wsite.family.name == "wikinews":
        if wsite.lang == "it":
            logg = 'Wikinotizie:Benvenuto log'
            welcomer = "{{subst:benvenuto|%s}}"
            sign = 'Tooby'
    elif wsite.family.name == "wiktionary":
        if wsite.lang == "it":
            logg = 'Wiktionary:Benvenuto log'
            welcomer = '{{subst:Utente:Filnik/Benve|nome={{subst:PAGENAME}}}} %s'

    hechas = list()
    number_user = 0
    # Use try and finally, to put the wikipedia.stopme() always at the end of the code.
    try:
        # Here there is the main loop.
        while True:
            if filter_wp == True:
                # A standard list of bad username components (you can change/delate it in your project...) [ i divide the list into two to make it smaller...]
                elencoaf = [' ano', ' anus', 'anal ', 'babies', 'baldracca', 'balle', 'bastardo',
                            'bestiali', 'bestiale', 'bastarda', 'b.i.t.c.h.', 'bitch', 'boobie',
                            'bordello', 'breast', 'cacata', 'cacca', 'cachapera', 'cagata',
                            'cane', 'cazz', 'cazzo', 'cazzata', 'chiavare', 'chiavata', 'chick',
                            'christ ', 'cristo', 'clitoride', 'coione', 'cojdioonear', 'cojones',
                            'cojo', 'coglione', 'coglioni', 'cornuto', 'cula', 'culatone',
                            'culattone', 'culo', 'deficiente', 'deficente', 'dio', 'die ',
                            'died ', 'ditalino', 'ejackulate', 'enculer', 'eroticunt', 'fanculo',
                            'fellatio', 'fica ', 'ficken', 'figa', 'sfiga', 'fottere', 'fotter',
                            'fottuto', 'fuck', 'f.u.c.k.', "funkyass"]
                elencogz = ['gay', 'hentai.com', 'horne', 'horney', 'virgin', 'hotties', 'idiot',
                            '@alice.it', 'incest', 'jesus', 'gesu', 'gesù', 'kazzo', 'kill',
                            'leccaculo', 'lesbian', 'lesbica', 'lesbo', 'masturbazione',
                            'masturbare', 'masturbo', 'merda', 'merdata', 'merdoso', 'mignotta',
                            'minchia', 'minkia', 'minchione', 'mona', 'nudo', 'nuda', 'nudi',
                            'oral', 'sex', 'orgasmso', 'porc', 'pompa', 'pompino', 'porno',
                            'puttana', 'puzza', 'puzzone', "racchia", 'sborone', 'sborrone',
                            'sborata', 'sborolata', 'sboro', 'scopata', 'scopare', 'scroto',
                            'scrotum', 'sega', 'sesso', 'shit', 'shiz', 's.h.i.t.', 'sadomaso',
                            'sodomist', 'stronzata', 'stronzo', 'succhiamelo', 'succhiacazzi',
                            'testicol', 'troia', 'universetoday.net', 'vaffanculo', 'vagina',
                            'vibrator', "vacca", 'yiddiot', "zoccola"]
                elenco_others = ['@', ".com", ".sex", ".org", ".uk", ".en", ".it", "admin",
                                "administrator", "amministratore", '@yahoo.com', '@alice.com',
                                "amministratrice", "burocrate", "checkuser", "developer",
                                "http://", "jimbo", "mediawiki", "on wheals", "on wheal",
                                "on wheel", "planante", "razinger", "sysop", "troll", "vandal",
                                " v.f. ", "v. fighter",
                                "vandal f.", "vandal fighter", 'wales jimmy', "wheels", "wales",
                                "www."]
                badword_page = wikipedia.Page(wsite, bad_page)
                if badword_page.exists():
                    wikipedia.output(u"\nLoading the bad words list from " + wsite.hostname() + u"...")
                    text_bad = badword_page.get()
                    list_loaded = load_word_function(wsite,text_bad)
                else:
                    wikipedia.output(u"\t\t>>>WARNING: The bad word page doesn't exist!<<<")
                    list_loaded = list()
                # Joining the "other things" with the loaded...
                elencovarie = elenco_others + list_loaded
            elif filter_wp == False:
                elencoaf = list()
                elencogz = list()
                elencovarie = list()
            # ^__^ Joined the three lists..
            elenco = elencoaf + elencogz + elencovarie
            if filter_wp == True:
                # That is the default whitelist (it contains few name because it has been improved in the latest days..)
                whitelist_default = ['emiliano']
                whitelist_page = wikipedia.Page(wsite, wtlpg)
                if whitelist_page.exists():
                    wikipedia.output(u"\nLoading the whitelist from " + wsite.hostname() + u"...")
                    text_white = whitelist_page.get()
                    list_white = load_word_function(wsite,text_white)
                else:
                    wikipedia.output(u"\t\t>>>WARNING: The whitelist's page doesn't exist!<<<")
                    list_white = list()
            else:
                list_white = list()
                whitelist_default = list()
            # Joined the whitelist words
            whitelist = list_white + whitelist_default
            # List of word that the Bot understand when it ask you something...
            block = ("B", "b", "Blocco", "blocco", "block", "bloc", "Block", "Bloc", 'Report', 'report')
            say_hi = ("S", "s", "Saluto", "saluto", "Welcome", "welcome", 'w', 'W', 'say hi',
                    'Say hi', 'Hi', 'hi', 'h', 'hello', 'Hello')

            # Here there is the URL of the new users, i've find that this url below is the same for all the project, so it
            # mustn't be changed
            URL = "/w/index.php?title=Special:Log&type=newusers&user=&page=&limit=%d" % limit
            log = wsite.getUrl(URL)
            wikipedia.output(u"Loading latest " + str(limit) + u" new users from " + (wsite.hostname()) + u"...\n")
            parsed = parselog(wsite,log)
            # Defing what sign the Bot will use
            if random == True:
                try:
                    wikipedia.output(u"Loading random signs...")
                    signList = defineSign(wsite,signPageTitle)
                except wikipedia.NoPage:
                    wikipedia.output(u"The sign's list isn't available... using default sign...")
                    random = False
            for found_result in parsed:
                # Defing the final sign...
                if random == True:
                    if number_user + 1> len(signList):
                        number_user = 0
                    welcom = welcomer % signList[number_user] + '{{subst:LOCALTIME}}, {{subst:CURRENTDAY}} {{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}} (UTC).'
                else:
                    welcom = welcomer % sign
                username = str(found_result[0])
                usertalkpage = wikipedia.Page(wsite, talk + username)
                baduser = False
                # Check if the username is composed by only numbers.
                try:
                    int(username)
                    baduser = True
                except ValueError:
                    # Ok, no problem ^__^
                    pass
                # Check if the user has been already blocked
                ki = blocked(wsite,username)
                if ki == True:
                    wikipedia.output(username + u' has been blocked! Skipping him...')
                    continue
                # Understand if the user has a bad-username
                for word in elenco:
                    username = str(username).encode(config.console_encoding)
                    if word.lower() in username.lower():
                        baduser = True
                        if wsite.lang == 'it':
                            final_rep = rep_text + word + '}}'
                            break
                        else:
                            final_rep = rep_text
                # Checking in the whitelist...
                for xy in whitelist:
                    if xy.lower() in username.lower():
                        username.replace(xy, '')
                        for word in elenco:
                            if word.lower() in username.lower():
                                baduser = True
                            else:
                                baduser = False
                # He has a badusername, trying to report him...
                if baduser == True:
                    while 1:
                        if ask == True:
                            wikipedia.output(u"%s hasn't got a valid username, what shall i do?" % username )
                            answer = wikipedia.input(u"[B]lock or [W]elcome?")
                            for w in block:
                                if w in answer:
                                    if not usertalkpage.exists():
                                        # Check if the user has been already blocked (second check)
 	 	                        ki = blocked(wsite, username)
 	 	                        if ki == True:
 	 	                            wikipedia.output(username + u' has been blocked! Skipping him...')
 	 	                            continue
                                        report(wsite, rep_page, username, com, final_rep)
                                        break
                                    else:
                                        wikipedia.output(u'The discussion page of the bad-user already exist...')
                                        running = False
                            for w in say_hi:
                                if w in answer:
                                    baduser = False
                                    break
                        elif ask == False:
                            wikipedia.output(u"%s is possibly not a wanted username. It will be reported." % username)
                            if not usertalkpage.exists():
                                report(wsite, rep_page, username, com, final_rep)
                                break
                            else:
                                wikipedia.output(u'The discussion page of the bad-user already exist...')
                                break
                # He has a good username, welcome!
                elif baduser == False:
                    if not usertalkpage.exists():
                        # Tring to put the welcome...
                        try:
                            # make non-minor edit to trigger new talk page message
                            usertalkpage.put(welcom, summ, minorEdit = False)
                            hechas.append(found_result)
                            if random == True:
                                number_user += 1
                        except wikipedia.EditConflict:
                            wikipedia.output(u"An edit conflict has occured, skipping this user.")
                            continue
                    else:
                        wikipedia.output(username + u" has been already welcomed when i was loading all the users... skipping")
                        continue
                # That's the log ^__^
                if log_variable == True and logg:
                    if len(hechas) == 1:
                        wikipedia.output(u"One user has been welcomed.")
                    elif len(hechas) == 0:
                        wikipedia.output(u"No users have been welcomed.")
                    else:
                        wikipedia.output( str(len(hechas)) + u" users have been welcomed.")
                    if len(hechas) < numberlog:
                        continue
                    # Update the welcome log each fifth welcome message
                    elif len(hechas) >= numberlog:
                        safety = list()
                        # Deduct the correct sub page name form the current date.
                        rightime = time.localtime(time.time())
                        year = str(rightime[0])
                        month = str(rightime[1])
                        day = str(rightime[2])
                        if len(month)==1:
                            month = '0' + month
                            if wsite.lang == 'it':
                                target = logg + '/' + day + '/' + month + '/' + year
                            elif wsite.lang == 'commons':
                                target = logg + '/' + month + '/' + day + '/' + year
                            else:
                                target = logg + '/' + year + '/' + month + '/' + day
                        page = wikipedia.Page(wsite, target)
                        try:
                            safety.append(page.get())
                        except wikipedia.NoPage:
                            #Add the table heading each new period. See http://commons.wikimedia.org/wiki/Commons:Welcome_log
                            if wsite.lang == 'it':
                                safety.append('[[Categoria:Benvenuto log|{{subst:PAGENAME}}]]\n{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
                            elif wsite.lang == 'no':
                                safety.append('[[Kategori:Velkomstlogg|{{PAGENAME}}]]\n{| class="wikitable"')
                            else:
                                safety.append('{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
                            # The string below show how the "Usernames" will be notified
                            safety.append('\n!' + usernam)
                            # The string below show how the "Contribs" will be notified
                            safety.append('\n!' + contrib)

                        for found_result in hechas:
                            # Adding the log... (don't take care of the variable's name... i've set them in a BOFH-time ^__^)
                            luserpage = str(found_result[0])
                            luser = wikipedia.url2link(luserpage, wsite, wsite)
                            cantidad = str(found_result[1])
                            logtext = '\n{{WLE|user=' + luser + '|contribs=' + cantidad + '}}'
                            safety.append(logtext)
                        hechas = list()
                        try:
                            page.put(''.join(safety), summ2)
                        except wikipedia.EditConflict:
                            wikipedia.output(u"An edit conflict has occured. Pausing for 10 seconds before continuing.")
                            time.sleep(10)
                            page = wikipedia.Page(wsite, target)
                            try:
                                page.put(''.join(safety), summ2)
                            except wikipedia.EditConflict:
                                wikipedia.output(u"Another edit conflict... well, i skip the report for this time...")
                                continue
                # If we haven't to report, do nothing.
                elif log_variable == False:
                    pass
            # If recursive, don't exit, repeat after one hour.
            if recursive == True:
                    wikipedia.output(u"Sleeping " +  str(time_variable) + u" seconds before rerun. " + time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()))
                    time.sleep(time_variable)
            # If not recursive, break.
            elif recursive == False:
                    wikipedia.output(u"Stop!")
                    break
    finally:
        wikipedia.stopme()
