#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script to check recently uploaded files. This script checks if a file
description is present and if there is only a {{PD}} tag in the description.
It will tag a file "no source" in the former case, and request the uploader
to choose a more specific license in the latter case.

This script will have to be configured for each language. Please submit
translations as addition to the pywikipediabot framework.

Everything that needs customisation is indicated by comments.

This script understands the following command-line arguments:

    -limit          - The number of images to check (default: 80)

    -commons        - The Bot will check if an image on Commons has the same name
                    and if true it report the image.

    -duplicates     - Checking if the image has duplicates.

    -break	        - To break the bot after the first check (default: recursive)

    -time[:#]	- Time in seconds between repeat runs (default: 30)

    -wait[:#]       - Wait x second before check the images (default: 0)

    -skip[:#]	- The bot skip the first [:#] images (default: 0)

    -start[:#]	- Use allpages() as generator (it starts already form Image:[:#])

    -cat[:#]        - Use a category as generator

    -regex[:#]      - Use regex, must be used with -url or -page

    -page[:#]       - Define the name of the wikipage where are the images

    -url[:#]	- Define the url where are the images

    -untagged[:#]   - Use daniel's tool as generator ( http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php )

---- Istructions for the real-time settings  ----
* For every new block you have to add:

<------- ------->

In this way the Bot can understand where the block start to take the right parameter.

* Name= Set the name of the block
* Find= Use it to define what search in the text of the image's description,
while Findonly= search only if the exactly text that you give is in the image's description.
* Summary= That's the summary that the bot will use when it will notify the problem.
* Head= That's the incipit that the bot will use for the message.
* Text= This is the template that the bot will use when it will report the image's problem.

---- Known issues/FIXMEs: ----
* Fix the "real-time" regex and function
* Add the "catch the language" function for commons.
* Fix and reorganise the new documentation
* Add a report for the image tagged.
"""

#
# (C) Kyle/Orgullomoore, 2006-2007 (newimage.py)
# (C) Siebrand Mazeland, 2007
# (C) Filnik, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import re, time, urllib, urllib2, os, locale, sys
import wikipedia, config, pagegenerators, catlib 

locale.setlocale(locale.LC_ALL, '')

#########################################################################################################################
# <------------------------------------------- Change only below! ----------------------------------------------------->#
#########################################################################################################################

# That's what you want that will be added. (i.e. the {{no source}} with the right day/month/year )
n_txt = {
    'commons':u'\n{{subst:nld}}',
    'de'     :u'{{Benutzer:ABF/D|~~~~}} {{Dateiüberprüfung/benachrichtigt (Kategorie)|{{subst:LOCALYEAR}}|{{subst:LOCALMONTH}}|{{subst:LOCALDAY}}}} {{Dateiüberprüfung/benachrichtigt (Text)|Lizenz|||||}} --This was added by ~~~~-- ',
    'en'     :u'\n{{subst:nld}}',
    'it'     :u'\n{{subst:unverdata}}',
    'ja'     :u'{{subst:Nsd}}',
    'hu'     :u'\n{{nincslicenc|~~~~~}}',
    'ta'     :u'\n{{subst:nld}}',
    'zh'     :u'{{subst:No license/auto}}',
}
 
# Text that the bot will try to see if there's already or not. If there's a
# {{ I'll use a regex to make a better check.
# This will work so:
# '{{nld' --> '\{\{(?:template:|)no[ _]license ?(?:\||\n|\}) ?' (case insensitive).
# If there's not a {{ it will work as usual (if x in Text)
txt_find =  {
        'commons':[u'{{no license', u'{{nld', u'{{no permission since'],
        'de':[u'{{DÜP', u'{{Dateiüberprüfung'],  
        'en':[u'{{nld', u'{{no license'],
        'hu':[u'{{nincsforrás',u'{{nincslicenc'],
        'it':[u'{{unverdata', u'{{unverified'],
        'ja':[u'{{no source', u'{{unknown', u'{{non free', u'<!--削除についての議論が終了するまで',],
        'ta':[u'{{no source', u'{{nld', u'{{no license'],
        'zh':[u'{{no source', u'{{unknown', u'{{No license',],
        }
 
# Summary for when the will add the no source
comm = {
        'ar'     :u'بوت: التعليم على ملف مرفوع حديثا غير موسوم',    
        'commons':u'Bot: Marking newly uploaded untagged file',
        'de'     :u'Bot: Markierung als Bild ohne Lizenz',
        'en'     :u'Bot: Marking newly uploaded untagged file',
        'hu'     :u'Robot: Frissen feltöltött licencsablon nélküli fájl megjelölése',
        'it'     :u"Bot: Aggiungo unverified",
        'ja'     :u'ロボットによる:出典やライセンスなしの画像をタグ',
        'ta'     :u'தானியங்கி:காப்புரிமை வழங்கப்படா படிமத்தை சுட்டுதல்',
        'zh'     :u'機器人:標示新上傳且未包含必要資訊的檔案',
        }

# When the Bot find that the usertalk is empty is not pretty to put only the no source without the welcome, isn't it?
empty = {
        'commons':u'{{subst:welcome}}\n~~~~\n',
        'de'     :u'{{subst:willkommen}} ~~~~',
        'en'     :u'{{welcome}}\n~~~~\n',
        'it'     :u'<!-- inizio template di benvenuto -->\n{{subst:Benvebot}}\n~~~~\n<!-- fine template di benvenuto -->',
        'ja'     :u'{{welcome}}\n--~~~~\n',
        'hu'     :u'{{subst:Üdvözlet|~~~~}}\n',
        'zh'     :u'{{subst:welcome|sign=~~~~}}',
        }
 
# Summary that the bot use when it notify the problem with the image's license
comm2 = {
        'ar'     :u"بوت: طلب معلومات المصدر." ,    
        'commons':u"Bot: Requesting source information." ,
        'de'     :u'Bot:Notify User',
        'en'     :u"Bot: Requesting source information." ,
        'it'     :u"Bot: Notifico l'unverified",
        'ja'     :u"ロボットによる:出典とライセンス明記のお願い",
        'hu'     :u'Robot: Forrásinformáció kérése',
        'ja'     :u'{{welcome}}\n--~~~~\n',
        'hu'     :u'{{subst:Üdvözlet|~~~~}}\n',
        'ta'     :u'தானியங்கி:மூலம் வழங்கப்படா படிமத்தை சுட்டுதல்',
        'zh'     :u'{{subst:welcome|sign=~~~~}}',
        }
 
# if the file has an unknown extension it will be tagged with this template.
# In reality, there aren't unknown extension, they are only not allowed...
delete_immediately = {
            'commons':u"{{speedy|The file has .%s as extension. Is it ok? Please check.}}",
            'en'     :u"{{db-meta|The file has .%s as extension.}}",
            'it'     :u'{{cancella subito|motivo=Il file ha come estensione ".%s"}}',
            'ja'     :u'{{db|知らないファイルフォーマット%s}}',
            'hu'     :u'{{azonnali|A fájlnak .%s a kiterjesztése}}',
            'ta'     :u'{{delete|இந்தக் கோப்பு .%s என்றக் கோப்பு நீட்சியைக் கொண்டுள்ளது.}}',
            'zh'     :u'{{delete|未知檔案格式%s}}',
            }
 
# The header of the Unknown extension's message.
delete_immediately_head = {
            'commons':u"\n== Unknown extension! ==\n",
            'en'     :u"\n== Unknown extension! ==\n",
            'it'     :u'\n\n== File non specificato ==\n',
            'hu'     :u'\n== Ismeretlen kiterjesztésű fájl ==\n',
            'ta'     :u'\n== இனங்காணப்படாத கோப்பு நீட்சி! ==\n',
            'zh'     :u'\n==您上載的檔案格式可能有誤==\n',
            }
 
# Text that will be add if the bot find a unknown extension.
delete_immediately_notification = {
                'ar'     :u'الملف [[:Image:%s]] يبدو أن امتداده خاطيء, من فضلك تحقق. ~~~~',    
                'commons':u'The [[:Image:%s]] file seems to have a wrong extension, please check. ~~~~',
                'en'     :u'The [[:Image:%s]] file seems to have a wrong extension, please check. ~~~~',
                'it'     :u'{{subst:Utente:Filbot/Ext|%s}} --~~~~',
                'hu'     :u'A [[:Kép:%s]] fájlnak rossz a kiterjesztése, kérlek ellenőrízd. ~~~~',
                'ta'     :u'[[:படிமம்:%s]] இனங்காணப்படாத கோப்பு நீட்சியை கொண்டுள்ளது தயவு செய்து ஒரு முறை சரி பார்க்கவும் ~~~~',
                'zh'    :u'您好，你上傳的[[:Image:%s]]無法被識別，請檢查您的檔案，謝謝。--~~~~',
                }
# Summary of the delate immediately. (f.e: Adding {{db-meta|The file has .%s as extension.}})
del_comm = {
            'ar'     :u'بوت: إضافة %s',    
            'commons':u'Bot: Adding %s',
            'en'     :u'Bot: Adding %s',
            'it'     :u'Bot: Aggiungo %s',
            'ja'     :u'ロボットによる: 追加 %s',
            'hu'     :u'Robot:"%s" hozzáadása',
            'ta'     :u'Bot: Adding %s',
            'zh'     :u'機器人: 正在新增 %s',
            }
 
# This is the most important header, because it will be used a lot. That's the header that the bot
# will add if the image hasn't the license.
nothing_head = {
                'ar'     :u"\n== صورة بدون ترخيص ==\n",    
                'commons':u"",# Nothing, the template has already the header inside.
                'de'     :u"\n== Bild ohne Lizenz ==\n",
                'en'     :u"\n== Image without license ==\n",
                'ja'     :u'',
                'it'     :u"\n\n== Immagine senza licenza ==\n",
                'hu'     :u"\n== Licenc nélküli kép ==\n",
                'ta'     :u'',
                'zh'     :u'',
                }
# That's the text that the bot will add if it doesn't find the license.
# Note: every __botnick__ will be repleaced with your bot's nickname (feel free not to use if you don't need it)
nothing_notification = {
                'commons':u"\n{{subst:User:Filnik/untagged|Image:%s}}\n\n''This message was '''added automatically by [[User:" + \
                "__botnick__|__botnick__]]''', if you need some help about it, ask its master (~~~) or go to the [[Commons:Help desk]]''. --~~~~",
                'de'     :u'\n{{subst:Benutzer:ABF/D2|%s}} ~~~~ ',
                'en'     :u"{{subst:image source|Image:%s}} --~~~~",
                'it'     :u"{{subst:Utente:Filbot/Senza licenza|%s}} --~~~~",
                'ja'	 :u"\n{{subst:image source|Image:%s}}--~~~~",
                'hu'     :u"{{subst:adjforrást|Kép:%s}} \n Ezt az üzenetet ~~~ automatikusan helyezte el a vitalapodon, kérdéseddel fordulj a gazdájához, vagy a [[WP:KF|Kocsmafalhoz]]. --~~~~",
                'ta'     :u'\n{{subst:Di-no license-notice|படிமம்:%s}} ~~~~ ',
                'zh'     :u'\n{{subst:Uploadvionotice|Image:%s}} ~~~~ ',
                }
 
# This is a list of what bots used this script in your project.
# NOTE: YOUR Botnick is automatically added. It's not required to add it twice.
bot_list = {
            'commons':[u'Siebot', u'CommonsDelinker', u'Filbot', u'John Bot', u'Sz-iwbot', u'ABFbot'],
            'de'     :[u'ABFbot'],
            'en'     :[u'OrphanBot'],
            'it'     :[u'Filbot', u'Nikbot', u'.snoopyBot.'],
            'ja'     :[u'alexbot'],
            'ta'     :[u'TrengarasuBOT'],
            'zh'     :[u'alexbot'],
            }
 
# The message that the bot will add the second time that find another license problem.
second_message_without_license = {
                'commons':None,
                'de':None,
                'en': None,
                'it':u':{{subst:Utente:Filbot/Senza licenza2|%s}} --~~~~',
                'hu':u'\nSzia! Úgy tűnik a [[:Kép:%s]] képpel is hasonló a probléma, mint az előbbivel. Kérlek olvasd el a [[WP:KÉPLIC|feltölthető képek]]ről szóló oldalunk, és segítségért fordulj a [[WP:KF-JO|Jogi kocsmafalhoz]]. Köszönöm --~~~~',
                'ja':None,
                'ta':None,
                'zh':None,
                }
# You can add some settings to wikipedia. In this way, you can change them without touch the code.
# That's useful if you are running the bot on Toolserver.
page_with_settings = {
                    'commons':u'User:Filbot/Settings',
                    'de':None,
                    'en':None,
                    'hu':None,
                    'it':u'Progetto:Coordinamento/Immagini/Bot/Settings#Settings',
                    'ja':None,
                    'ta':None,
                    'zh':u"User:Alexbot/cisettings#Settings",
                    }
# The bot can report some images (like the images that have the same name of an image on commons)
# This is the page where the bot will store them.
report_page = {
                'commons':u'User:Filbot/Report',
                'de'     :u'Benutzer:ABFbot/Report',
                'en'     :u'User:Filnik/Report',
                'it'     :u'Progetto:Coordinamento/Immagini/Bot/Report',
                'ja'     :u'User:Alexbot/report',
                'hu'     :u'User:Bdamokos/Report',
                'ta'     :u'Trengarasu/commonsimages',
                'zh'     :u'User:Alexsh/checkimagereport',
                }
# Adding the date after the signature. 
timeselected = u' ~~~~~'
# The text added in the report
report_text = {
            'commons':u"\n*[[:Image:%s]] " + timeselected,
            'de':u"\n*[[:Bild:%s]] " + timeselected,
            'en':u"\n*[[:Image:%s]] " + timeselected,
            'it':u"\n*[[:Immagine:%s]] " + timeselected,
            'ja':u"\n*[[:Immagine:%s]] " + timeselected,
            'hu':u"\n*[[:Kép:%s]] " + timeselected,
            'ta':u"\n*[[:படிமம்:%s]] " + timeselected,
            'zh':u"\n*[[:Image:%s]] " + timeselected,
            }
# The summary of the report
comm10 = {
        'commons':u'Bot: Updating the log',
        'ar'     :u'بوت: تحديث السجل',
        'de'     :u'Bot:schreibe Log',
        'en'     :u'Bot: Updating the log',
        'it'     :u'Bot: Aggiorno il log',
        'ja'     :u'ロボットによる:更新',
        'hu'     :u'Robot: A napló frissítése',
        'ta'     :u'தானியங்கி:பட்டியலை இற்றைப்படுத்தல்',
        'zh'     :u'機器人:更新記錄',
        }
 
# If a template isn't a license but it's included on a lot of images, that can be skipped to
# analise the image without taking care of it. (the template must be in a list)
# Warning: Don't add template like "en, de, it" because they are already in (added in the code, below
# Warning 2: The bot will use regex, make the names compatible, please (don't add "Template:" or {{
# because they are already put in the regex).
HiddenTemplate = {
        'commons':[u'information', u'trademarked', u'trademark'],
        'de':[u'information'],
        'en':[u'information'],
        'it':[u'edp', u'informazioni[ _]file', u'information', u'trademark'],
        'ja':[u'Information'],
        'hu':[u'információ', u'enwiki', u'azonnali'],
        'ta':[u'information'],
        'zh':[u'information'],
        }
 
# Template added when the bot finds only an hidden template and nothing else.
# Note: every __botnick__ will be repleaced with your bot's nickname (feel free not to use if you don't need it)
HiddenTemplateNotification = {
        'commons': u"""\n{{subst:User:Filnik/whitetemplate|Image:%s}}\n\n''This message was '''added automatically by [[User:__botnick__|__botnick__]]''', if you need some help about it, ask its master (~~~) or go to the [[Commons:Help desk]]''. --~~~~""",
        'de': None,
        'en': None,
        'it': u"{{subst:Utente:Filbot/Template_insufficiente|%s}} --~~~~",
        'ta': None,
        }
# Stub - will make it better in future (no time now)
duplicatesText = {
        'commons':u'\n{{Dupe|__image__}}',
        'en':None,
        'it':u'\n{{Cancella subito|Immagine doppia di __image__}}',
        }
duplicatesRegex = {
        'commons':r'\{\{(?:[Tt]emplate:|)[Dd]upe[|}]',
        'en':None,
        'it':r'\{\{(?:[Tt]emplate:|)[Cc]ancella[ _]subito[|}]',
        }

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = [u'ar', u'commons', u'de', u'en', u'ja', u'hu', u'it', u'ta', u'zh']

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project.
#########################################################################################################################
# <------------------------------------------- Change only above! ----------------------------------------------------> #
#########################################################################################################################

# Error Classes
class LogIsFull(wikipedia.Error):
    """An exception indicating that the log is full and the Bot cannot add other data to prevent Errors."""

class NothingFound(wikipedia.Error):
    """ An exception indicating that a regex has return [] instead of results."""

class NoHash(wikipedia.Error):
    """ The APIs don't return any Hash for the image searched.
        Really Strange, better to raise an error. """

# Other common useful functions
def printWithTimeZone(message):
    """ Function to print the messages followed by the TimeZone encoded correctly. """
    if message[-1] != ' ':
        message = '%s ' % unicode(message)
    time_zone = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.localtime())
    if locale.getlocale()[1]:
        time_zone = unicode(time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()), locale.getlocale()[1])
    else:
        time_zone = unicode(time.strftime(u"%d %b %Y %H:%M:%S (UTC)", time.gmtime()))
    wikipedia.output(u"%s%s" % (message, time_zone))
                        
def pageText(url):
    """ Function used to get HTML text from every reachable URL """
    # When the page is not a wiki-page (as for untagged generator) you need that function
    try:
        request = urllib2.Request(url)
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
        request.add_header("User-Agent", user_agent)
        response = urllib2.urlopen(request)
        text = response.read()
        response.close()
        # When you load to many users, urllib2 can give this error.
    except urllib2.HTTPError:
        printWithTimeZone(u"Server error. Pausing for 10 seconds... ")
        time.sleep(10)
        request = urllib2.Request(url)
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
        request.add_header("User-Agent", user_agent)
        response = urllib2.urlopen(request)
        text = response.read()
        response.close()
    return text

# Here there is the main class.
class main:
    def __init__(self, site, logFulNumber = 25000):
        """ Constructor, define some global variable """
        self.site = site
        self.logFulNumber = logFulNumber
        self.settings = wikipedia.translate(site, page_with_settings)
        self.rep_page = wikipedia.translate(site, report_page)
        self.rep_text = wikipedia.translate(site, report_text)
        self.com = wikipedia.translate(site, comm10)
        # Commento = Summary in italian
        self.commento = wikipedia.translate(self.site, comm)
    def general(self, newtext, image, notification, head, botolist):
        """ This class can be called for two reason. So I need two different constructors, one with common data
        and another with the data that I required... maybe it can be added on the other function, but in this way
        seems more clear what parameters I need """
        self.newtext = newtext
        self.image = image
        self.head = head
        self.notification = notification
        self.botolist = botolist
    def put_mex(self, put = True):
        """ Function to add the template in the image and to find out
        who's the user that has uploaded the image. """
        # Defing the image's Page Object
        p = wikipedia.ImagePage(self.site, 'Image:%s' % self.image)
        # Get the image's description
        try:
            testoa = p.get()
        except wikipedia.NoPage:
            wikipedia.output(u'%s has been deleted...' % p.title())
            # We have a problem! Report and exit!     
            return False
        # You can use this function also to find only the user that
        # has upload the image (FixME: Rewrite a bit this part)
        if put:
            p.put(testoa + self.newtext, comment = self.commento, minorEdit = True)
        image_n = self.site.image_namespace()
        image_namespace = "%s:" % image_n # Example: "User_talk:"
        # paginetta it's the image page object.
        paginetta = wikipedia.ImagePage(self.site, image_namespace + self.image)
        # I take the data of the latest uploader and I take only the name
        imagedata = paginetta.getFileVersionHistory()
        #print imagedata # Let it so for de-buggin porpuse (wikipedia.output gives error)
        # When an Image is deleted from Commons and someone has add something in the wikipedia page
        # The bot doesn't catch the data properly :-)
        if imagedata == list():
            wikipedia.output(u"Seems that %s hasn't the image at all, but there is something in the description..." % self.image)
            repme = "\n*[[:Image:%s]] seems to have problems ('''no data found in the image''')"
            self.report_image(self.image, self.rep_page, self.com, repme)
            # We have a problem! Report and exit!         
            return False
        try:
            nick = paginetta.getFileVersionHistory()[-1][1]
        except IndexError:
            wikipedia.output(u"Seems that %s hasn't the image at all, but there is something in the description..." % self.image)
            repme = "\n*[[:Image:%s]] seems to have problems ('''no data found in the image''')"
            # We have a problem! Report and exit!
            self.report_image(self.image, self.rep_page, self.com, repme)
            return False
        luser = wikipedia.url2link(nick, self.site, self.site)
        pagina_discussione = "%s:%s" % (self.site.namespace(3), luser)
        # Defing the talk page (pagina_discussione = talk_page ^__^ )
        talk_page = wikipedia.Page(self.site, pagina_discussione)
        self.talk_page = talk_page
        return True
    def put_talk(self, notification, head, notification2 = None, commx = None):
        """ Function to put the warning in talk page of the uploader."""
        commento2 = wikipedia.translate(self.site, comm2)
        talk_page = self.talk_page
        notification = self.notification
        if notification2 == None:
            notification2 = notification
        else:
            notification2 = notification2 % self.image
        head = self.head
        second_text = False
        # Getting the talk page's history, to check if there is another advise...
        # The try block is used to prevent error if you use an old wikipedia.py's version.
        edit_to_load = 10
        if talk_page.exists():
            try:
                history = talk_page.getVersionHistory(False, False, False, edit_to_load)
            except TypeError:
                history = talk_page.getVersionHistory(False, False, False)
            latest_edit = history[0]
            latest_user = latest_edit[2]
            wikipedia.output(u'The latest user that has written something is: %s' % latest_user)
        else:
            wikipedia.output(u'The user page is blank')

        if talk_page.exists():
            try:
                testoattuale = talk_page.get() # Actual text
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'The user talk is a redirect, trying to get the right talk...')
                try:
                    talk_page = talk_page.getRedirectTarget()
                    testoattuale = talk_page.get()
                except wikipedia.NoPage:
                    second_text = False
                    ti_es_ti = wikipedia.translate(self.site, empty)
                    testoattuale = ti_es_ti                               
            project = self.site.family.name
            bot = config.usernames[project]
            botnick = bot[self.site.lang]
            botolist = self.botolist + [botnick]
            for i in botolist:
                if latest_user == i:
                    second_text = True
                    # A block to prevent the second message if the bot also welcomed users...
                    if latest_edit == history[-1]:
                        second_text = False
        else:
            second_text = False
            ti_es_ti = wikipedia.translate(self.site, empty)
            testoattuale = ti_es_ti
        if commx == None:
            commentox = commento2
        else:
            commentox = commx
        if second_text == True:
            talk_page.put("%s\n\n%s" % (testoattuale, notification2), comment = commentox, minorEdit = False)
        elif second_text == False:
            talk_page.put(testoattuale + head + notification, comment = commentox, minorEdit = False)
			
    def untaggedGenerator(self, untaggedProject, limit):
        """ Generator that yield the images without license. It's based on a tool of the toolserver. """
        lang = untaggedProject.split('.', 1)[0]
        project = '.%s' % untaggedProject.split('.', 1)[1]
        if lang == 'commons':
            link = 'http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php?wikifam=commons.wikimedia.org&since=-100d&until=&img_user_text=&order=img_timestamp&max=100&order=img_timestamp&format=html'
        else:
            link = 'http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php?wikilang=%s&wikifam=%s&order=img_timestamp&max=%s&ofs=0&max=%s' % (lang, project, limit, limit)         
        text = pageText(link)
        regexp = r"""<td valign='top' title='Name'><a href='http://.*?\.org/w/index\.php\?title=(.*?)'>.*?</a></td>"""
        results = re.findall(regexp, text)
        if results == []:
            wikipedia.output(link)
            raise NothingFound('Nothing found! Try to use the tool by yourself to be sure that it works!')
        else:
            for result in results:
                wikiPage = wikipedia.Page(self.site, result)
                yield wikiPage
	
    def regexGenerator(self, regexp, textrun):
        """ Generator used when an user use a regex parsing a page to yield the results """
        pos = 0
        done = list()
        ext_list = list()
        r = re.compile(r'%s' % regexp, re.UNICODE|re.M)
        while 1:
            m = r.search(textrun, pos)
            if m == None:
                wikipedia.output(u"\t\t>> All images checked. <<")
                break
            pos = m.end()
            image = m.group(1)
            if image not in done:
                done.append(image)
                yield image
                #continue

    def checkImageOnCommons(self, image):
        """ Checking if the image is on commons """
        self.image = image
        wikipedia.output(u'Checking if %s is on commons...' % self.image)
        commons = wikipedia.getSite('commons', 'commons')
        regexOnCommons = r"\n\*\[\[:Image:%s\]\] is also on '''Commons''': \[\[commons:Image:%s\]\]$" % (self.image, self.image)
        if wikipedia.Page(commons, u'Image:%s' % self.image).exists():
            wikipedia.output(u'%s is on commons!' % self.image)
            imagePage = wikipedia.ImagePage(self.site, 'Image:%s' % self.image)
            on_commons_text = imagePage.getImagePageHtml()
            if "<div class='sharedUploadNotice'>" in on_commons_text:
                wikipedia.output(u"But, the image doesn't exist on your project! Skip...")
                # Problems? Yes! We have to skip the check part for that image!
                # Because it's on commons but someone has added something on your project.
                return False
            elif 'stemma' in image.lower() and self.site.lang == 'it':
                wikipedia.output(u'%s has "stemma" inside, means that it\'s ok.' % image)
                return True # Problems? No, it's only not on commons but the image needs a check
            else:            
                repme = "\n*[[:Image:%s]] is also on '''Commons''': [[commons:Image:%s]]" % (self.image, self.image)
                self.report_image(self.image, self.rep_page, self.com, repme, addings = False, regex = regexOnCommons)
                # Problems? No, return True
                return True
        else:
            # Problems? No, return True
            return True

    def convert_to_url(self, page):
        # Function stolen from wikipedia.py
        """The name of the page this Page refers to, in a form suitable for the URL of the page."""
        title = page.replace(" ", "_")
        encodedTitle = title.encode(self.site.encoding())
        return urllib.quote(encodedTitle)

    def checkImageDuplicated(self, image):
        """ Function to check the duplicated images. """
        # {{Dupe|Image:Blanche_Montel.jpg}}
        # report(unvertext, imageName, notification, head)
        dupText = wikipedia.translate(self.site, duplicatesText)
        dupRegex = wikipedia.translate(self.site, duplicatesRegex)
        self.image = image
        duplicateRegex = r'\n\*(?:\[\[:Image:%s\]\] has the following duplicates:|\*\[\[:Image:%s\]\])$' % (self.convert_to_url(self.image), self.convert_to_url(self.image))
        imagePage = wikipedia.ImagePage(self.site, 'Image:%s' % self.image)
        wikipedia.output(u'Checking if %s has duplicates...' % image)
        get_hash = self.site.getUrl('/w/api.php?action=query&format=xml&titles=Image:%s&prop=imageinfo&iiprop=sha1' % self.convert_to_url(self.image))
        hash_found_list = re.findall(r'<ii sha1="(.*?)" />', get_hash)
        if hash_found_list != []:
            hash_found = hash_found_list[0]
        else:
            if imagePage.exists():
                raise NoHash('No Hash found in the APIs! Maybe the regex to catch it is wrong or someone has changed the APIs structure.')
            else:
                wikipedia.output(u'Image deleted before getting the Hash. Skipping...')
                return False # Error, we need to skip the page.
        get_duplicates = self.site.getUrl('/w/api.php?action=query&format=xml&list=allimages&aisha1=%s' % hash_found)
        duplicates = re.findall(r'<img name="(.*?)".*?/>', get_duplicates)
        if len(duplicates) > 1:
            if len(duplicates) == 2:
                wikipedia.output(u'%s has a duplicate! Reporting it...' % self.image)
            else:
                wikipedia.output(u'%s has %s duplicates! Reporting them...' % (self.image, len(duplicates) - 1))
            repme = "\n*[[:Image:%s]] has the following duplicates:" % self.convert_to_url(self.image)
            for duplicate in duplicates:
                if self.convert_to_url(duplicate) == self.convert_to_url(self.image):
                    continue # the image itself, not report also this as duplicate
                repme += "\n**[[:Image:%s]]" % self.convert_to_url(duplicate)    
            result = self.report_image(self.image, self.rep_page, self.com, repme, addings = False, regex = duplicateRegex)
            if result and not dupText == None and not dupRegex == None:
                for duplicate in duplicates:
                    if self.convert_to_url(duplicate) == self.convert_to_url(self.image):
                        continue # the image itself, not report also this as duplicate
                    DupePage = wikipedia.Page(self.site, u'Image:%s' % duplicate)
                    try:
                        DupPageText = DupePage.get()
                    except wikipedia.NoPage:
                        continue # The page doesn't exists
                    if re.findall(dupRegex, DupPageText) == []:
                        wikipedia.output(u'Adding the duplicate template in the image...')
                        report(re.sub(r'__image__', r'%s' % self.image, dupText), duplicate)                
        return True # Ok - No problem. Let's continue the checking phase
        
    def report_image(self, image, rep_page = None, com = None, rep_text = None, addings = True, regex = None):
        """ Function to report the images in the report page when needed. """
        if rep_page == None: rep_page = self.rep_page
        if com == None: com = self.com
        if rep_text == None: rep_text = self.rep_text
        another_page = wikipedia.Page(self.site, rep_page)
	if regex == None: regex = image
        if another_page.exists():
            text_get = another_page.get()
        else:
            text_get = str()
        if len(text_get) >= self.logFulNumber:
            raise LogIsFull("The log page (%s) is full! Please delete the old images reported." % another_page.title())  
        pos = 0
        # The talk page includes "_" between the two names, in this way i replace them to " "        
        n = re.compile(regex, re.UNICODE|re.M)
        y = n.search(text_get, pos)
        if y == None:
            # Adding the log
            if addings:
                rep_text = rep_text % image # Adding the name of the image in the report if not done already              
            another_page.put(text_get + rep_text, comment = com, minorEdit = False)
            wikipedia.output(u"...Reported...")
            reported = True
        else:
            pos = y.end()
            wikipedia.output(u"%s is already in the report page." % image)
            reported = False
        return reported
	
    def takesettings(self):
        """ Function to take the settings from the wiki. """
        pos = 0
        if self.settings == None: lista = None
        else:
            x = wikipedia.Page(self.site, self.settings)
            lista = list()
            try:
                testo = x.get()
                rxp = "<------- ------->\n\*[Nn]ame ?= ?['\"](.*?)['\"]\n\*([Ff]ind|[Ff]indonly)=(.*?)\n\*[Ii]magechanges=(.*?)\n\*[Ss]ummary=['\"](.*?)['\"]\n\*[Hh]ead=['\"](.*?)['\"]\n\*[Tt]ext ?= ?['\"](.*?)['\"]\n\*[Mm]ex ?= ?['\"]?(.*?)['\"]?$"
                r = re.compile(rxp, re.UNICODE|re.M)
                number = 1
                while 1:
                    m = r.search(testo, pos)
                    if m == None:
                        if lista == list():
                            wikipedia.output(u"You've set wrongly your settings, please take a look to the relative page. (run without them)")
                            lista = None
                        else:
                            break
                    else:
                        pos = m.end()
                        name = str(m.group(1))
                        find_tipe = str(m.group(2))
                        find = str(m.group(3))
                        imagechanges = str(m.group(4))
                        summary = str(m.group(5))
                        head = str(m.group(6))
                        text = str(m.group(7))
                        mexcatched = str(m.group(8))
                        tupla = [number, name, find_tipe, find, imagechanges, summary, head, text, mexcatched]
                        lista += [tupla]
                        number += 1
            except wikipedia.NoPage:
                wikipedia.output(u"The settings' page doesn't exist!")
                lista = None
        return lista
	
    def load(self, raw):
        """ Load a list of object from a string using regex. """
        list_loaded = list()
        pos = 0
        load_2 = True
        # I search with a regex how many user have not the talk page
        # and i put them in a list (i find it more easy and secure)
        while 1:
            regl = "(\"|\')(.*?)(\"|\')(, |\])"
            pl = re.compile(regl, re.UNICODE)
            xl = pl.search(raw, pos)
            if xl == None:
                if len(list_loaded) >= 1:
                    return list_loaded
                    break
                elif len(done) == 0:
                    break
            pos = xl.end()
            word = xl.group(2)
            if word not in list_loaded:
                list_loaded.append(word)  

# I've seen that the report class before (the main) was to long to be called so,
# here there is a function that has all the settings, so i can call it once ^__^
def report(newtext, image, notification = None, head = None, notification2 = None, unver = True, commx = None, bot_list = bot_list):
    # Adding the bot's nickname at the notification text if needed.
    botolist = wikipedia.translate(wikipedia.getSite(), bot_list)
    project = wikipedia.getSite().family.name
    bot = config.usernames[project]
    botnick = bot[wikipedia.getSite().lang]
    if notification != None:
        notification = re.sub('__botnick__', botnick, notification)
    if notification2 != None:
        notification2 = re.sub('__botnick__', botnick, notification2)
    # Ok, done, let's loop.
    while 1:
        run = main(site = wikipedia.getSite())
        secondrun = run.general(newtext, image, notification, head, botolist)
        if unver == True:
            try:
                resPutMex = run.put_mex()
            except wikipedia.NoPage:
                wikipedia.output(u"The page has been deleted! Skip!")
                break
            except wikipedia.EditConflict:
                wikipedia.output(u"Edit conflict! Skip!")
                break
            else:
                if resPutMex == False:
                    break
        else:
            try:
                resPutMex = run.put_mex(False)
            except wikipedia.NoPage:
                wikipedia.output(u"The page has been deleted!")
                break
            except wikipedia.EditConflict:
                wikipedia.output(u"Edit conflict! Skip!")
                break
            else:
                if resPutMex == False:
                    break
        if notification != None and head != None:
            try:
                run.put_talk(notification, head, notification2, commx)
            except wikipedia.EditConflict:
                wikipedia.output(u"Edit Conflict! Retrying...")
                try:
                    run.put_talk(notification, head, notification2, commx)
                except:
                    wikipedia.output(u"Another error... skipping the user..")
                    break
            else:
                break
        else:
            break
                        
def checkbot():
    # Command line configurable parameters
    repeat = True # Restart after having check all the images?
    limit = 80 # How many images check?
    time_sleep = 30 # How many time sleep after the check?
    skip_number = 0 # How many images to skip before checking?
    wait_number = 0 # How many time sleep before the check?
    commonsActive = False # Check if on commons there's an image with the same name?
    normal = False # Check the new images or use another generator?
    urlUsed = False # Use the url-related function instead of the new-pages generator
    regexGen = False # Use the regex generator
    untagged = False # Use the untagged generator
    skip_list = list() # Inizialize the skip list used below
    duplicatesActive = False
        
    # Here below there are the parameters.
    for arg in wikipedia.handleArgs():
        if arg.startswith('-limit'):
            if len(arg) == 7:
                limit = int(wikipedia.input(u'How many images do you want to check?'))
            else:
                limit = int(arg[7:])
        if arg.startswith('-time'):
            if len(arg) == 5:
                time_sleep = int(wikipedia.input(u'How many seconds do you want runs to be apart?'))
            else:
                time_sleep = int(arg[6:])
        elif arg == '-break':
            repeat = False
        elif arg == '-commons':
            commonsActive = True
        elif arg == '-duplicates':
            duplicatesActive = True
        elif arg.startswith('-skip'):
            if len(arg) == 5:
                skip = True
                skip_number = int(wikipedia.input(u'How many images do you want to skip?'))
            elif len(arg) > 5:
                skip = True
                skip_number = int(arg[6:])
        elif arg.startswith('-wait'):
            if len(arg) == 5:
                wait = True
                wait_number = int(wikipedia.input(u'How many time do you want to wait before checking the images?'))
            elif len(arg) > 5:
                wait = True
                wait_number = int(arg[6:])
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = str(wikipedia.input(u'From witch page do you want to start?'))
            elif len(arg) > 6:
                firstPageTitle = str(arg[7:])
            generator = wikipedia.getSite().allpages(start='Image:%s' % firstPageTitle)
            repeat = False
        elif arg.startswith('-page'):
            if len(arg) == 5:
                regexPageName = str(wikipedia.input(u'Which page do you want to use for the regex?'))
            elif len(arg) > 5:
                regexPageName = str(arg[6:])
            repeat = False
            regexGen = True
        elif arg.startswith('-url'):
            if len(arg) == 4:
                regexPageUrl = str(wikipedia.input(u'Which url do you want to use for the regex?'))
            elif len(arg) > 4:
                regexPageUrl = str(arg[5:])
            urlUsed = True
            repeat = False
            regexGen = True
        elif arg.startswith('-regex'):
            if len(arg) == 6:
                regexpToUse = str(wikipedia.input(u'Which regex do you want to use?'))
            elif len(arg) > 6:
                regexpToUse = str(arg[7:])
            generator = 'regex'
            repeat = False
        elif arg.startswith('-cat'):
            if len(arg) == 4:
                catName = str(wikipedia.input(u'In which category do I work?'))
            elif len(arg) > 4:
                catName = str(arg[5:])
            catSelected = catlib.Category(wikipedia.getSite(), 'Category:%s' % catName)
            generator = pagegenerators.CategorizedPageGenerator(catSelected)
            repeat = False
        elif arg.startswith('-ref'):
            if len(arg) == 4:
                refName = str(wikipedia.input(u'The references of what page should I parse?'))
            elif len(arg) > 4:
                refName = str(arg[5:])
            generator = pagegenerators.ReferringPageGenerator(wikipedia.Page(wikipedia.getSite(), refName))
            repeat = False
        elif arg.startswith('-untagged'):
            untagged = True    
            if len(arg) == 9:
                projectUntagged = str(wikipedia.input(u'In which project should I work?'))
            elif len(arg) > 9:
                projectUntagged = str(arg[10:])          

    # Understand if the generator it's the default or not.
    try:
        generator
    except NameError:
        normal = True
                
    # Define the site.
    site = wikipedia.getSite()
        
    # Block of text to translate the parameters set above.
    image_n = site.image_namespace()
    image_namespace = "%s:" % image_n # Example: "User_talk:"
    unvertext = wikipedia.translate(site, n_txt)
    di = wikipedia.translate(site, delete_immediately)
    dih = wikipedia.translate(site, delete_immediately_head)
    din = wikipedia.translate(site, delete_immediately_notification)
    nh = wikipedia.translate(site, nothing_head)
    nn = wikipedia.translate(site, nothing_notification)
    dels = wikipedia.translate(site, del_comm)
    smwl = wikipedia.translate(site, second_message_without_license)
    TextFind = wikipedia.translate(site, txt_find)
    hiddentemplate = wikipedia.translate(site, HiddenTemplate)
    # If there's an hidden template, change the used
    HiddenTN = wikipedia.translate(site, HiddenTemplateNotification)
    # A template as {{en is not a license! Adding also them in the whitelist template...
    for langK in wikipedia.Family('wikipedia').langs.keys():
        hiddentemplate.append('%s' % langK)
                
    # If the images to skip are 0, set the skip variable to False (the same for the wait time)
    if skip_number == 0:
        skip = False
    if wait_number == 0:
        wait = False
    # nothing = Defining an empty image description
    nothing = ['', ' ', '  ', '   ', '\n', '\n ', '\n  ', '\n\n', '\n \n', ' \n', ' \n ', ' \n \n']
    # something = Minimal requirements for an image description.
    # If this fits, no tagging will take place (if there aren't other issues)
    # MIT license is ok on italian wikipedia, let also this here
    something = ['{{', "'''MIT&nbsp;license'''"] # Don't put "}}" here, please. Useless and can give problems.
    # Unused file extensions. Does not contain PDF.
    notallowed = ("xcf", "xls", "sxw", "sxi", "sxc", "sxd")

    # A little block-statement to ensure that the bot will not start with en-parameters
    if site.lang not in project_inserted:
        wikipedia.output(u"Your project is not supported by this script. You have to edit the script and add it!")
        wikipedia.stopme()
    # Some formatting for delete immediately template
    di = '\n%s' % di
    dels = dels % di
        
    # Reading the log of the new images if another generator is not given.
    if normal == True:
        if limit == 1:
            wikipedia.output(u"Retrieving the latest file for checking...")
        else:
            wikipedia.output(u"Retrieving the latest %d files for checking..." % limit)
    # Main Loop
    while 1:
        # Defing the Main Class.
        mainClass = main(site)
        # Untagged is True? Let's take that generator
        if untagged == True:
            generator =  mainClass.untaggedGenerator(projectUntagged, limit)
            normal = False # Ensure that normal is False
        # Normal True? Take the default generator
        if normal == True:
            generator = pagegenerators.NewimagesPageGenerator(number = limit, site = site)
        # if urlUsed and regexGen, get the source for the generator
        if urlUsed == True and regexGen == True:
            textRegex = pagetext(regexPageUrl)
        # Not an url but a wiki page as "source" for the regex
        elif regexGen == True:
            pageRegex = wikipedia.Page(site, regexPageName)
            try:
                textRegex = pageRegex.get()
            except wikipedia.NoPage:
                wikipedia.output(u"%s doesn't exist!" % page.title())
                textRegex = '' # No source, so the bot will quit later.
        # If generator is the regex' one, use your own Generator using an url or page and a regex.
        if generator == 'regex' and regexGen == True:
            generator = mainClass.regexGenerator(regexpToUse, textRegex)
        # Ok, We (should) have a generator, so let's go on.
        try:
            # Take the additional settings for the Project
            tupla_written = mainClass.takesettings()
        except wikipedia.Error:
            # Error? Settings = None
            wikipedia.output(u'Problems with loading the settigs, run without them.')
            tupla_written = None
            some_problem = False
        # Ensure that if the list given is empty it will be converted to "None"
        # (but it should be already done in the takesettings() function)
        if tupla_written == []: tupla_written = None
        # Real-Time page loaded
        if tupla_written != None: wikipedia.output(u'\t   >> Loaded the real-time page... <<')
        # No settings found, No problem, continue.
        else: wikipedia.output(u'\t   >> No additional settings found! <<')
        # Not the main, but the most important loop.
        #parsed = False
        for image in generator:            
            # When you've a lot of image to skip before working use this workaround, otherwise
            # let this commented, thanks. [ decoment also parsed = False if you want to use it
            #
            #if image.title() != u'Immagine:Nytlogo379x64.gif' and not parsed:
            #    wikipedia.output(u"%s already parsed." % image.title())
            #    continue
            #else:
            #    parsed = True
            
            # If I don't inizialize the generator, wait part and skip part are useless
            if wait:
                printWithTimeZone(u'Waiting %s seconds before checking the images,' % wait_number)
                # Let's sleep...
                time.sleep(wait_number)
                # Never sleep again (we are in a loop)
                wait = False
            # If the generator returns something that is not an image, simply skip it.
            if normal == False and regexGen == False:
                if image_namespace.lower() not in image.title().lower() and \
                'image:' not in image.title().lower():
                    wikipedia.output(u'%s seems not an image, skip it...' % image.title())
                    continue
            try:
                imageName = image.title().split(image_namespace)[1] # Deleting the namespace (useless here)
            except IndexError:# Namespace image not found, that's not an image! Let's skip...
                wikipedia.output(u"%s is not an image, skipping..." % image.title())
                continue
            # Skip block
            if skip == True:
                # If the images to skip are more the images to check, make them the same number
                if skip_number > limit: skip_number = limit
                # Print a starting message only if no images has been skipped
                if skip_list == []:
                    if skip_number == 1:
                        wikipedia.output(u'Skipping the first image:\n')
                    else:
                        wikipedia.output(u'Skipping the first %s images:\n' % skip_number)
                # If we still have pages to skip:
                if len(skip_list) < skip_number:
                    wikipedia.output(u'Skipping %s...' % imageName)
                    skip_list.append(imageName)
                    if skip_number == 1:
                        wikipedia.output('')
                        skip = False 
                    continue
                else:
                    wikipedia.output('') # Print a blank line.
                    skip = False					                                               
            elif skip_list == []: # Skip must be false if we are here but
                       # the user has set 0 as images to skip
                wikipedia.output(u'\t\t>> No images to skip...<<')
                skip_list.append('skip = Off') # Only to print it once
            parentesi = False # parentesi are these in italian: { ( ) } []
            delete = False
            tagged = False
            extension = imageName.split('.')[-1] # get the extension from the image's name
            # Page => ImagePage
            p = wikipedia.ImagePage(site, image.title())
            # Get the text in the image (called g)
            try:
                g = p.get()
            except wikipedia.NoPage:
                wikipedia.output(u"Skipping %s because it has been deleted." % imageName)
                continue
            except wikipedia.IsRedirectPage:
                wikipedia.output(u"The file description for %s is a redirect?!" % imageName )
                continue
            # Check on commons if there's already an image with the same name
            if commonsActive == True:
                response = mainClass.checkImageOnCommons(imageName)
                if response == False:
                    continue
            # Check if there are duplicates of the image on the project selected
            if duplicatesActive == True:
                response2 = mainClass.checkImageDuplicated(imageName)
                if response2 == False:
                    continue      
            # Is the image already tagged? If yes, no need to double-check, skip
            for i in TextFind:
                # If there are {{ use regex, otherwise no (if there's not the {{ may not be a template
                # and the regex will be wrong)
                if '{{' in i:
                    regexP = re.compile('\{\{(?:template|)%s ?(?:\||\n|\}) ?' % i.split('{{')[1].replace(' ', '[ _]'), re.I)
                    result = regexP.findall(g)
                    if result != []:
                        tagged = True
                elif i.lower() in g:
                    tagged = True
            # Deleting the useless template from the description (before adding something
            # in the image the original text will be reloaded, don't worry).
            hiddenTemplateFound = False
            white_template_found = 0
            for l in hiddentemplate:
                if tagged == False:
                    res = re.findall(r'\{\{(?:[Tt]emplate:|)%s(?: \n|\||\n|\})' % l.lower(), g.lower())
                    if res != []:
                        white_template_found += 1
                        if l != '' and l != ' ': # Check that l is not nothing or a space
                            # Deleting! (replace the template with nothing)
                            g = re.sub(r'\{\{(?:template:|)%s' % l.lower(), r'', g.lower())
                            hiddenTemplateFound = True
            if white_template_found == 1:
                wikipedia.output(u'A white template found, skipping the template...')
            elif white_template_found == 0:
                pass # if nothing found, print nothing
            else:
                wikipedia.output(u'White templates found: %s; skipping those templates...' % white_template_found)                
            for a_word in something: # something is the array with {{, MIT License and so on.
                if a_word in g:
                    # There's a template, probably a license (or I hope so)
                    parentesi = True
            # Is the extension allowed? (is it an image or f.e. a .xls file?)
            for parl in notallowed:
                if parl.lower() in extension.lower():
                    delete = True
            some_problem = False # If it has "some_problem" it must check
                      # the additional settings.
            # if tupla_writte, use addictional settings
            if tupla_written != None:
                # In every tupla there's a setting configuration
                for tupla in tupla_written:
                    name = tupla[1]
                    find_tipe = tupla[2]
                    find = tupla[3]
                    find_list = mainClass.load(find)
                    imagechanges = tupla[4]
                    if imagechanges.lower() == 'false':
                        imagestatus = False
                    elif imagechanges.lower() == 'true':
                        imagestatus = True
                    else:
                        wikipedia.output(u"Error! Imagechanges set wrongly!")
                        tupla_written = None
                        break
                    summary = tupla[5]
                    head_2 = tupla[6]
                    text = tupla[7]
                    text = text % imageName
                    mexCatched = tupla[8]
                    wikipedia.setAction(summary)
                    for k in find_list:
                        if find_tipe.lower() == 'findonly':
                            if k.lower() == g.lower():
                                some_problem = True
                                text_used = text
                                head_used = head_2
                                imagestatus_used = imagestatus
                                name_used = name
                                summary_used = summary
                                mex_used = mexCatched                                    
                                break
                        elif find_tipe.lower() == 'find':
                            if k.lower() in g.lower():
                                some_problem = True
                                text_used = text
                                head_used = head_2
                                imagestatus_used = imagestatus
                                name_used = name
                                summary_used = summary
                                mex_used = mexCatched
                                continue
            # If the image exists (maybe it has been deleting during the oder
            # checking parts or something, who knows? ;-))
            if p.exists():
                # Here begins the check block.
                if tagged == True:
                    # Tagged? Yes, skip.
                    printWithTimeZone(u'%s is already tagged...' % imageName)
                    continue
                if some_problem == True:
                    if mex_used in g:
                        wikipedia.output(u'Image already fixed. Skip.')
                        continue
                    wikipedia.output(u"The image description for %s contains %s..." % (imageName, name_used))
                    if mex_used.lower() == 'default':
                        mex_used = unvertext
                    if imagestatus_used == False:
                        reported = mainClass.report_image(imageName)
                    else:
                        reported = True
                    if reported == True:
                        #if imagestatus_used == True:
                        report(mex_used, imageName, text_used, "\n%s\n" % head_used, None, imagestatus_used, summary_used)
                    else:
                        wikipedia.output(u"Skipping the image...")
                    some_problem = False
                    continue
                elif parentesi == True:
                    printWithTimeZone(u"%s seems ok," % imageName)
                    # It works also without this... but i want only to be sure ^^
                    parentesi = False
                    continue
                elif delete == True:
                    wikipedia.output(u"%s is not a file!" % imageName)
                    # Modify summary text
                    wikipedia.setAction(dels)
                    canctext = di % extension
                    notification = din % imageName
                    head = dih
                    report(canctext, imageName, notification, head)
                    delete = False
                    continue
                elif g in nothing:
                    wikipedia.output(u"The image description for %s does not contain a license template!" % imageName)
                    if hiddenTemplateFound and HiddenTN != None and HiddenTN != '' and HiddenTN != ' ':
                        notification = HiddenTN % imageName
                    else:
                        notification = nn % imageName
                    head = nh 
                    report(unvertext, imageName, notification, head, smwl)
                    continue
                else:
                    wikipedia.output(u"%s has only text and not the specific license..." % imageName)
                    if hiddenTemplateFound and HiddenTN != None and HiddenTN != '' and HiddenTN != ' ':
                        notification = HiddenTN % imageName
                    else:
                        notification = nn % imageName
                    head = nh
                    report(unvertext, imageName, notification, head, smwl)
                    continue
    # A little block to perform the repeat or to break.
        if repeat == True:
            printWithTimeZone(u"Waiting for %s seconds," % time_sleep)
            time.sleep(time_sleep)
        elif repeat == False:
            wikipedia.output(u"\t\t\t>> STOP! <<")
            return True # Exit
                
# Here there is the main loop. I'll take all the (name of the) images and then i'll check them.
if __name__ == "__main__":
    try:
        try:
            checkbot()
        except wikipedia.BadTitle:
            wikipedia.output(u"Wikidown or server's problem, quit")
            wikipedia.stopme()
    finally:
        wikipedia.stopme()
