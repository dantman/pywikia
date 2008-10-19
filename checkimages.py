#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Script to check recently uploaded files. This script checks if a file
description is present and if there are other problems in the image's description.

This script will have to be configured for each language. Please submit
translations as addition to the pywikipediabot framework.

Everything that needs customisation is indicated by comments.

This script understands the following command-line arguments:

    -limit              - The number of images to check (default: 80)

    -commons            - The Bot will check if an image on Commons has the same name
                        and if true it report the image.

    -duplicates[:#]     - Checking if the image has duplicates (if arg, set how many rollback
                          wait before reporting the image in the report instead of tag the image)
                          default: 1 rollback.

    -duplicatesreport   - Report the duplicates in a log *AND* put the template in the images.

    -smartdetection     - Check in a category if the license found exist in realit or not.

    -sendemail          - Send an email after tagging.

    -break            - To break the bot after the first check (default: recursive)

    -time[:#]            - Time in seconds between repeat runs (default: 30)

    -wait[:#]           - Wait x second before check the images (default: 0)

    -skip[:#]            - The bot skip the first [:#] images (default: 0)

    -start[:#]            - Use allpages() as generator (it starts already form Image:[:#])

    -cat[:#]            - Use a category as generator

    -regex[:#]          - Use regex, must be used with -url or -page

    -page[:#]           - Define the name of the wikipage where are the images

    -url[:#]            - Define the url where are the images

    -untagged[:#]       - Use daniel's tool as generator ( http://toolserver.org/~daniel/WikiSense/UntaggedImages.php )

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
* Clean the code, some passages are pretty difficult to understand if you're not the coder.
* Fix the "real-time" regex and function
* Add the "catch the language" function for commons.
* Fix and reorganise the new documentation
* Add a report for the image tagged.
* Duplicates: check the usage, find out which image is most usued and "delete" the other ones.
* -> if the other ones are used, advise it in the message!

"""

#
# (C) Kyle/Orgullomoore, 2006-2007 (newimage.py)
# (C) Siebrand Mazeland, 2007
# (C) Filnik, 2007-2008
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import re, time, urllib, urllib2, os, locale, sys, datetime
import wikipedia, config, pagegenerators, catlib, query

locale.setlocale(locale.LC_ALL, '')

#########################################################################################################################
# <------------------------------------------- Change only below! ----------------------------------------------------->#
#########################################################################################################################

# NOTE: in the messages used by the Bot if you put __botnick__ in the text, it will automatically replaced
# with the bot's nickname.

# That's what you want that will be added. (i.e. the {{no source}} with the right day/month/year )
n_txt = {
    'commons':u'\n{{subst:nld}}',
    'ar'     :u'\n{{subst:لم}}',
    'de'     :u'{{Benutzer:ABF/D|~~~~}} {{Dateiüberprüfung/benachrichtigt (Kategorie)|{{subst:LOCALYEAR}}|{{subst:LOCALMONTH}}|{{subst:LOCALDAY}}}} {{Dateiüberprüfung/benachrichtigt (Text)|Lizenz|||||}} --This was added by ~~~~-- ',
    'en'     :u'\n{{subst:nld}}',
    'hu'     :u'\n{{nincslicenc|~~~~~}}',
    'it'     :u'\n{{subst:unverdata}}',
    'ja'     :u'{{subst:Nld}}',
    'ko'     :u'\n{{subst:nld}}',
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
        'ko':[u'{{출처 없음', u'{{라이선스 없음',u'{{Unknown',],
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
        'ja'     :u'ロボットによる:著作権情報なしの画像をタグ',
        'ko'     :u'로봇:라이선스 없음',
        'ta'     :u'தானியங்கி:காப்புரிமை வழங்கப்படா படிமத்தை சுட்டுதல்',
        'zh'     :u'機器人:標示新上傳且未包含必要資訊的檔案',
        }

# When the Bot find that the usertalk is empty is not pretty to put only the no source without the welcome, isn't it?
empty = {
        'commons':u'{{subst:welcome}}\n~~~~\n',
    	'ar'     :u'{{ترحيب}}\n~~~~\n',
        'de'     :u'{{subst:willkommen}} ~~~~',
        'en'     :u'{{welcome}}\n~~~~\n',
        'hu'     :u'{{subst:Üdvözlet|~~~~}}\n',
        'it'     :u'<!-- inizio template di benvenuto -->\n{{subst:Benvebot}}\n~~~~\n<!-- fine template di benvenuto -->',
        'ja'     :u'{{subst:Welcome/intro}}\n{{subst:welcome|--~~~~}}\n',
        'ko'     :u'{{환영}}\n~~~~\n',
        'ta'     :u'{{welcome}}\n~~~~\n',
        'zh'     :u'{{subst:welcome|sign=~~~~}}',
        }

# Summary that the bot use when it notify the problem with the image's license
comm2 = {
        'ar'     :u"بوت: طلب معلومات المصدر." ,
        'commons':u"Bot: Requesting source information." ,
        'de'     :u'Bot:Notify User',
        'en'     :u"Bot: Requesting source information." ,
        'it'     :u"Bot: Notifico l'unverified",
        'hu'     :u'Robot: Forrásinformáció kérése',
        'ja'     :u"ロボットによる:著作権情報明記のお願い",
        'ko'     :u'로봇:라이선스 정보 요청',
        'ta'     :u'தானியங்கி:மூலம் வழங்கப்படா படிமத்தை சுட்டுதல்',
        'zh'     :u'機器人：告知用戶',
        }

# if the file has an unknown extension it will be tagged with this template.
# In reality, there aren't unknown extension, they are only not allowed...
delete_immediately = {
            'commons':u"{{speedy|The file has .%s as extension. Is it ok? Please check.}}",
    		'ar'     :u"{{شطب|الملف له .%s كامتداد.}}",
            'en'     :u"{{db-meta|The file has .%s as extension.}}",
            'hu'     :u'{{azonnali|A fájlnak .%s a kiterjesztése}}',
            'it'     :u'{{cancella subito|motivo=Il file ha come estensione ".%s"}}',
            'ja'     :u'{{db|知らないファイルフォーマット %s}}',
            'ko'     :u'{{delete|잘못된 파일 형식 (.%s)}}',
            'ta'     :u'{{delete|இந்தக் கோப்பு .%s என்றக் கோப்பு நீட்சியைக் கொண்டுள்ளது.}}',
            'zh'     :u'{{delete|未知檔案格式%s}}',
            }

# The header of the Unknown extension's message.
delete_immediately_head = {
            'commons':u"\n== Unknown extension! ==\n",
    		'ar'     :u"\n== امتداد غير معروف! ==\n",
            'en'     :u"\n== Unknown extension! ==\n",
            'hu'     :u'\n== Ismeretlen kiterjesztésű fájl ==\n',
            'it'     :u'\n\n== File non specificato ==\n',
            'ko'     :u'\n== 잘못된 파일 형식 ==\n',
            'ta'     :u'\n== இனங்காணப்படாத கோப்பு நீட்சி! ==\n',
            'zh'     :u'\n==您上載的檔案格式可能有誤==\n',
            }

# Text that will be add if the bot find a unknown extension.
delete_immediately_notification = {
                'ar'     :u'الملف [[:Image:%s]] يبدو أن امتداده خاطيء, من فضلك تحقق. ~~~~',
                'commons':u'The [[:Image:%s]] file seems to have a wrong extension, please check. ~~~~',
                'en'     :u'The [[:Image:%s]] file seems to have a wrong extension, please check. ~~~~',
                'hu'     :u'A [[:Kép:%s]] fájlnak rossz a kiterjesztése, kérlek ellenőrízd. ~~~~',
                'it'     :u'{{subst:Progetto:Coordinamento/Immagini/Bot/Messaggi/Ext|%s|__botnick__}} --~~~~',
                'ko'     :u'[[:그림:%s]]의 파일 형식이 잘못되었습니다. 확인 바랍니다.--~~~~',
                'ta'     :u'[[:படிமம்:%s]] இனங்காணப்படாத கோப்பு நீட்சியை கொண்டுள்ளது தயவு செய்து ஒரு முறை சரி பார்க்கவும் ~~~~',
                'zh'    :u'您好，你上傳的[[:Image:%s]]無法被識別，請檢查您的檔案，謝謝。--~~~~',
                }
# Summary of the delate immediately. (f.e: Adding {{db-meta|The file has .%s as extension.}})
del_comm = {
            'ar'     :u'بوت: إضافة %s',
            'commons':u'Bot: Adding %s',
            'en'     :u'Bot: Adding %s',
            'hu'     :u'Robot:"%s" hozzáadása',
            'it'     :u'Bot: Aggiungo %s',
            'ja'     :u'ロボットによる: 追加 %s',
            'ko'     :u'로봇 : %s 추가',
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
                'hu'     :u"\n== Licenc nélküli kép ==\n",
                'it'     :u"\n\n== Immagine senza licenza ==\n",
                'ja'     :u'',
                'ko'     :u'',
                'ta'     :u'',
                'zh'     :u'',
                }
# That's the text that the bot will add if it doesn't find the license.
# Note: every __botnick__ will be repleaced with your bot's nickname (feel free not to use if you don't need it)
nothing_notification = {
                'commons':u"\n{{subst:User:Filnik/untagged|Image:%s}}\n\n''This message was '''added automatically by [[User:" + \
                "__botnick__|__botnick__]]''', if you need some help about it, ask its master (~~~) or go to the [[Commons:Help desk]]''. --~~~~",
    			'ar'     :u"{{subst:مصدر الصورة|Image:%s}} --~~~~",
                'de'     :u'\n{{subst:Benutzer:ABF/D2|%s}} ~~~~ ',
                'en'     :u"{{subst:image source|Image:%s}} --~~~~",
                'hu'     :u"{{subst:adjforrást|Kép:%s}} \n Ezt az üzenetet ~~~ automatikusan helyezte el a vitalapodon, kérdéseddel fordulj a gazdájához, vagy a [[WP:KF|Kocsmafalhoz]]. --~~~~",
                'it'     :u"{{subst:Progetto:Coordinamento/Immagini/Bot/Messaggi/Senza licenza|%s|__botnick__}} --~~~~",
                'ja'     :u"\n{{subst:Image copyright|Image:%s}}--~~~~",
                'ko'     :u'\n{{subst:사용자:김우진1/BotRFL|%s}} --~~~~',
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
            'ko'     :[u'Kwjbot IV'],
            'ta'     :[u'TrengarasuBOT'],
            'zh'     :[u'alexbot'],
            }

# The message that the bot will add the second time that find another license problem.
second_message_without_license = {
                'commons':None,
                'de':None,
                'en': None,
                'hu':u'\nSzia! Úgy tűnik a [[:Kép:%s]] képpel is hasonló a probléma, mint az előbbivel. Kérlek olvasd el a [[WP:KÉPLIC|feltölthető képek]]ről szóló oldalunk, és segítségért fordulj a [[WP:KF-JO|Jogi kocsmafalhoz]]. Köszönöm --~~~~',
                'it':u':{{subst:Progetto:Coordinamento/Immagini/Bot/Messaggi/Senza licenza2|%s|__botnick__}} --~~~~',
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
                'hu'     :u'User:Bdamokos/Report',
                'it'     :u'Progetto:Coordinamento/Immagini/Bot/Report',
                'ja'     :u'User:Alexbot/report',
                'ko'     :u'User:Kwjbot IV/Report',
                'ta'     :u'User:Trengarasu/commonsimages',
                'zh'     :u'User:Alexsh/checkimagereport',
                }
# Adding the date after the signature.
timeselected = u' ~~~~~'
# The text added in the report
report_text = {
            'commons':u"\n*[[:Image:%s]] " + timeselected,
    		'ar':u"\n*[[:صورة:%s]] " + timeselected,
            'de':u"\n*[[:Bild:%s]] " + timeselected,
            'en':u"\n*[[:Image:%s]] " + timeselected,
            'hu':u"\n*[[:Kép:%s]] " + timeselected,
            'it':u"\n*[[:Immagine:%s]] " + timeselected,
            'ja':u"\n*[[:Immagine:%s]] " + timeselected,
            'ko':u"\n*[[:그림:%s]] " + timeselected,
            'ta':u"\n*[[:படிமம்:%s]] " + timeselected,
            'zh':u"\n*[[:Image:%s]] " + timeselected,
            }
# The summary of the report
comm10 = {
        'commons':u'Bot: Updating the log',
        'ar'     :u'بوت: تحديث السجل',
        'de'     :u'Bot:schreibe Log',
        'en'     :u'Bot: Updating the log',
        'hu'     :u'Robot: A napló frissítése',
        'it'     :u'Bot: Aggiorno il log',
        'ja'     :u'ロボットによる:更新',
        'ko'     :u'로봇:로그 업데이트',
        'ta'     :u'தானியங்கி:பட்டியலை இற்றைப்படுத்தல்',
        'zh'     :u'機器人:更新記錄',
        }

# If a template isn't a license but it's included on a lot of images, that can be skipped to
# analise the image without taking care of it. (the template must be in a list)
# Warning: Don't add template like "en, de, it" because they are already in (added in the code, below
# Warning 2: The bot will use regex, make the names compatible, please (don't add "Template:" or {{
# because they are already put in the regex).
# Warning 3: the part that use this regex is case-insensitive (just to let you know..)
HiddenTemplate = {
        'commons':[u'information'], # Put the other in the page on the project defined below
    	'ar':[u'معلومات'],
        'de':[u'information'],
        'en':[u'information'],
        'hu':[u'információ', u'enwiki', u'azonnali'],
        'it':[u'edp', u'informazioni[ _]file', u'information', u'trademark', u'permissionotrs'], # Put the other in the page on the project defined below
        'ja':[u'Information'],
        'ko':[u'그림 정보'],
        'ta':[u'information'],
        'zh':[u'information'],
        }
# A page where there's a list of template to skip.
PageWithHiddenTemplates = {
    'commons': u'User:Filbot/White_templates#White_templates',
    'en':None,
    'it':u'Progetto:Coordinamento/Immagini/Bot/WhiteTemplates',
    'ko': u'User:Kwjbot_IV/whitetemplates/list',
    }

# A page where there's a list of template to consider as licenses.
PageWithAllowedTemplates = {
    'commons': u'User:Filbot/Allowed templates',
    'en':None,
    'it':u'Progetto:Coordinamento/Immagini/Bot/AllowedTemplates',
    'ko': u'User:Kwjbot_IV/whitetemplates/list',
    }

# Template added when the bot finds only an hidden template and nothing else.
# Note: every __botnick__ will be repleaced with your bot's nickname (feel free not to use if you don't need it)
HiddenTemplateNotification = {
        'commons': u"""\n{{subst:User:Filnik/whitetemplate|Image:%s}}\n\n''This message was '''added automatically by [[User:__botnick__|__botnick__]]''', if you need some help about it, ask its master (~~~) or go to the [[Commons:Help desk]]''. --~~~~""",
        'de'     : None,
        'en'     : None,
        'it'     : u"{{subst:Progetto:Coordinamento/Immagini/Bot/Messaggi/Template_insufficiente|%s|__botnick__}} --~~~~",
        'ko'     : u"\n{{subst:User:김우진1/BotRFL|%s}} --~~~~",
        'ta'     : None,
        }

# In this part there are the parameters for the dupe images.

# Put here the template that you want to put in the image to warn that it's a dupe
# put __image__ if you want only one image, __images__ if you want the whole list
duplicatesText = {
        'commons': u'\n{{Dupe|__image__}}',
        'en'     : None,
        'it'     : u'\n{{Progetto:Coordinamento/Immagini/Bot/Template duplicati|__images__}}',
        'ko'     :'분류:그림 저작권 틀',
        }
# Head of the message given to the author
duplicate_user_talk_head = {
        'commons': None,
        'en'     : None, 
        'it'     : u'\n\n== Immagine doppia ==\n',
        }
# Message to put in the talk
duplicates_user_talk_text = {
        'commons': u'{{subst:User:Filnik/duplicates|Image:%s|Image:%s}}',
        'en'     : None,
        'it'     : u"{{subst:Progetto:Coordinamento/Immagini/Bot/Messaggi/Duplicati|%s|%s|__botnick__}} --~~~~",
        }
# Comment used by the bot while it reports the problem in the uploader's talk
duplicates_comment_talk = {
        'commons': u'Bot: Dupe image found',
        'en'     : None,
        'it'     : u"Bot: Notifico l'immagine doppia trovata",
        }
# Comment used by the bot while it reports the problem in the image
duplicates_comment_image = {
        'commons': u'Bot: Tagging dupe image',
        'en'     : None,
        'it'     : u'Bot: Immagine doppia, da cancellare',
        }
# Regex to detect the template put in the image's decription to find the dupe
duplicatesRegex = {
        'commons': r'\{\{(?:[Tt]emplate:|)[Dd]upe[|}]',
        'en'     : None,
        'it'     : r'\{\{(?:[Tt]emplate:|)[Pp]rogetto:[Cc]oordinamento/Immagini/Bot/Template duplicati[|}]',
        }
# Category with the licenses and / or with subcategories with the other licenses.
category_with_licenses = {
        'commons': 'Category:License tags',
        'en'     : None,
        'it'     : 'Categoria:Template Licenze copyright',
        }

## Put None if you don't use this option or simply add nothing if en
## is still None.
# Page where is stored the message to send as email to the users
emailPageWithText = {
        'de':'Benutzer:ABF/D3',
        'en':None,
        }
# Title of the email
emailSubject = {
        'de':'Problemen mit Deinem Bild auf der Deutschen Wikipedia',
        'en':None,
        }

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = [u'ar', u'commons', u'de', u'en', u'hu', u'it', u'ja', u'ko', u'ta', u'zh']

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project.
#########################################################################################################################
# <------------------------------------------- Change only above! ----------------------------------------------------> #
#########################################################################################################################

# Error Classes
class LogIsFull(wikipedia.Error):
    """An exception indicating that the log is full and the Bot cannot add other data to prevent Errors."""

class NothingFound(wikipedia.Error):
    """ An exception indicating that a regex has return [] instead of results."""

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

class EmailSender(wikipedia.Page):
    """ Class to send emails through the Wikipedia's dedicated page. """
    def __init__(self, site, user):
        self.wikisite = site
        self.user = user
        page_special_name = u'Special:EmailUser'
        self.page_special_name = page_special_name
        # Special:EmailUser/Filnik
        page = '%s/%s' % (self.page_special_name, self.user)
        self.page = page
        wikipedia.Page.__init__(self, site, page, None, 0)

    def send(self, subject, text, prompt = True):
        """ Send an email through wikipedia's page. """
        host = self.site().hostname()
        address = '/w/index.php?title=%s&target=%s&action=submit' % (self.page_special_name, self.user)
        # Getting the token.
        token = self.site().getToken(self)
        # Defing the predata.
        predata = {
            "wpSubject" : subject,
            "wpText" : text,
            'wpSend' : "Send",
            'wpCCMe' : '0',
        }
        predata['wpEditToken'] = token
        if self.site().hostname() in config.authenticate.keys():
            predata['Content-type'] = 'application/x-www-form-urlencoded'
            predata['User-agent'] = wikipedia.useragent
            data = self.site().urlEncode(predata)
            response = urllib2.urlopen(urllib2.Request('http://' + self.site().hostname() + address, data))
            data = u''
        else:
            response, data = self.site().postForm(address, predata, sysop = False)
        if data:
            if 'var wgAction = "success";' in data:
                wikipedia.output(u'Email sent')
                return True
            else:
                wikipedia.output(u'Email not sent')
                return False
        else:
            wikipedia.output(u'No data found.')
            return False

# Here there is the main class.
class main:
    def __init__(self, site, logFulNumber = 25000, sendemailActive = False,
                 duplicatesReport = False, smartdetection = False):
        """ Constructor, define some global variable """
        self.site = site
        self.logFulNumber = logFulNumber
        self.settings = wikipedia.translate(self.site, page_with_settings)
        self.rep_page = wikipedia.translate(self.site, report_page)
        self.rep_text = wikipedia.translate(self.site, report_text)
        self.com = wikipedia.translate(self.site, comm10)
        self.hiddentemplate = wikipedia.translate(self.site, HiddenTemplate)
        self.pageHidden = wikipedia.translate(self.site, PageWithHiddenTemplates)
        self.pageAllowed = wikipedia.translate(self.site, PageWithAllowedTemplates)        
        # Commento = Summary in italian
        self.commento = wikipedia.translate(self.site, comm)
        # Adding the bot's nickname at the notification text if needed.
        botolist = wikipedia.translate(self.site, bot_list)
        project = wikipedia.getSite().family.name
        self.project = project
        bot = config.usernames[project]
        botnick = bot[self.site.lang]
        self.botnick = botnick
        botolist.append(botnick)
        self.botolist = botolist
        self.sendemailActive = sendemailActive
        self.skip_list = list() # Inizialize the skip list used below
        self.duplicatesReport = duplicatesReport
        image_n = self.site.image_namespace()
        self.image_namespace = u"%s:" % image_n # Example: "Image:"
        # Load the licenses only once, so do it once
        self.smartdetection = smartdetection
        if self.smartdetection:
            self.list_licenses = self.load_licenses()
    def setParameters(self, imageName, timestamp, uploader):
        """ Function to set parameters, now only image but maybe it can be used for others in "future" """
        self.imageName = imageName
        # Defing the image's Page Object
        self.image = wikipedia.ImagePage(self.site, u'%s%s' % (self.image_namespace, self.imageName))
        self.timestamp = timestamp
        self.uploader = uploader
    def report(self, newtext, image_to_report, notification = None, head = None,
               notification2 = None, unver = True, commTalk = None, commImage = None):
        """ Function to make the reports easier. """
        # Defining some useful variable for next...
        self.image_to_report = image_to_report
        self.newtext = newtext
        self.head = head
        self.notification = notification
        self.notification2 = notification2
        if self.notification != None:
            self.notification = re.sub(r'__botnick__', self.botnick, notification)
        if self.notification2 != None:
            self.notification2 = re.sub(r'__botnick__', self.botnick, notification2)
        self.commTalk = commTalk
        if commImage == None:
            self.commImage = self.commento
        else:
            self.commImage = commImage
        # Ok, done, let's loop.
        while 1:
            if unver == True:
                try:
                    resPutMex = self.tag_image()
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
                    resPutMex = self.tag_image(False)
                except wikipedia.NoPage:
                    wikipedia.output(u"The page has been deleted!")
                    break
                except wikipedia.EditConflict:
                    wikipedia.output(u"Edit conflict! Skip!")
                    break
                else:
                    if resPutMex == False:
                        break
            if self.notification != None and self.head != None:
                try:
                    self.put_mex_in_talk()
                except wikipedia.EditConflict:
                    wikipedia.output(u"Edit Conflict! Retrying...")
                    try:
                        self.put_mex_in_talk()
                    except:
                        wikipedia.output(u"Another error... skipping the user..")
                        break
                else:
                    break
            else:
                break

    def tag_image(self, put = True):
        """ Function to add the template in the image and to find out
        who's the user that has uploaded the image. """
        # Get the image's description
        reportPageObject = wikipedia.ImagePage(self.site, self.image_namespace + self.image_to_report)
        try:
            reportPageText = reportPageObject.get()
        except wikipedia.NoPage:
            wikipedia.output(u'%s has been deleted...' % self.imageName)
            # We have a problem! Report and exit!
            return False
        # You can use this function also to find only the user that
        # has upload the image (FixME: Rewrite a bit this part)
        if put:
            reportPageObject.put(reportPageText + self.newtext, comment = self.commImage, minorEdit = True)
        # paginetta it's the image page object.        
        try:
            if reportPageObject == self.image and self.uploader != None:
                nick = self.uploader
            else:
                nick = reportPageObject.getLatestUploader()[0]
        except wikipedia.NoPage:
            wikipedia.output(u"Seems that %s hasn't the image at all, but there is something in the description..." % self.image_to_report)
            repme = u"\n*[[:Image:%s]] problems '''with the APIs'''"
            # We have a problem! Report and exit!
            self.report_image(self.image_to_report, self.rep_page, self.com, repme)
            return False
        luser = wikipedia.url2link(nick, self.site, self.site)
        talk_page = wikipedia.Page(self.site, u"%s:%s" % (self.site.namespace(3), luser))
        self.talk_page = talk_page
        self.luser = luser
        return True
    def put_mex_in_talk(self):
        """ Function to put the warning in talk page of the uploader."""
        commento2 = wikipedia.translate(self.site, comm2)
        emailPageName = wikipedia.translate(self.site, emailPageWithText)
        emailSubj = wikipedia.translate(self.site, emailSubject)
        if self.notification2 == None:
            self.notification2 = self.notification
        else:
            self.notification2 = self.notification2 % self.image_to_report
        second_text = False
        # Getting the talk page's history, to check if there is another advise...
        # The try block is used to prevent error if you use an old wikipedia.py's version.
        edit_to_load = 10
        try:
            testoattuale = self.talk_page.get()
            try:
                history = self.talk_page.getVersionHistory(False, False, False, edit_to_load)
            except TypeError:
                history = self.talk_page.getVersionHistory(False, False, False)
            latest_edit = history[0]
            latest_user = latest_edit[2]
            wikipedia.output(u'The latest user that has written something is: %s' % latest_user)
            for i in self.botolist:
                if latest_user == i:
                    second_text = True
                    # A block to prevent the second message if the bot also welcomed users...
                    if latest_edit == history[-1]:
                        second_text = False
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'The user talk is a redirect, trying to get the right talk...')
            try:
                self.talk_page = self.talk_page.getRedirectTarget()
                testoattuale = self.talk_page.get()
            except wikipedia.NoPage:
                second_text = False
                ti_es_ti = wikipedia.translate(self.site, empty)
                testoattuale = ti_es_ti                        
        except wikipedia.NoPage:
            wikipedia.output(u'The user page is blank')
            second_text = False
            ti_es_ti = wikipedia.translate(self.site, empty)
            testoattuale = ti_es_ti
        if self.commTalk == None:
            commentox = commento2
        else:
            commentox = self.commTalk
        if second_text == True:
            self.talk_page.put(u"%s\n\n%s" % (testoattuale, self.notification2), comment = commentox, minorEdit = False)
        elif second_text == False:
            self.talk_page.put(testoattuale + self.head + self.notification, comment = commentox, minorEdit = False)
        if emailPageName != None and emailSubj != None:
            emailPage = wikipedia.Page(self.site, emailPageName)
            try:
                emailText = emailPage.get()
            except (wikipedia.NoPage, wikipedia.IsRedirectPage):
                return # Exit
            if self.sendemailActive:
                text_to_send = re.sub(r'__user-nickname__', r'%s' % self.luser, emailText)
                emailClass = EmailSender(self.site, self.luser)
                emailClass.send(emailSubj, text_to_send)

    def untaggedGenerator(self, untaggedProject, limit):
        """ Generator that yield the images without license. It's based on a tool of the toolserver. """
        lang = untaggedProject.split('.', 1)[0]
        project = '.%s' % untaggedProject.split('.', 1)[1]
        if lang == 'commons':
            link = 'http://toolserver.org/~daniel/WikiSense/UntaggedImages.php?wikifam=commons.wikimedia.org&since=-100d&until=&img_user_text=&order=img_timestamp&max=100&order=img_timestamp&format=html'
        else:
            link = 'http://toolserver.org/~daniel/WikiSense/UntaggedImages.php?wikilang=%s&wikifam=%s&order=img_timestamp&max=%s&ofs=0&max=%s' % (lang, project, limit, limit)
        text = self.site.getUrl(link, no_hostname = True)
        regexp = r"""<td valign='top' title='Name'><a href='http://.*?\.org/w/index\.php\?title=(.*?)'>.*?</a></td>"""
        results = re.findall(regexp, text)
        if results == []:
            wikipedia.output(link)
            raise NothingFound(u'Nothing found! Try to use the tool by yourself to be sure that it works!')
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

    def loadHiddenTemplates(self):
        """ Function to load the white templates """
        # A template as {{en is not a license! Adding also them in the whitelist template...
        for langK in wikipedia.Family(u'wikipedia').langs.keys():
            self.hiddentemplate.append(u'%s' % langK)
        # The template #if: and #switch: aren't something to care about
        self.hiddentemplate.extend([u'#if:', u'#switch:'])
        # Hidden template loading
        if self.pageHidden != None:
            try:
                pageHiddenText = wikipedia.Page(self.site, self.pageHidden).get()
            except (wikipedia.NoPage, wikipedia.IsRedirectPage):
                pageHiddenText = ''
            self.hiddentemplate.extend(self.load(pageHiddenText))
        return self.hiddentemplate

    def returnOlderTime(self, listGiven, timeListGiven):
        """ Get some time and return the oldest of them """
        # print listGiven; print timeListGiven
        # -- Output: --
        # [[1210596312.0, u'Autoritratto.png'], [1210590240.0, u'Duplicato.png'], [1210592052.0, u'Duplicato_2.png']]
        # [1210596312.0, 1210590240.0, 1210592052.0]
        usage = False
        num = 0
        num_older = None
        max_usage = 0
        for element in listGiven:
            imageName = element[1]
            imagePage = wikipedia.ImagePage(self.site, u'Image:%s' % imageName)
            imageUsage = [page for page in imagePage.usingPages()]
            if len(imageUsage) > 0 and len(imageUsage) > max_usage:
                max_usage = len(imageUsage)
                num_older = num
            num += 1
        if num_older != None:
            return listGiven[num_older][1]
        for element in listGiven:
            time = element[0]
            imageName = element[1]
            not_the_oldest = False
            for time_selected in timeListGiven:
                if time > time_selected:
                    not_the_oldest = True
                    break
            if not_the_oldest == False:
                return imageName

    def convert_to_url(self, page):
        # Function stolen from wikipedia.py
        """The name of the page this Page refers to, in a form suitable for the URL of the page."""
        title = page.replace(u" ", u"_")
        encodedTitle = title.encode(self.site.encoding())
        return urllib.quote(encodedTitle)

    def countEdits(self, pagename, userlist):
        """ Function to count the edit of a user or a list of users in a page. """
        # self.botolist
        if type(userlist) == type(''):
            userlist = [userlist]
        page = wikipedia.Page(self.site, pagename)
        history = page.getVersionHistory()
        user_list = list()
        for data in history:
            user_list.append(data[2])
        number_edits = 0
        for username in userlist:
            number_edits += user_list.count(username)
        return number_edits

    def checkImageOnCommons(self):
        """ Checking if the image is on commons """
        wikipedia.output(u'Checking if %s is on commons...' % self.imageName)
        commons_site = wikipedia.getSite('commons', 'commons')
        regexOnCommons = r"\n\*\[\[:Image:%s\]\] is also on '''Commons''': \[\[commons:Image:.*?\]\](?: \(same name\)|)$" % self.imageName
        imagePage = wikipedia.ImagePage(self.site, u'Image:%s' % self.imageName)
        hash_found = imagePage.getHash()
        if hash_found == None:
            return False # Problems? Yes! Image deleted, no hash found. Skip the image.
        else:
            commons_image_with_this_hash = commons_site.getImagesFromAnHash(hash_found)
            if commons_image_with_this_hash != []:
                wikipedia.output(u'%s is on commons!' % self.imageName)
                imagePage = wikipedia.ImagePage(self.site, u'Image:%s' % self.imageName)
                on_commons_text = imagePage.getImagePageHtml()
                if u"<div class='sharedUploadNotice'>" in on_commons_text:
                    wikipedia.output(u"But, the image doesn't exist on your project! Skip...")
                    # Problems? Yes! We have to skip the check part for that image!
                    # Because it's on commons but someone has added something on your project.
                    return False
                elif re.findall(r'\bstemma\b', self.imageName.lower()) != [] and self.site.lang == 'it':
                    wikipedia.output(u'%s has "stemma" inside, means that it\'s ok.' % self.imageName)
                    return True # Problems? No, it's only not on commons but the image needs a check
                else:
                    # the second usually is a url or something like that. Compare the two in equal way, both url.
                    if self.convert_to_url(self.imageName) == self.convert_to_url(commons_image_with_this_hash[0]):
                        repme = u"\n*[[:Image:%s]] is also on '''Commons''': [[commons:Image:%s]] (same name)" % (self.imageName, commons_image_with_this_hash[0])
                    else:
                        repme = u"\n*[[:Image:%s]] is also on '''Commons''': [[commons:Image:%s]]" % (self.imageName, commons_image_with_this_hash[0])
                    self.report_image(self.imageName, self.rep_page, self.com, repme, addings = False, regex = regexOnCommons)
                    # Problems? No, return True
                    return True
            else:
                # Problems? No, return True
                return True

    def checkImageDuplicated(self, duplicates_rollback):
        """ Function to check the duplicated images. """
        # {{Dupe|Image:Blanche_Montel.jpg}}
        # Skip the stub images
        #if 'stub' in self.imageName.lower() and self.project == 'wikipedia' and self.site.lang == 'it':
        #    return True # Skip the stub, ok
        dupText = wikipedia.translate(self.site, duplicatesText)
        dupRegex = wikipedia.translate(self.site, duplicatesRegex)
        dupTalkHead = wikipedia.translate(self.site, duplicate_user_talk_head)
        dupTalkText = wikipedia.translate(self.site, duplicates_user_talk_text)
        dupComment_talk = wikipedia.translate(self.site, duplicates_comment_talk)
        dupComment_image = wikipedia.translate(self.site, duplicates_comment_image)
        duplicateRegex = r'\n\*(?:\[\[:Image:%s\]\] has the following duplicates(?: \(\'\'\'forced mode\'\'\'\)|):|\*\[\[:Image:%s\]\])$' % (self.convert_to_url(self.imageName), self.convert_to_url(self.imageName))
        imagePage = wikipedia.ImagePage(self.site, u'Image:%s' % self.imageName)
        hash_found = imagePage.getHash()
        duplicates = self.site.getImagesFromAnHash(hash_found)
        if duplicates == None:
            return False # Error, image deleted, no hash found. Skip the image.
        if len(duplicates) > 1:
            if len(duplicates) == 2:
                wikipedia.output(u'%s has a duplicate! Reporting it...' % self.imageName)
            else:
                wikipedia.output(u'%s has %s duplicates! Reporting them...' % (self.imageName, len(duplicates) - 1))
            if not dupText == None and not dupRegex == None:
                time_image_list = list()
                time_list = list()
                for duplicate in duplicates:
                    DupePage = wikipedia.ImagePage(self.site, u'Image:%s' % duplicate)
                    if DupePage == self.image and self.timestamp != None:
                        imagedata = self.timestamp
                    else:
                        imagedata = DupePage.getLatestUploader()[1]
                    # '2008-06-18T08:04:29Z'
                    data = time.strptime(imagedata, u"%Y-%m-%dT%H:%M:%SZ")
                    data_seconds = time.mktime(data)
                    time_image_list.append([data_seconds, duplicate])
                    time_list.append(data_seconds)
                older_image = self.returnOlderTime(time_image_list, time_list)
                # And if the images are more than two?
                Page_oder_image = wikipedia.ImagePage(self.site, u'Image:%s' % older_image)
                string = ''
                images_to_tag_list = []
                for duplicate in duplicates:
                    if wikipedia.ImagePage(self.site, u'%s:%s' % (self.image_namespace, duplicate)) == \
                       wikipedia.ImagePage(self.site, u'%s:%s' % (self.image_namespace, older_image)):
                        continue # the older image, not report also this as duplicate
                    DupePage = wikipedia.ImagePage(self.site, u'Image:%s' % duplicate)
                    try:
                        DupPageText = DupePage.get()
                        older_page_text = Page_oder_image.get()
                    except wikipedia.NoPage:
                        continue # The page doesn't exists
                    if re.findall(dupRegex, DupPageText) == [] and re.findall(dupRegex, older_page_text) == []:
                        wikipedia.output(u'%s is a duplicate and has to be tagged...' % duplicate)
                        images_to_tag_list.append(duplicate)
                        #if duplicate != duplicates[-1]:
                        string += u"*[[:%s%s]]\n" % (self.image_namespace, duplicate)
                        #else:
                        #    string += "*[[:%s%s]]" % (self.image_namespace, duplicate)
                    else:
                        wikipedia.output(u"Already put the dupe-template in the image's page or in the dupe's page. Skip.")
                        return True # Ok - No problem. Let's continue the checking phase
                older_image_ns = u'%s%s' % (self.image_namespace, older_image) # adding the namespace
                only_report = False # true if the image are not to be tagged as dupes

                # put only one image or the whole list according to the request
                if u'__images__' in dupText:
                    text_for_the_report = re.sub(r'__images__', r'\n%s*[[:%s]]\n' % (string, older_image_ns), dupText)
                else:
                    text_for_the_report = re.sub(r'__image__', r'%s' % older_image_ns, dupText)
                # Two iteration: report the "problem" to the user only once (the last)
                if len(images_to_tag_list) > 1:
                    for image_to_tag in images_to_tag_list[:-1]:
                        already_reported_in_past = self.countEdits(u'Image:%s' % image_to_tag, self.botolist)
                        # if you want only one edit, the edit found should be more than 0 -> num - 1
                        if already_reported_in_past > duplicates_rollback - 1:
                            only_report = True
                            break
                        # Delete the image in the list where we're write on
                        text_for_the_report = re.sub(r'\n\*\[\[:%s\]\]' % (self.image_namespace + image_to_tag), '', text_for_the_report)
                        self.report(text_for_the_report, image_to_tag,
                                    commImage = dupComment_image, unver = True)
                if len(images_to_tag_list) != 0 and not only_report:
                    already_reported_in_past = self.countEdits(u'Image:%s' % images_to_tag_list[-1], self.botolist)
                    # It's a regex, we need to fix the name in order to make it regex-compatible.
                    replaces_to_perform = [[' ', '_'], ['(', '\('], [')', '\)'], ['.', '\.'], ['[', '\['], [']', '\]'],
                                           ['{', '\{'], ['}', '\}']]
                    for replace_to_perform in replaces_to_perform:
                        image_to_resub = images_to_tag_list[-1].replace(replace_to_perform[0], replace_to_perform[1])
                    from_regex = r'\n\*\[\[:%s\]\]' % (self.image_namespace + image_to_resub)
                    # Delete the image in the list where we're write on
                    text_for_the_report = re.sub(from_regex, '', text_for_the_report)
                    # if you want only one edit, the edit found should be more than 0 -> num - 1
                    if already_reported_in_past > duplicates_rollback - 1:
                        only_report = True
                    else:
                        self.report(text_for_the_report, images_to_tag_list[-1],
                            dupTalkText % (older_image_ns, string), dupTalkHead, commTalk = dupComment_talk,
                                commImage = dupComment_image, unver = True)
            if self.duplicatesReport or only_report:
                if only_report:
                    repme = u"\n*[[:Image:%s]] has the following duplicates ('''forced mode'''):" % self.convert_to_url(self.imageName)
                else:
                    repme = u"\n*[[:Image:%s]] has the following duplicates:" % self.convert_to_url(self.imageName)
                for duplicate in duplicates:
                    if self.convert_to_url(duplicate) == self.convert_to_url(self.imageName):
                        continue # the image itself, not report also this as duplicate
                    repme += u"\n**[[:Image:%s]]" % self.convert_to_url(duplicate)
                result = self.report_image(self.imageName, self.rep_page, self.com, repme, addings = False, regex = duplicateRegex)
                if not result:
                    return True # If Errors, exit (but continue the check)                
            if older_image != self.imageName:
                return False # The image is a duplicate, it will be deleted. So skip the check-part, useless
        return True # Ok - No problem. Let's continue the checking phase

    def report_image(self, image_to_report, rep_page = None, com = None, rep_text = None, addings = True, regex = None):
        """ Function to report the images in the report page when needed. """
        if rep_page == None: rep_page = self.rep_page
        if com == None: com = self.com
        if rep_text == None: rep_text = self.rep_text
        another_page = wikipedia.Page(self.site, rep_page)
        if regex == None: regex = image_to_report
        try:
            text_get = another_page.get()
        except wikipedia.NoPage:
            text_get = ''
        except wikipedia.IsRedirectPage:            
            text_get = another_page.getRedirectTarget().get()
        if len(text_get) >= self.logFulNumber:
            raise LogIsFull(u"The log page (%s) is full! Please delete the old images reported." % another_page.title())
        pos = 0
        # The talk page includes "_" between the two names, in this way i replace them to " "
        n = re.compile(regex, re.UNICODE|re.M)
        y = n.search(text_get, pos)
        if y == None:
            # Adding the log
            if addings:
                rep_text = rep_text % image_to_report # Adding the name of the image in the report if not done already
            another_page.put(text_get + rep_text, comment = com, minorEdit = False)
            wikipedia.output(u"...Reported...")
            reported = True
        else:
            pos = y.end()
            wikipedia.output(u"%s is already in the report page." % image_to_report)
            reported = False
        return reported

    def takesettings(self):
        """ Function to take the settings from the wiki. """
        try:
            if self.settings == None: self.settingsData = None
            else:
                x = wikipedia.Page(self.site, self.settings)
                self.settingsData = list()
                try:
                    testo = x.get()
                    rxp = r"<------- ------->\n\*[Nn]ame ?= ?['\"](.*?)['\"]\n\*([Ff]ind|[Ff]indonly)=(.*?)\n\*[Ii]magechanges=(.*?)\n\*[Ss]ummary=['\"](.*?)['\"]\n\*[Hh]ead=['\"](.*?)['\"]\n\*[Tt]ext ?= ?['\"](.*?)['\"]\n\*[Mm]ex ?= ?['\"]?(.*?)['\"]?$"
                    r = re.compile(rxp, re.UNICODE|re.M)
                    number = 1
                    for m in r.finditer(testo):
                        name = str(m.group(1))
                        find_tipe = str(m.group(2))
                        find = str(m.group(3))
                        imagechanges = str(m.group(4))
                        summary = str(m.group(5))
                        head = str(m.group(6))
                        text = str(m.group(7))
                        mexcatched = str(m.group(8))
                        tupla = [number, name, find_tipe, find, imagechanges, summary, head, text, mexcatched]
                        self.settingsData += [tupla]
                        number += 1
                    if self.settingsData == list():
                        wikipedia.output(u"You've set wrongly your settings, please take a look to the relative page. (run without them)")
                        self.settingsData = None
                except wikipedia.NoPage:
                    wikipedia.output(u"The settings' page doesn't exist!")
                    self.settingsData = None
        except wikipedia.Error:
            # Error? Settings = None
            wikipedia.output(u'Problems with loading the settigs, run without them.')
            self.settingsData = None
            self.some_problem = False
        if self.settingsData == []:
            self.settingsData = None
        # Real-Time page loaded
        if self.settingsData != None: wikipedia.output(u'\t   >> Loaded the real-time page... <<')
        # No settings found, No problem, continue.
        else: wikipedia.output(u'\t   >> No additional settings found! <<')
        return self.settingsData # Useless, but it doesn't harm..

    def load_licenses(self):
        """ Load the list of the licenses """
        catName = wikipedia.translate(self.site, category_with_licenses)
        cat = catlib.Category(wikipedia.getSite(), catName)
        categories = [page.title() for page in pagegenerators.SubCategoriesPageGenerator(cat)]
        categories.append(catName)
        list_licenses = list()
        wikipedia.output(u'\n\t...Loading the licenses allowed...\n')
        for catName in categories:
            cat = catlib.Category(wikipedia.getSite(), catName)
            gen = pagegenerators.CategorizedPageGenerator(cat)
            pages = [page for page in gen]
            list_licenses.extend(pages)

        # Add the licenses set in the default page as licenses
        # to check
        if self.pageAllowed != None:
            try:
                pageAllowedText = wikipedia.Page(self.site, self.pageAllowed).get()
            except (wikipedia.NoPage, wikipedia.IsRedirectPage):
                pageAllowedText = ''
            for nameLicense in self.load(pageAllowedText):
                if not 'template:' in nameLicense.lower():
                    nameLicense = u'Template:%s' % nameLicense
                pageLicense = wikipedia.Page(self.site, nameLicense)
                if pageLicense not in list_licenses:
                    list_licenses.append(pageLicense) # the list has wiki-pages
        return list_licenses

    def giveMeTheTemplate(self, license_selected):
        """ From the name of a template see if it's template:something or just
            an inclusion of another namespace != template. If it's a redirect
            gets the real page, if there's a NoPage, return None.
        """
        #print template.exists()
        template = wikipedia.Page(self.site, u'Template:%s' % license_selected)
        try:
            template.pageAPInfo()
        except wikipedia.NoPage:
            try:
                template = wikipedia.Page(self.site, license_selected)
                template.pageAPInfo()
            except (wikipedia.NoPage, wikipedia.IsRedirectPage):
                return None # break and exit
        except wikipedia.IsRedirectPage:
            template = template.getRedirectTarget()
        return template

    def smartDetection(self, image_text):
        """ The bot instead of checking if there's a simple template in the
            image's description, checks also if that template is a license or
            something else. In this sense this type of check is smart.
            """
        seems_ok = False
        license_found = None
        regex_find_licenses = re.compile(r'\{\{(?:[Tt]emplate:|)(.*?)(?:[|\n<].*?|)\}\}', re.DOTALL)
        licenses_found = regex_find_licenses.findall(image_text)
        second_round = False

        exit_cicle = False # howTo exit from both the for and the while cicle
        while 1:
            if exit_cicle: # howTo exit from the while
                break
            if licenses_found != []:
                for license_selected in licenses_found:
                    # put the first, if there is problem, this will be reported in the log
                    if license_found == None:
                        license_found = license_selected
                    try:
                        template = self.giveMeTheTemplate(license_selected)
                        if template == None:
                            continue
                    except wikipedia.BadTitle:
                        # Template with wrong name, no need to report, simply skip
                        continue
                    if template in self.list_licenses: # the list_licenses are loaded in the __init__ (not to load them multimple times)
                        seems_ok = True
                        exit_cicle = True
                        license_found = license_selected # let the last "fake" license normally detected
                        break
                # previous block was unsuccessful? Try with the next one
                for license_selected in licenses_found:
                    try:
                        template = self.giveMeTheTemplate(license_selected)
                        if template == None:
                            continue # ok, this template it's not ok, continue..                          
                    except wikipedia.BadTitle:
                        # Template with wrong name, no need to report, simply skip
                        continue                          
                    try:                         
                        template_text = template.get()            
                    except wikipedia.NoPage:
                        continue # ok, this template it's not ok, continue..
                    regex_noinclude = re.compile(r'<noinclude>(.*?)</noinclude>', re.DOTALL)
                    template_text = regex_noinclude.sub('', template_text)
                    if second_round == False:
                        licenses_found = regex_find_licenses.findall(template_text)
                        second_round = True
                        break # only exit from the for, not from the while
                    else:
                        exit_cicle = True
                        break
        if not seems_ok:
            rep_text_license_fake = u"\n*[[:Image:%s]] seems to have a ''fake license'', license detected: {{tl|%s}}." % (self.imageName, license_found)
            regexFakeLicense = r"\* ?\[\[:Image:%s\]\] seems to have a ''fake license'', license detected: \{\{tl\|%s\}\}\.$" % (self.imageName, license_found)
            printWithTimeZone(u"%s seems to have a fake license: %s, reporting..." % (self.imageName, license_found))
            self.report_image(self.imageName, rep_text = rep_text_license_fake,
                                   addings = False, regex = regexFakeLicense)
        else:
            printWithTimeZone(u"%s seems ok, license found: %s..." % (self.imageName, license_found))
        return license_found

    def load(self, raw):
        """ Load a list of object from a string using regex. """
        list_loaded = list()
        pos = 0
        load_2 = True
        # I search with a regex how many user have not the talk page
        # and i put them in a list (i find it more easy and secure)
        regl = r"(\"|\')(.*?)\1(?:,|\])"
        pl = re.compile(regl, re.UNICODE)
        for xl in pl.finditer(raw):
            word = xl.group(2).replace(u'\\\\', u'\\')
            if word not in list_loaded:
                list_loaded.append(word)
        return list_loaded

    def skipImages(self, skip_number, limit):
        """ Given a number of images, skip the first -number- images. """
        # If the images to skip are more the images to check, make them the same number
        if skip_number == 0:
            wikipedia.output(u'\t\t>> No images to skip...<<')
            return False
        if skip_number > limit: skip_number = limit
        # Print a starting message only if no images has been skipped
        if self.skip_list == []:
            if skip_number == 1:
                wikipedia.output(u'Skipping the first image:\n')
            else:
                wikipedia.output(u'Skipping the first %s images:\n' % skip_number)
        # If we still have pages to skip:
        if len(self.skip_list) < skip_number:
            wikipedia.output(u'Skipping %s...' % self.imageName)
            self.skip_list.append(self.imageName)
            if skip_number == 1:
                wikipedia.output('')
            return True
        else:
            wikipedia.output('') # Print a blank line.
            return False
        
    def wait(self, waitTime):
        """ Skip the images uploaded before x seconds to let
            the users to fix the image's problem alone in the
            first x seconds.
        """
        #http://pytz.sourceforge.net/ <- maybe useful?
        imagedata = self.timestamp
        # '2008-06-18T08:04:29Z'
        img_time = datetime.datetime.strptime(imagedata, u"%Y-%m-%dT%H:%M:%SZ") #not relative to localtime
        now = datetime.datetime.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S") #timezones are UTC
        # + seconds to be sure that now > img_time
        while now < img_time:
            now = (now + datetime.timedelta(seconds=1))
        delta = now - img_time
        secs_of_diff = delta.seconds
        if waitTime > secs_of_diff:
            wikipedia.output(u'Skipping %s, uploaded %s seconds ago..' % (self.imageName, int(secs_of_diff)))
            return True # Still wait
        else:
            return False # No ok, continue

     
    def isTagged(self):
        """ Understand if an image is already tagged or not. """
        TextFind = wikipedia.translate(self.site, txt_find)
        # Is the image already tagged? If yes, no need to double-check, skip
        for i in TextFind:
            # If there are {{ use regex, otherwise no (if there's not the {{ may not be a template
            # and the regex will be wrong)
            if '{{' in i:
                regexP = re.compile(r'\{\{(?:template|)%s ?(?:\||\n|\}|<) ?' % i.split('{{')[1].replace(u' ', u'[ _]'), re.I)
                result = regexP.findall(self.imageCheckText)
                if result != []:
                    return True
            elif i.lower() in self.imageCheckText:
                return True
        return False # Nothing Found? Ok: False

    def whiteTemplateEraser(self):
        """ Erase the white template from the checking text and return how many have been found. """
        # Load the white templates(hidden template is the same as white template, regarding the meaning)
        white_templates_found = 0
        hiddentemplate = self.loadHiddenTemplates()
        for l in hiddentemplate:
            if self.tagged == False:
                # why creator? Because on commons there's a template such as {{creator:name}} that.. works
                res = re.findall(r'\{\{(?:[Tt]emplate:|)(?:%s[ \n]*?(?:\n|\||\}|<)|creator:)' % l.lower(), self.imageCheckText.lower())
                if res != []:
                    white_templates_found += 1
                    if l != '' and l != ' ': # Check that l is not nothing or a space
                        # Deleting! (replace the template with nothing)
                        regex_white_template = re.compile(r'\{\{(?:template:|)(?:%s|creator)' % l, re.IGNORECASE)
                        self.imageCheckText = regex_white_template.sub(r'', self.imageCheckText)
        if white_templates_found == 1:
            wikipedia.output(u'A white template found, skipping the template...')
        elif white_templates_found > 1:
            wikipedia.output(u'White templates found: %s; skipping those templates...' % white_templates_found)
        return white_templates_found        

    def findAdditionalProblems(self):
        # In every tupla there's a setting configuration
        for tupla in self.settingsData:
            name = tupla[1]
            find_tipe = tupla[2]
            find = tupla[3]
            find_list = self.load(find)
            imagechanges = tupla[4]
            if imagechanges.lower() == 'false':
                imagestatus = False
            elif imagechanges.lower() == 'true':
                imagestatus = True
            else:
                wikipedia.output(u"Error! Imagechanges set wrongly!")
                self.settingsData = None
                break
            summary = tupla[5]
            head_2 = tupla[6]
            text = tupla[7]
            text = text % self.imageName
            mexCatched = tupla[8]
            for k in find_list:
                if find_tipe.lower() == 'findonly':
                    searchResults = re.findall(r'%s' % k.lower(), self.imageCheckText.lower())
                    if searchResults != []:
                        if searchResults[0] == self.imageCheckText.lower():
                            self.some_problem = True
                            self.text_used = text
                            self.head_used = head_2
                            self.imagestatus_used = imagestatus
                            self.name_used = name
                            self.summary_used = summary
                            self.mex_used = mexCatched
                            break
                elif find_tipe.lower() == 'find':
                    if re.findall(r'%s' % k.lower(), self.imageCheckText.lower()) != []:
                        self.some_problem = True
                        self.text_used = text
                        self.head_used = head_2
                        self.imagestatus_used = imagestatus
                        self.name_used = name
                        self.summary_used = summary
                        self.mex_used = mexCatched
                        continue

    def checkStep(self, smartdetection):
        # nothing = Defining an empty image description
        nothing = ['', ' ', '  ', '   ', '\n', '\n ', '\n  ', '\n\n', '\n \n', ' \n', ' \n ', ' \n \n']
        # something = Minimal requirements for an image description.
        # If this fits, no tagging will take place (if there aren't other issues)
        # MIT license is ok on italian wikipedia, let also this here
        something = ['{{'] # Don't put "}}" here, please. Useless and can give problems.
        # Unused file extensions. Does not contain PDF.
        notallowed = ("xcf", "xls", "sxw", "sxi", "sxc", "sxd")        
        brackets = False 
        delete = False
        extension = self.imageName.split('.')[-1] # get the extension from the image's name
        # Load the notification messages
        HiddenTN = wikipedia.translate(self.site, HiddenTemplateNotification)
        unvertext = wikipedia.translate(self.site, n_txt)
        di = wikipedia.translate(self.site, delete_immediately)
        dih = wikipedia.translate(self.site, delete_immediately_head)
        din = wikipedia.translate(self.site, delete_immediately_notification)
        nh = wikipedia.translate(self.site, nothing_head)
        nn = wikipedia.translate(self.site, nothing_notification)
        dels = wikipedia.translate(self.site, del_comm)
        smwl = wikipedia.translate(self.site, second_message_without_license)

        # Some formatting for delete immediately template
        di = u'\n%s' % di
        dels = dels % di
        
        # Page => ImagePage
        # Get the text in the image (called imageCheckText)
        try:
            # the checkText will be modified in order to make the check phase easier
            # the imageFullText will be used when the full text is needed without changes
            self.imageCheckText = self.image.get()
            self.imageFullText = self.imageCheckText
        except wikipedia.NoPage:
            wikipedia.output(u"Skipping %s because it has been deleted." % self.imageName)
            return True
        except wikipedia.IsRedirectPage:
            wikipedia.output(u"The file description for %s is a redirect?!" % self.imageName)
            return True
        # Delete the fields where the templates cannot be loaded
        regex_nowiki = re.compile(r'<nowiki>(.*?)</nowiki>', re.DOTALL)
        regex_pre = re.compile(r'<pre>(.*?)</pre>', re.DOTALL)
        self.imageCheckText = regex_nowiki.sub('', self.imageCheckText); self.imageCheckText = regex_pre.sub('', self.imageCheckText)        
        # Deleting the useless template from the description (before adding something
        # in the image the original text will be reloaded, don't worry).
        self.tagged = self.isTagged()
        white_templates_found = self.whiteTemplateEraser()
        if white_templates_found != 0:
            hiddenTemplateFound = True
        else:
            hiddenTemplateFound = False
        for a_word in something: # something is the array with {{, MIT License and so on.
            if a_word in self.imageCheckText:
                # There's a template, probably a license (or I hope so)
                brackets = True
        # Is the extension allowed? (is it an image or f.e. a .xls file?)
        for parl in notallowed:
            if parl.lower() in extension.lower():
                delete = True
        self.some_problem = False # If it has "some_problem" it must check
                  # the additional settings.
        # if self.settingsData, use addictional settings
        if self.settingsData != None:
            self.findAdditionalProblems()
        # If the image exists (maybe it has been deleting during the oder
        # checking parts or something, who knows? ;-))
        #if p.exists(): <-- improve the bot, better to make as
        #                   less call to the server as possible
        # Here begins the check block.
        if self.tagged == True:
            # Tagged? Yes, skip.
            printWithTimeZone(u'%s is already tagged...' % self.imageName)
            return True
        if self.some_problem == True:
            if self.mex_used in self.imageCheckText:
                wikipedia.output(u'Image already fixed. Skip.')
                return True
            wikipedia.output(u"The image description for %s contains %s..." % (self.imageName, self.name_used))
            if self.mex_used.lower() == 'default':
                self.mex_used = unvertext
            if self.imagestatus_used == False:
                reported = self.report_image(self.imageName)
            else:
                reported = True
            if reported == True:
                #if self.imagestatus_used == True:
                self.report(self.mex_used, self.imageName, self.text_used, u"\n%s\n" % self.head_used, None, self.imagestatus_used, self.summary_used)
            else:
                wikipedia.output(u"Skipping the image...")
            self.some_problem = False
            return True
        elif brackets == True:
            seems_ok = False
            license_found = None
            if smartdetection:
                license_found = self.smartDetection(self.imageCheckText)
            else:
                printWithTimeZone(u"%s seems ok..." % self.imageName)
            # It works also without this... but i want only to be sure ^^
            brackets = False
            return True
        elif delete == True:
            wikipedia.output(u"%s is not a file!" % self.imageName)
            # Modify summary text
            wikipedia.setAction(dels)
            canctext = di % extension
            notification = din % self.imageName
            head = dih
            self.report(canctext, self.imageName, notification, head)
            delete = False
            return True
        elif self.imageCheckText in nothing:
            wikipedia.output(u"The image description for %s does not contain a license template!" % self.imageName)
            if hiddenTemplateFound and HiddenTN != None and HiddenTN != '' and HiddenTN != ' ':
                notification = HiddenTN % self.imageName
            else:
                notification = nn % self.imageName
            head = nh
            self.report(unvertext, self.imageName, notification, head, smwl)
            return True
        else:
            wikipedia.output(u"%s has only text and not the specific license..." % self.imageName)
            if hiddenTemplateFound and HiddenTN != None and HiddenTN != '' and HiddenTN != ' ':
                notification = HiddenTN % self.imageName
            else:
                notification = nn % self.imageName
            head = nh
            self.report(unvertext, self.imageName, notification, head, smwl)
            return True

def checkbot():
    """ Main function """
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
    duplicatesActive = False # Use the duplicate option
    duplicatesReport = False # Use the duplicate-report option
    sendemailActive = False # Use the send-email
    smartdetection = False # Enable the smart detection

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
        elif arg.startswith('-duplicates'):
            duplicatesActive = True
            if len(arg) == 11:
                duplicates_rollback = 1
            elif len(arg) > 11:
                duplicates_rollback = int(arg[12:])
        elif arg == '-duplicatereport':
            duplicatesReport = True
        elif arg == '-sendemail':
            sendemailActive = True
        elif arg == '-smartdetection':
            smartdetection = True
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
            generator = wikipedia.getSite().allpages(start=firstPageTitle, namespace=6)
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
    image_namespace = u"%s:" % image_n # Example: "User_talk:"

    # If the images to skip are 0, set the skip variable to False (the same for the wait time)
    if skip_number == 0:
        skip = False
    if wait_number == 0:
        wait = False

    # A little block-statement to ensure that the bot will not start with en-parameters
    if site.lang not in project_inserted:
        wikipedia.output(u"Your project is not supported by this script. You have to edit the script and add it!")
        return

    # Reading the log of the new images if another generator is not given.
    if normal == True:
        if limit == 1:
            wikipedia.output(u"Retrieving the latest file for checking...")
        else:
            wikipedia.output(u"Retrieving the latest %d files for checking..." % limit)
    # Main Loop
    while 1:
        # Defing the Main Class.
        mainClass = main(site, sendemailActive = sendemailActive, duplicatesReport = duplicatesReport, smartdetection = smartdetection)
        # Untagged is True? Let's take that generator
        if untagged == True:
            generator =  mainClass.untaggedGenerator(projectUntagged, limit)
            normal = False # Ensure that normal is False
        # Normal True? Take the default generator
        if normal == True:
            generator = site.newimages(number = limit)
        # if urlUsed and regexGen, get the source for the generator
        if urlUsed == True and regexGen == True:
            textRegex = site.getUrl(regexPageUrl, no_hostname = True)
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
        # Take the additional settings for the Project
        mainClass.takesettings()
        # Not the main, but the most important loop.
        #parsed = False
        if wait:
            printWithTimeZone(u'Skipping the images uploaded less than %s seconds ago..' % wait_number)
        for image in generator:
            # When you've a lot of image to skip before working use this workaround, otherwise
            # let this commented, thanks. [ decoment also parsed = False if you want to use it
            #
            #if image.title() != u'Immagine:Nytlogo379x64.gif' and not parsed:
            #    wikipedia.output(u"%s already parsed." % image.title())
            #    continue
            #else:
            #    parsed = True
            # If the generator returns something that is not an image, simply skip it.
            if normal == False and regexGen == False:
                if image_namespace.lower() not in image.title().lower() and \
                'image:' not in image.title().lower():
                    wikipedia.output(u'%s seems not an image, skip it...' % image.title())
                    continue
            if normal:
                imageData = image
                image = imageData[0]
                timestamp = imageData[1]
                uploader = imageData[2]
                comment = imageData[3] # useless, in reality..
            else:
                timestamp = None
                uploader = None
                comment = None # useless, also this, let it here for further developments
            try:
                imageName = image.title().split(image_namespace)[1] # Deleting the namespace (useless here)
            except IndexError:# Namespace image not found, that's not an image! Let's skip...
                wikipedia.output(u"%s is not an image, skipping..." % image.title())
                continue
            mainClass.setParameters(imageName, timestamp, uploader) # Setting the image for the main class
            # If I don't inizialize the generator, wait part and skip part are useless
            if wait:
                # Let's sleep...
                wait = mainClass.wait(wait_number)
                if wait:
                    continue          
            # Skip block
            if skip == True:
                skip = mainClass.skipImages(skip_number, limit)
                if skip == True:
                    continue             
            # Check on commons if there's already an image with the same name
            if commonsActive == True:
                response = mainClass.checkImageOnCommons()
                if response == False:
                    continue
            # Check if there are duplicates of the image on the project selected
            if duplicatesActive == True:
                response2 = mainClass.checkImageDuplicated(duplicates_rollback)
                if response2 == False:
                    continue
            resultCheck = mainClass.checkStep(smartdetection)
            if resultCheck:
                continue
    # A little block to perform the repeat or to break.
        if repeat == True:
            printWithTimeZone(u"Waiting for %s seconds," % time_sleep)
            time.sleep(time_sleep)
        elif repeat == False:
            wikipedia.output(u"\t\t\t>> STOP! <<")
            break # Exit

# Here there is the main loop. I'll take all the (name of the) images and then i'll check them.
if __name__ == "__main__":
    try:
        checkbot()
    finally:
        wikipedia.stopme()
