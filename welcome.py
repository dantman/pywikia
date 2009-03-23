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
* Arabic Wikipedia: http://ar.wikipedia.org/wiki/ويكيبيديا:سجل_الترحيب
* Wikimedia Commons: http://commons.wikimedia.org/wiki/Commons:Welcome_log
* Dutch Wikipedia: http://nl.wikipedia.org/wiki/Wikipedia:Logboek_welkom
* Italian Wikipedia: http://it.wikipedia.org/wiki/Wikipedia:Benvenuto_log
* English Wikiquote: http://en.wikiquote.org/wiki/Wikiquote:Welcome_log
* Persian Wikipedia: http://fa.wikipedia.org/wiki/ویکی‌پدیا:سیاهه_خوشامد
* Korean Wikipedia: http://ko.wikipedia.org/wiki/위키백과:Welcome_log

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
                   (default: 1, max: 50)

    -time[:#]      Define how many seconds the bot sleeps before restart
                   (default: 3600)

    -break         Use it if you don't want that the Bot restart at the end
                   (it will break) (default: False)

    -nlog          Use this parameter if you do not want the bot to log all
                   welcomed users (default: False)

    -limit[:#]     Use this parameter to define how may users should be
                   checked (default:50)

    -offset[:TIME] Skip the latest new users (those newer than TIME)
                   to give interactive users a chance to welcome the
                   new users (default: now)
                   Timezone is the server timezone, GMT for Wikimedia
                   TIME format : yyyymmddhhmmss

    -timeoffset[:#] Skip the latest new users, accounts newer than
                    # minutes

    -numberlog[:#] The number of users to welcome before refreshing the
                   welcome log (default: 4)

    -filter        Enable the username checks for bad names (default: False)

    -ask           Use this parameter if you want to confirm each possible
                   bad username (default: False)

    -random        Use a random signature, taking the signatures from a wiki
                   page (for istruction, see below).

    -file[:#]      Use a file instead of a wikipage to take the random sign.
                   N.B. If you use this parameter, you don't need to use -random.

    -savedata      This feature saves the random signature index to allow to
                   continue to welcome with the last signature used.

    -sul           Welcome the auto-created users (default: False)

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

*<SPACE>SIGNATURE
<NEW LINE>

Example:
<pre>
* [[User:Filnik|Filnik]]
* [[User:Rock|Rock]]
</pre>

NOTE: The white space and <pre></pre> aren't required but I suggest you to
      use them.

*************************** Known issues/FIXMEs ****************************

* The regex to load the user might be slightly different from project to project.
  (in this case, write to Filnik for help...)
* Use a class to group toghether the functions used.

******************************** Badwords ***********************************

The list of Badwords of the code is opened. If you think that a word is international
and it must be blocked in all the projects feel free to add it. If also you think that
a word isn't so international, feel free to delete it.

However, there is a dinamic-wikipage to load that badwords of your project or you can
add them directly in the source code that you are using without adding or deleting.

Some words, like "Administrator" or "Dio" (God in italian) or "Jimbo" aren't badword at all
but can be used for some bad-nickname.
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
__version__ = '$Id: welcome.py,v 1.5 2007/12/7 19.23.00 filnik Exp$'
#

import wikipedia, config, string, locale, query
import time, re, cPickle, os, urllib
import codecs, sys
from datetime import timedelta

locale.setlocale(locale.LC_ALL, '')

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
    'commons': u'Project:Welcome log',
    'ar': u'Project:سجل الترحيب',
    'da': None, # no welcome log on da.wiki
    'de': None, # no welcome log on de.wiki
    'en': u'Project:Welcome log',
    'fa': u'Project:سیاهه خوشامد',
    'fr': u'Wikipedia:Prise de décision/Accueil automatique des nouveaux par un robot/log',
    'ga': u'Project:Log fáilte',
    'he': None, # no welcome log on he.wiki
    'id': None, # no welcome log on id.wiki
    'it': u'Project:Benvenuto Bot/Log',
    'ja': u'利用者:Alexbot/Welcomebotログ',
    'ka': None, # no welcome log on ka.wiki
    'nl': u'Project:Logboek welkom',
    'no': u'Project:Velkomstlogg',
    'pt': None, # no welcome log on pt.wiki
    'ru': None, # no welcome log on ru.wiki
    'sq': u'Project:Tung log',
    'sr': u'Project:Добродошлице',
    'vo': None, # no welcome log on vo.wiki
    'zh': u'User:Welcomebot/欢迎日志',
    }
#The edit summary for the welcome message (e.g. Welcome!).
summary = {
    'commons':u'Welcome!',
    'ar':u'مرحبا!',
    'da':u'Velkommen',
    'de':u'Herzlich willkommen!',
    'en':u'Welcome!',
    'fa':u'خوش آمدید!',
    'fr':u'Bienvenue sur Wikipedia !',
    'ga':u'Fáilte!',
    'he':u'ברוך הבא!',
    'id':u'Selamat datang',
    'it':u'Benvenuto!',
    'ja':u'ウィキペディア日本語版へようこそ！',
    'ka':u'კეთილი იყოს თქვენი მობრძანება!',
    'nl':u'Welkom!',
    'no':u'Velkommen!',
    'pt':u'Bem vindo!',
    'ru':u'Добро пожаловать!',
    'sq':u'Tung',
    'sr':u'Добродошли!',
    'vo':u'Benokömö!',
    'zh':u'欢迎！',
    }
# The text for the welcome message (e.g. {{welcome}}) and %s at the end
# that is your signature (the bot has a random parameter to add different
# sign, so in this way it will change according to your parameters).
netext = {
    'commons':u'{{subst:welcome}} %s',
    'ar':u'{{نسخ:مستخدم:Alnokta/ترحيب}} %s',
    'da':u'{{velkommen|%s}}',
    'de':u'{{subst:Hallo}} %s',
    'en':u'{{subst:welcome}} %s',
    'fa':u'{{جا:خوشامد}} %s',
    'fr':u'{{subst:Discussion Projet:Aide/Bienvenue}} %s',
    'ga':u'{{subst:fáilte}} %s',
    'he':u'{{ס:ברוך הבא}} %s',
    'id':u'{{sdbot|%s}}',
    'it':u'<!-- inizio template di benvenuto -->\n{{subst:Benvebot}} %s',
    'ja':u'{{subst:Welcome/intro}}\n{{subst:welcome|%s}} ',
    'ka':u'{{ახალი მომხმარებელი}}--%s',
    'nl':u'{{hola|bot|%s}}',
    'no':u'{{subst:bruker:jhs/vk}} %s',
    'pt':u'{{subst:bem vindo}} %s',
    'ru':u'{{Hello}} %s',
    'sq':u'{{subst:tung}} %s',
    'sr':u'{{Добродошлица}} %s',
    'vo':u'{{benokömö}} %s',
    'zh':u'{{subst:welcome|sign=%s}}',
    }
# The edit summary for updating the welcome log (e.g. Updating log).
summary2 = {
    'commons':u'Updating log',
    'ar':u'تحديث السجل',
    'da':u'Updating log',
    'de':u'Aktualisiere Logdatei',
    'en':u'Updating log',
    'fa':u'به روز رسانی سیاهه',
    'fr':u'Mise a jour du log',
    'ga':u'Log a thabhairt suas chun dáta',
    'it':u'Aggiorno il log',
    'ja':u'更新記録',
    'nl':u'Logboek bijwerken',
    'no':u'Oppdaterer logg',
    'ru':u'Обновление',
    'sq':u'Rifreskoj log',
    'sr':u'Освежавање записа',
    'zh':u'更新日志',
    }
# The page where the bot will report users with a possibly bad username.
report_page = {
    'commons': u'Project:Administrators\' noticeboard/User problems/Usernames to be checked',
    'ar': 'Project:إخطار الإداريين/أسماء مستخدمين للفحص',
    'da': u'Bruger:Broadbot/Report',
    'de': u'Benutzer:Filnik/Report',
    'en': u'Project:Administrator intervention against vandalism',
    'fa': u'Project:تابلوی اعلانات مدیران/گزارش ربات',
    'ga': u'Project:Log fáilte/Drochainmneacha',
    'it': u'Project:Benvenuto_Bot/Report',
    'ja': u'利用者:Alexbot/report',
    'nl': u'Project:Verzoekpagina voor moderatoren/RegBlok/Te controleren gebruikersnamen',
    'no': u'Bruker:JhsBot II/Rapport',
    'ru': u'Участник:LatitudeBot/Рапорт',
    'sq': u'User:EagleBot/Report',
    'sr': u'User:SashatoBot/Записи',
    }
# The edit summary for reporting a possibly bad username.
comment = {
    'commons':u'Adding a username that needs to be checked',
    'ar':u'إضافة اسم مستخدم يحتاج للفحص',
    'da':u'Adding a username that needs to be checked',
    'de':u'Ergänze zu überprüfenden Benutzernamen',
    'en':u'Adding a username that needs to be checked',
    'fa':u'افزودن حساب کاربری نیازمند بررسی',
    'it':u'Aggiunto utente da controllare',
    'ja':u'不適切な利用者名の報告',
    'nl':u'Te controleren gebruikersnaam toegevoegd',
    'no':u'Legger til et brukernavn som m? sjekkes',
    'ru':u'Добавлено подозрительное имя участника',
    'sq':u'Added username to be checked',
    'zh':u'回報不適當的用戶名稱',
    }
# The page where the bot reads the real-time bad words page
# (this parameter is optional).
bad_pag = {
    'commons': u'Project:Welcome log/Bad_names',
    'ar': u'Project:سجل الترحيب/أسماء سيئة',
    'en': u'Project:Welcome log/Bad_names',
    'fa': u'Project:سیاهه خوشامد/نام بد',
    'it': u'Project:Benvenuto_Bot/Lista_Badwords',
    'ja': u'Project:不適切な名前の利用者',
    'nl': u'Project:Logboek_welkom/Bad_names',
    'no': u'Bruker:JhsBot/Daarlige ord',
    'ru': u'Участник:LatitudeBot/Чёрный список',
    'sq': u'User:Eagleal/Bad_names',
    'sr': u'Додавање корисника за проверу',
    }

timeselected = u' ~~~~~' # Defining the time used after the signature

# The text for reporting a possibly bad username (e.g. *[[Talk_page:Username|Username]]).
report_text = {
    'commons':u"\n*{{user3|%s}}" + timeselected,
    'ar':u"\n*{{user13|%s}}" + timeselected,
    'da':u'\n*[[Bruger Diskussion:%s]] ' + timeselected,
    'de':u'\n*[[Benutzer Diskussion:%s]] ' + timeselected,
    'en':u'\n*{{Userlinks|%s}} ' + timeselected,
    'fa':u'\n*{{کاربر|%s}}' + timeselected,
    'fr':u'\n*{{u|%s}} ' + timeselected,
    'ga':u'\n*[[Plé úsáideora:%s]] ' + timeselected,
    'it':u"\n{{Reported|%s|",
    'ja':u"\n*{{User2|%s}}" + timeselected,
    'nl':u'\n*{{linkgebruiker%s}} ' + timeselected,
    'no':u'\n*{{bruker|%s}} ' + timeselected,
    'sq':u'\n*[[User:%s]] ' + timeselected,
    'zh':u"\n*{{User|%s}}" + timeselected
    }
# Set where you load your list of signatures that the bot will load if you use
# the random argument (this parameter is optional).
random_sign = {
    'ar': u'Project:سجل الترحيب/توقيعات',
    'da': u'Wikipedia:Velkommen/Signaturer',
    'en': u'User:Filnik/Sign',
    'fa': u'Project:سیاهه خوشامد/امضاها',
    'fr': u'Projet:Service de Parrainage Actif/Signatures',
    'it': u'Project:Benvenuto_Bot/Firme',
    'ja':u'利用者:Alexbot/Welcomebotログ/List',
    'ru': u'Участник:LatitudeBot/Sign',
    'zh': u'user:Welcomebot/欢迎日志/用户',
    }
# The page where the bot reads the real-time whitelist page.
# (this parameter is optional).
whitelist_pg = {
    'ar':u'Project:سجل الترحيب/قائمة بيضاء',
    'en':u'User:Filnik/whitelist',
    'ga':u'Project:Log fáilte/Bánliosta',
    'it':u'Project:Benvenuto_Bot/Lista_Whitewords',
    'ru':u'Участник:LatitudeBot/Белый_список',
    }

# Text after the {{welcome}} template, if you want to add something
# Default (en): nothing.
final_new_text_additions = {
    'ar':u'',
    'en':u'',
    'it':u'\n<!-- fine template di benvenuto -->',
    'zh':'<small>(via ~~~)</small>',
    }

# Ok, that's all. What is below, is the rest of code, now the code is fixed
# and it will run correctly in your project ;)
############################################################################
############################################################################
############################################################################

class FilenameNotSet(wikipedia.Error):
    """An exception indicating that a signature filename was not specifed."""

# Function stolen from wikipedia.py and modified.
def urlname(talk_page, site):
    """The name of the page this Page refers to, in a form suitable for the URL of the page."""
    title = talk_page.replace(" ", "_")
    encodedTitle = title.encode(site.encoding())
    return urllib.quote(encodedTitle)

def load_word_function(wsite, raw):
    """ This is a function used to load the badword and the whitelist."""
    regl = r"(?:\"|\')(.*?)(?:\"|\')(?:, |\))"
    page = re.compile(regl, re.UNICODE)

    list_loaded = page.findall(raw)

    if len(list_loaded) == 0:
        wikipedia.output(u'There was no input on the real-time page.')
    else:
        wikipedia.output(u'\nReal-time list loaded.')
    return list_loaded

def parselog(wsite, raw, talk, number, sul):
    """ The function to load the users (only users who have a certain number of edits) """
    someone_found = False
    autocreated = wsite.mediawiki_message('newuserlog-autocreate-entry')

    # I search with a regex how many user have not the talk page
    # and i put them in a list (i find it more easy and secure).

    # XXX: That's the regex, if there are problems, take a look here.
    reg =  u'\(<a href=\"' + re.escape(wsite.path())
    reg += u'\?title=%s(?P<user>.*?)&(?:amp;|)action=(?:edit|editredlink|edit&amp;redlink=1)\"' % re.escape(talk)
    reg += u'.*?</span> (?P<reason>.*?) *?</li>'

    p = re.compile(reg, re.UNICODE)

    for x in p.finditer(raw):
        someone_found = True
        username = x.group('user')
        #skip autocreated users (SUL)
        if autocreated in x.group('reason') and not sul:
            wikipedia.output(u'%s has been created automatically, skipping...' % username)
            continue
        userpage = wikipedia.Page(wsite, username)
        # Defing the contrib's page of the user.
        pathWiki = wsite.family.nicepath(wsite.lang)
        con = '%sSpecial:Contributions/%s' % (pathWiki, userpage.urlname())
        # Getting the contribs...
        contribs = wsite.getUrl(con)

        #FIXME: It counts the first 50 edits
        # if number > 50, it won't work
        # (not *so* useful, it should be enough).
        contribnum = contribs.count('<li class=')

        if contribnum >= number:
            wikipedia.output(u'%s has enough edits to be welcomed' % userpage.titleWithoutNamespace() )
            # The user must be welcomed, return his data.
            yield ([username, contribnum])
        elif contribnum < number:
            if contribnum == 0:
                wikipedia.output(u'%s has no contributions.' % userpage.titleWithoutNamespace() )
            else:
                wikipedia.output(u'%s has only %s contributions.' % (userpage.titleWithoutNamespace(), str(contribnum)) )
            # That user mustn't be welcomed.
            continue

    if someone_found:
        wikipedia.output(u'There is nobody to be welcomed...')
    else:
        wikipedia.output(u'\nLoaded all users...')

def report(wsite, rep_page, username, com, rep):
    """  The function to report the username to a wiki-page. """

    another_page = wikipedia.Page(wsite, rep_page)
    if another_page.exists():
        text_get = another_page.get()
    else:
        nameBot = config.usernames[wsite.family.name][wsite.lang]
        text_get = u'This is a report page for the Bad-username, please translate me. --[[User:%s|%s]]' % (nameBot, nameBot)
    pos = 0
    # The talk page includes "_" between the two names, in this way i replace them to " ".
    username = wikipedia.url2link(username, wsite, wsite)
    regex = re.escape(username)
    n = re.compile(regex, re.UNICODE)
    y = n.search(text_get, pos)
    if y == None:
        # Adding the log.
        rep_text = rep % username
        another_page.put(text_get + rep_text, comment = com, minorEdit = True)
        wikipedia.output(u'...Reported...')
    else:
        pos = y.end()
        wikipedia.output(u'%s is already in the report page.' % username)

def blocked(username):
    #action=query&list=users&ususers=Filnik&usprop=blockinfo
    """
    Function that detects if a user is currently blocked or not.
    """
  
    params = {
        'action'    :'query',
        'list'      :'users',
        'ususers'   :username,
        'usprop'    :'blockinfo',
        }

    data = query.GetData(params,
                    useAPI = True, encodeTitle = False)
    # If there's not the blockedby parameter (that means the user isn't blocked), it will return False otherwise True.
    try:
        blockedBy = data['query']['users'][0]['blockedby']
    except KeyError:
        return False # No he's not
    return True # Yes is blocked

def defineSign(wsite, signPageTitle, fileSignName = None, fileOption = False):
    """ Function to load the random signatures. """
    reg = r"^\* ?(.*?)$"
    creg = re.compile(reg, re.M)
    if not fileOption:
        signPage = wikipedia.Page(wsite, signPageTitle)
        signText = signPage.get()
    else:
        if fileSignName == None:
            wikipedia.output(u'Error! - No fileName!')
            raise FilenameNotSet("No signature filename specified.")
        try:
            f = codecs.open(wikipedia.config.datafilepath(fileSignName), 'r',
                            encoding=config.console_encoding)
        except:
            f = codecs.open(wikipedia.config.datafilepath(fileSignName), 'r',
                            encoding='utf-8')
        signText = f.read()
        f.close()

    listSign = creg.findall(signText)
    return listSign

def logmaker(wsite, welcomed_users, logg, summ2, usernam, contrib):
    """ Deduct the correct sub page name form the current date """
    safety = list()
    rightime = time.localtime(time.time())
    year = str(rightime[0])
    month = str(rightime[1])
    day = str(rightime[2])
    if len(month) == 1:
        month = u'0' + month
    if wsite.lang == 'it':
        target = logg + '/' + day + '/' + month + '/' + year
    else:
        target = logg + '/' + year + '/' + month + '/' + day
    page = wikipedia.Page(wsite, target)
    try:
        safety.append(page.get())
    except wikipedia.NoPage:
        #Add the table heading each new period. See http://commons.wikimedia.org/wiki/Commons:Welcome_log
        if wsite.lang == 'it':
            safety.append(u'[[Categoria:Benvenuto log|{{subst:PAGENAME}}]]\n{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
        elif wsite.lang == 'no':
            safety.append(u'[[Kategori:Velkomstlogg|{{PAGENAME}}]]\n{| class="wikitable"')
        else:
            safety.append(u'{|border="2" cellpadding="4" cellspacing="0" style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #bfcda5; border: 1px #b6fd2c solid; border-collapse: collapse; font-size: 95%;"')
        # The string below show how the "Usernames" will be notified.
        safety.append('\n!%s' % usernam)
        # The string below show how the "Contribs" will be notified.
        safety.append(u'\n!%s' % contrib)

    for found_result in welcomed_users:
        # Adding the log... (don't take care of the variable's name...).
        luserpage = str(found_result[0])
        luser = wikipedia.url2link(luserpage, wsite, wsite)
        edit_count = str(found_result[1])
        logtext = u'\n{{WLE|user=%s|contribs=%s}}' % (luser, edit_count)
        safety.append(logtext)
    try:
        page.put(''.join(safety), summ2)
        return True
    except wikipedia.EditConflict:
        wikipedia.output(u'An edit conflict has occured. Pausing for 10 seconds before continuing.')
        time.sleep(10)
        page = wikipedia.Page(wsite, target)
        try:
            page.put(u''.join(safety), summ2)
            return True
        except wikipedia.EditConflict:
            wikipedia.output(u'Another edit conflict... Skipping...')
            return False

def mainSettings():
    global filename
    global random
    global savedata
    """ Function to get the settings via arg and return them """
    number = 1                  # number of edits that an user required to be welcomed
    numberlog = 15              # number of users that are required to add the log :)
    limit = 50                  # number of users that the bot load to check
    offset_variable = 0         # skip users newer than that timestamp
    timeoffset_variable = 0     # skip users newer than # minutes
    recursive = True            # define if the Bot is recursive or not
    time_variable = 3600        # how much time (sec.) the bot sleeps before restart
    log_variable = True         # create the welcome log or not
    ask = False                 # should bot ask to add username to bad-username list
    sul = False                 # should bot welcome auto-created users
    filter_wp = False           # check if the username is ok or not
    sign = ' --~~~~'            # default signature
    random = False              # should signature be random or not
    savedata = False            # should save the signature index or not
    fileOption = False          # check if the user wants to use a file or the wikipage
    fileSignName = None         # File name, default: None

    # The block below is used for the parameters.
    for arg in wikipedia.handleArgs():
        if arg.startswith('-edit'):
            if len(arg) == 5:
                number = int(wikipedia.input(u'After how many edits would you like to welcome new users? (0 is allowed)'))
            else:
                number = int(arg[6:])
        elif arg.startswith('-timeoffset'):
            if len(arg) == 11:
                timeoffset_variable = int(wikipedia.input(u'Which time offset (in minutest) for new users would you like to use?'))
            else:
                timeoffset_variable = int(arg[12:])
        elif arg.startswith('-time'):
            if len(arg) == 5:
                time_variable = int(wikipedia.input(u'For how many seconds would you like to bot to sleep before checking again?'))
            else:
                time_variable = int(arg[6:])
        elif arg.startswith('-offset'):
            if len(arg) == 7:
                offset_variable = int(wikipedia.input(u'Which time offset for new users would you like to use? (yyyymmddhhmmss)'))
            else:
                offset_variable = int(arg[8:])
            if len(str(offset_variable)) != 14:
                # upon request, we might want to check for software version here
                raise ValueError("Mediawiki has changed, -offset:# is not supported anymore, but -offset:TIMESTAMP is, assuming TIMESTAMP is yyyymmddhhmmss. -timeoffset is now also supported. Please read this script source header for documentation.")
        elif arg.startswith('-file:'):
            random = True
            fileOption = True
            if len(arg) == 6:
                fileSignName = wikipedia.input(u'Where have you saved your signatures?')
            else:
                fileSignName = arg[6:]
        elif arg == '-break':
            recursive = False
        elif arg == '-nlog':
            log_variable = False
        elif arg == '-ask':
            ask = True
        elif arg == '-filter':
            filter_wp = True
        elif arg == '-savedata':
            savedata = True
        elif arg == '-random':
            random = True
        elif arg == '-sul':
            sul = True
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
    # TODO: Maybe it's better change the tuple with a dictionary..
    wsite = wikipedia.getSite()
    # Filename and pywikipedia path
    filename = wikipedia.config.datafilepath('welcome-%s-%s.data' % (wsite.family.name, wsite.lang))  # file where is stored the random signature index
    if offset_variable and timeoffset_variable:
        wikipedia.output('WARING: both -offset and -timeoffset were provided, ignoring -offset')
        offset_variable = 0
    return (None, ask, filename, fileOption, fileSignName, filter_wp, limit, log_variable, number, numberlog, offset_variable, random, recursive,
            savedata, sign, time_variable, timeoffset_variable, sul)

def main(settingsBot):
    # Taking the messages inside the function namespace.
    global netext, summary, logbook, summary2, report_page, project_inserted
    global comment, bad_pag, report_text, random_sign, whitelist_pg, final_new_text_additions

    """
                      0     1      2           3           4           5         6         7          8         9           10            11
    Returned tuple: (None, ask, filename, fileOption, fileSignName, filter_wp, limit, log_variable, number, numberlog, offset_variable, random,
    (mainSettings())   12        13      14        15
                   recursive, savedata, sign, time_variable)
    """
    # Loading the option of the mainSettings()
    ask = settingsBot[1]
    filename = settingsBot[2]
    fileOption = settingsBot[3]
    fileSignName = settingsBot[4]
    filter_wp = settingsBot[5]
    limit = settingsBot[6]
    log_variable = settingsBot[7]
    number = settingsBot[8]
    numberlog = settingsBot[9]
    offset_variable = settingsBot[10]
    random = settingsBot[11]
    recursive = settingsBot[12]
    savedata = settingsBot[13]
    sign = settingsBot[14]
    time_variable = settingsBot[15]
    timeoffset_variable = settingsBot[16]
    sul = settingsBot[17]

    # The site
    wsite = wikipedia.getSite()

    # The follow lines translate the language's parameters.
    welcomer = wikipedia.translate(wsite, netext)
    summ = wikipedia.translate(wsite, summary)
    logg = wikipedia.translate(wsite, logbook)
    summ2 = wikipedia.translate(wsite, summary2)
    rep_page = wikipedia.translate(wsite, report_page)
    com = wikipedia.translate(wsite, comment)
    bad_page = wikipedia.translate(wsite, bad_pag)
    rep_text = wikipedia.translate(wsite, report_text)
    signPageTitle = wikipedia.translate(wsite, random_sign)
    wtlpg = wikipedia.translate(wsite, whitelist_pg)
    final_additions = wikipedia.translate(wsite, final_new_text_additions)

    usernam = wsite.namespace(2)
    contrib = string.capitalize(wsite.mediawiki_message('contribslink'))
    # The talk_page's variable gives "Talk page".
    talk_page = wsite.namespace(3)
    talk = '%s:' % urlname(talk_page, wsite)

    # Some project of the same language, have different settings. (this is the place to add them).
    if wsite.family.name == "wikinews" and wsite.lang == "it":
        welcomer = u'{{subst:benvenuto|%s}}'
        sign = 'Tooby'
    elif wsite.family.name == "wiktionary" and wsite.lang == "it":
        welcomer = u'{{subst:Utente:Filnik/Benve|nome={{subst:PAGENAME}}}} %s'
    elif wsite.family.name == "wikiversity" and wsite.lang == "it":
        welcomer = u'{{subst:Benvenuto}} %s'

    welcomed_users = list()
    if savedata and os.path.exists(filename):
        f = file(filename)
        number_user = cPickle.load(f)
        yield number_user
    else:
        number_user = 0
        yield number_user

    # Here there is the main loop.
    while True:
        if filter_wp:
            # A standard list of bad username components (you can change/delate it in your project...).
            # [ I divided the list into three to make it smaller...]
            elencoaf =      [' ano', ' anus', 'anal ', 'babies', 'baldracca', 'balle', 'bastardo',
                            'bestiali', 'bestiale', 'bastarda', 'b.i.t.c.h.', 'bitch', 'boobie',
                            'bordello', 'breast', 'cacata', 'cacca', 'cachapera', 'cagata',
                            'cane', 'cazz', 'cazzo', 'cazzata', 'chiavare', 'chiavata', 'chick',
                            'christ ', 'cristo', 'clitoride', 'coione', 'cojdioonear', 'cojones',
                            'cojo', 'coglione', 'coglioni', 'cornuto', 'cula', 'culatone',
                            'culattone', 'culo', 'deficiente', 'deficente', 'dio', 'die ',
                            'died ', 'ditalino', 'ejackulate', 'enculer', 'eroticunt', 'fanculo',
                            'fellatio', 'fica ', 'ficken', 'figa', 'sfiga', 'fottere', 'fotter',
                            'fottuto', 'fuck', 'f.u.c.k.', "funkyass"]
            elencogz =      ['gay', 'hentai.com', 'horne', 'horney', 'virgin', 'hotties', 'idiot',
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
                wikipedia.output(u'\nLoading the bad words list from %s...' % wsite.hostname() )
                text_bad = badword_page.get()
                list_loaded = load_word_function(wsite,text_bad)
            else:
                wikipedia.output(u'\t\t>>>WARNING: The bad word page doesn\'t exist!<<<')
                list_loaded = list()
            # Joining the "other things" with the loaded...
            elencovarie = elenco_others + list_loaded
        else:
            elencoaf = list()
            elencogz = list()
            elencovarie = list()
        # Joining the three lists..
        elenco = elencoaf + elencogz + elencovarie
        if filter_wp:
            # That is the default whitelist (it contains few name because it has been improved in the latest days..).
            whitelist_default = ['emiliano']
            if wtlpg != None:
                whitelist_page = wikipedia.Page(wsite, wtlpg)
                if whitelist_page.exists():
                    wikipedia.output(u'\nLoading the whitelist from %s...' % wsite.hostname() )
                    text_white = whitelist_page.get()
                    list_white = load_word_function(wsite, text_white)
                else:
                    wikipedia.output(u"\t\t>>>WARNING: The whitelist's page doesn't exist!<<<")
                    list_white = list()
            else:
                wikipedia.output(u"\t\t>>>WARNING: The whitelist hasn't been setted!<<<")
                list_white = list()
        else:
            list_white = list()
            whitelist_default = list()
        # Join the whitelist words.
        whitelist = list_white + whitelist_default

        # think about non-wikimedia wikis. Use Site functions.
        URL = wsite.log_address(limit, 'newusers')
        if timeoffset_variable != 0:
            now = wsite.server_time() - timedelta(minutes=timeoffset_variable)
            offset_variable = int(now.strftime("%Y%m%d%H%M%S"))
        if offset_variable != 0:
            URL += "&offset=%d" % offset_variable
        log = wsite.getUrl(URL)
        wikipedia.output(u'Loading latest %s new users from %s...\n' % (limit, wsite.hostname()))
        # Determine which signature to use
        if random:
            try:
                wikipedia.output(u'Loading random signatures...')
                signList = defineSign(wsite, signPageTitle, fileSignName, fileOption)
            except wikipedia.NoPage:
                wikipedia.output(u'The list with signatures is not available... Using default signature...')
                random = False
        for found_result in parselog(wsite, log, talk, number, sul):
            # Compiling the signature to be used.
            if random:
                if number_user + 1 > len(signList):
                    number_user = 0
                    yield number_user
                welcom = welcomer % signList[number_user] + timeselected
                # If there's something extra to add at the end of the template, add it!
                if final_additions != '':
                    welcom += final_additions
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
                # OK, no problem
                pass
            # Check if the user has been already blocked.
            ki = blocked(username)
            if ki == True:
                wikipedia.output(u'%s has been blocked! Skipping...' % usertalkpage.titleWithoutNamespace())
                continue
            # Understand if the user has a bad-username.
            username = str(username).encode(config.console_encoding)
            lower_uname = username.lower()
            for word in elenco: # elenco = list of bad words
                if word.lower() in lower_uname:
                    baduser = True
                    # The format of the italian report template is:
                    # {{Reported|NICKNAME|BADWORD}}
                    # The nickname is already added before and
                    # here we add the "badword" part, but
                    # this function is used only in the italian wiki.
                    if wsite.lang == 'it':
                        final_rep = "%s%s}}" % (rep_text, word)
                        break
                    else:
                        final_rep = rep_text
                        break
            # Checking in the whitelist...
            for xy in whitelist:
                if xy.lower() in lower_uname:
                    # Deleting the white word found and check
                    # the word that remains for badwords inside.
                    lower_uname = lower_uname.replace(xy, '')
                    for word in elenco:
                        baduser = word.lower() in lower_uname
                        break
            # He has a badusername, trying to report him...
            if baduser:
                if ask:
                    answer = wikipedia.inputChoice(u'%s may have an unwanted username, do you want to report this user?'
                                    % usertalkpage.titleWithoutNamespace(), ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                    if answer.lower() in ['yes', 'y']:
                        if not usertalkpage.exists():
                            # Check if the user has been already blocked (second check).
                            if blocked(username):
                                wikipedia.output(u'%s has been blocked! Skipping him...' % usertalkpage.titleWithoutNamespace())
                            report(wsite, rep_page, username, com, final_rep)
                            continue
                        else:
                            wikipedia.output(u'The discussion page of the bad-user already exists...')
                            continue
                    if answer.lower() in ['no', 'n', 'nope']:
                        baduser = False
                else:
                    wikipedia.output(u'%s is possibly an unwanted username. He will be reported.' % usertalkpage.titleWithoutNamespace())
                    if not usertalkpage.exists():
                        report(wsite, rep_page, username, com, final_rep)
                        continue
                    else:
                        wikipedia.output(u'The discussion page of the bad-user already exists...')
                        continue
            # He has a good username, welcome!
            else:
                if not usertalkpage.exists():
                    # Tring to put the welcome...
                    try:
                        # make non-minor edit to trigger new talk page message.
                        usertalkpage.put(welcom, summ, minorEdit = False)
                        welcomed_users.append(found_result)
                        if random == True:
                            number_user += 1
                            yield number_user
                    except wikipedia.EditConflict:
                        wikipedia.output(u'An edit conflict has occured, skipping this user.')
                        continue
                else:
                    wikipedia.output(u'%s has been already welcomed when i was loading all the users... skipping' % usertalkpage.titleWithoutNamespace())
                    continue
            # That's the log
            if log_variable and logg:
                if len(welcomed_users) == 1:
                    wikipedia.output(u'One user has been welcomed.')
                elif len(welcomed_users) == 0:
                    wikipedia.output(u'No users have been welcomed.')
                else:
                    wikipedia.output(u'%s users have been welcomed.' % str(len(welcomed_users)) )
                if len(welcomed_users) < numberlog:
                    continue
                # Update the welcome log each fifth welcome message.
                elif len(welcomed_users) >= numberlog:
                    logresult = logmaker(wsite, welcomed_users, logg, summ2, usernam, contrib)
                    welcomed_users = list()
                    if logresult == False:
                        continue
            # If we haven't to report, do nothing.
            elif log_variable == False:
                pass
        if log_variable and logg and len(welcomed_users) != 0:
            if len(welcomed_users) == 1:
                wikipedia.output(u'Putting the log of the latest user...')
            else:
                wikipedia.output(u'Putting the log of the latest %d users...' % len(welcomed_users))
            logresult2 = logmaker(wsite, welcomed_users, logg, summ2, usernam, contrib)
            welcomed_users = list()
            if logresult2 == False:
                continue
        # If recursive, don't exit, repeat after one hour.
        if recursive :
            waitstr = unicode(time_variable)
            if locale.getlocale()[1]:
                strfstr = unicode(time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()), locale.getlocale()[1])
            else:
                strfstr = unicode(time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()))
            wikipedia.output(u'Sleeping %s seconds before rerun. %s' % (waitstr, strfstr))
            time.sleep(time_variable)
        # If not recursive, break.
        elif recursive == False:
            yield number_user
            break

if __name__ == "__main__":
    # Use try and finally, to put the wikipedia.stopme() always at the end of the code.
    try:
        #try:
        number_user = 0
        settingsBot = mainSettings()
        # Take two settings for the "finally" block.
        filename = settingsBot[2]
        random = settingsBot[11]
        savedata = settingsBot[13]
        # I need to know what is the number_user, in this way I get it.
        # If recursive, just wait some error or something to get the number
        # and save it, otherwise just save the first one.
        for number_user in main(settingsBot):
            #print number_user
            pass # number_user get with the for cicle the value
        #except wikipedia.BadTitle:
            # If the server is down, pywikipediabot raise that error.
            # Better to catch it in order not to get useless errors
            # (in particular if you're running that script on toolserver).
            # FixME: put this except in a better "place" (next to the part
            # that raises the error)
        #    wikipedia.output(u"Wikidown or server's problem. Quit.")
        #    wikipedia.stopme()
    finally:
        # If there is the savedata, the script must save the number_user.
        if random and savedata and number_user != None:
            f = file(filename, 'w')
            cPickle.dump(number_user, f)
            f.close()
        wikipedia.stopme()
