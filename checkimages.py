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
* Add new documentation
* Add a report for the image tagged.
* Fix the settings part when the bot save the data (make it better)
"""

#
# (C) Kyle/Orgullomoore, 2006-2007 (newimage.py)
# (C) Siebrand Mazeland, 2007
# (C) Filnik, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: checkimages.py,v 1.0 2007/11/27 16:00:25 filnik Exp$'
#

import re, time, urllib2
import wikipedia, config, os, locale, sys
import cPickle, pagegenerators, catlib

locale.setlocale(locale.LC_ALL, '')
#########################################################################################################################
# <------------------------------------------- Change only below! ----------------------------------------------------->#
#########################################################################################################################

# That's what you want that will be added. (i.e. the {{no source}} with the right day/month/year )
n_txt = {
        'commons':'\n{{subst:nld}}',
    'en'     :'\n{{subst:nld}}',
    'it'     :'\n{{subst:unverdata}}',
    'ja':'{{subst:Nsd}}',
    'hu'     :u'\n{{nincslicenc|~~~~~}}',
    'zh'    :'{{subst:No license/auto}}',
}

txt_find =  {
    'commons':['{{no license', '{{nld'],
        'en':['{{nld', '{{no license'],
    'hu':[u'{{nincsforrás',u'{{nincslicenc'],
    'it':[u'{{unverdata', u'{{unverified'],
    'ja':[u'{{no source', u'{{unknown', u'{{non free', u'<!--削除についての議論が終了するまで',],
    'zh':[u'{{no source', u'{{unknown','{{No license',],
                }

# Summary for when the will add the no source
comm = {
		'commons':'Bot: Marking newly uploaded untagged file',
		'en'     :'Bot: Marking newly uploaded untagged file',
		'hu'    :'Robot: Frissen feltöltött licencsablon nélküli fájl megjelölése',
		'it'     :"Bot: Aggiungo unverified",
		'ja':u'ロボットによる:出典やライセンスなしの画像をタグ',
		'zh':u'機器人:標示新上傳且未包含必要資訊的檔案',
		}

# Summary that the bot use when it notify the problem with the image's license
comm2 = {
		'commons':"Bot: Requesting source information." ,
		'en'     :"Bot: Requesting source information." ,
		'it'     :"Bot: Notifico l'unverified",
		'ja'     :u"ロボットによる:出典とライセンス明記のお願い",
		'hu' :'Robot: Forrásinformáció kérése',
		'zh'     :u"機器人: 請求來源資訊"
		}

# When the Bot find that the usertalk is empty is not pretty to put only the no source without the welcome, isn't it?
empty = {
		'commons':'{{subst:welcome}}\n~~~~\n',
		'en'     :'{{welcome}}\n~~~~\n',
		'it'     :'{{benvenuto}}\n~~~~\n',
		'ja':'{{welcome}}\n--~~~~\n',
		'hu'     :u'{{subst:Üdvözlet|~~~~}}\n',
		'zh':'{{subst:welcome|sign=~~~~}}',
		}

# General summary
unver = {
		'commons':'Bot: no source',
		'en'     :'Bot: no source',
		'hu'     :'Robot: nincs forrás',
		'it'     :'Bot: Unverified!',
		'ja':u'ロボットによる: 出典なし',
		'zh':u'機器人:沒有來源資訊',
		}

# if the file has an unknown extension it will be tagged with this template.
# In reality, there aren't unknown extension, they are only not allewed... ^__^
delete_immediately = {
			'commons':"{{db-meta|The file has .%s as extension.}}",
			'en'     :"{{db-meta|The file has .%s as extension.}}",
			'it'     :'{{cancella subito|motivo=Il file ha come estensione ".%s"}}',
			'ja':u'{{db|知らないファイルフォーマット%s}}',
			'hu'     :u'{{azonnali|A fájlnak .%s a kiterjesztése}}',
			'zh'    :u'{{delete|未知檔案格式%s}}',
			}

# The header of the Unknown extension's message.
delete_immediately_head = {
			'commons':"\n== Unknown extension! ==\n",
			'en'     :"\n== Unknown extension! ==\n",
			'it'     :'\n== File non specificato ==\n',
			'hu'     :u'\n== Ismeretlen kiterjesztésű fájl ==\n',
			'zh':u'\n==您上載的檔案格式可能有誤==\n',
			}

# Text that will be add if the bot find a unknown extension.
delete_immediately_notification = {
                                'commons':'The [[:Image:%s]] file has a wrong extension, please check. ~~~~',
				'en'     :'The [[:Image:%s]] file has a wrong extension, please check. ~~~~',
				'it'     :'{{subst:Utente:Filbot/Ext|%s}}',
				'hu'     :u'A [[:Kép:%s]] fájlnak rossz a kiterjesztése, kérlek ellenőrízd. ~~~~',
				'zh'    :u'您好，你上傳的[[:Image:%s]]無法被識別，請檢查您的檔案，謝謝。--~~~~',
				}
# Summary of the delate immediately. (f.e: Adding {{db-meta|The file has .%s as extension.}})
del_comm = {
			'commons':'Bot: Adding %s',
			'en'     :'Bot: Adding %s',
			'it'     :'Bot: Aggiungo %s',
			'ja'     :u'ロボットによる: 追加 %s',
			'hu'     :u'Robot:"%s" hozzáadása',
			'zh'     :u'機器人: 正在新增 %s',
			}

# This is the most important header, because it will be used a lot. That's the header that the bot
# will add if the image hasn't the license.
nothing_head = {
				'commons':"",# Nothing, the template has already the header inside.
				'en'     :"\n== Image without license ==\n",
				'ja':u'',
				'it'     :"\n== Immagine senza licenza ==\n",
				'hu'     :u"\n== Licenc nélküli kép ==\n",
				'zh'    :u'',
				}
# That's the text that the bot will add if it doesn't find the license.
nothing_notification = {
				'commons':"\n{{subst:User:Filnik/untagged|Image:%s}}\n\n''This message was '''added automatically by [[User:Filbot|Filbot]]''', if you need some help about it, ask [[User:Filnik|its master]] or go to the [[Commons:Help desk]]''. --~~~~",
				'en'     :"{{subst:image source|Image:%s}} --~~~~",
				'it'     :"{{subst:Utente:Filbot/Senza licenza|%s}} --~~~~",
				'ja'	:"\n{{subst:image source|Image:%s}}--~~~~",
				'hu'     :u"{{subst:adjforrást|Kép:%s}} \n Ezt az üzenetet ~~~ automatikusan helyezte el a vitalapodon, kérdéseddel fordulj a gazdájához, vagy a [[WP:KF|Kocsmafalhoz]]. --~~~~",
				'zh'   :u'\n{{subst:Uploadvionotice|Image:%s}} ~~~~ ',
				}
# This is a list of what bots used this script in your project.
# NOTE: YOUR Botnick is automatically added. It's not required to add it twice.
bot_list = {
			'commons':['Siebot', 'CommonsDelinker'],
			'en'     :['OrphanBot'],
			'it'     :['Filbot', 'Nikbot', '.snoopyBot.'],
			'ja':['alexbot'],
			'zh':['alexbot'],
			}

# The message that the bot will add the second time that find another license problem.
second_message_without_license = {
				'commons':None,
                                'en': None,
				'it':':{{subst:Utente:Filbot/Senza licenza2|%s}} --~~~~',
				'hu':u'\nSzia! Úgy tűnik a [[:Kép:%s]] képpel is hasonló a probléma, mint az előbbivel. Kérlek olvasd el a [[WP:KÉPLIC|feltölthető képek]]ről szóló oldalunk, és segítségért fordulj a [[WP:KF-JO|Jogi kocsmafalhoz]]. Köszönöm --~~~~',
				'ja':None,
				'zh':None,
				}
# You can add some settings to wikipedia. In this way, you can change them without touch the code.
# That's useful if you are running the bot on Toolserver.
page_with_settings = {
					'commons':u'User:Filbot/Settings',
                                        'en':None,
                                        'hu':None,
					'it':u'Utente:Nikbot/Settings#Settings',
					'ja':None,
					'zh':u"User:Alexbot/cisettings#Settings",
					}
# The bot can report some images (like the images that have the same name of an image on commons)
# This is the page where the bot will store them.
report_page = {
				'commons':'User:Filbot/Report',
                                'en'     :'User:Filnik/Report',
				'it'     :'Utente:Nikbot/Report',
				'ja':'User:Alexbot/report',
				'hu'     :'User:Bdamokos/Report',
				'zh'    :'User:Alexsh/checkimagereport',
				}
# Adding the date after the signature. 
timeselected = u' ~~~~~'
# The text added in the report
report_text = {
			'commons':"\n*[[:Image:%s]] " + timeselected,
			'en':"\n*[[:Image:%s]] " + timeselected,
			'it':"\n*[[:Immagine:%s]] " + timeselected,
			'ja':"\n*[[:Immagine:%s]] " + timeselected,
			'hu':u"\n*[[:Kép:%s]] " + timeselected,
			'zh':"\n*[[:Image:%s]] " + timeselected,
			}
# The summary of the report
comm10 = {
		'commons':'Bot: Updating the log',
		'en':'Bot: Updating the log',
		'it':'Bot: Aggiorno il log',
		'ja': u'ロボットによる:更新',
		'hu': 'Robot: A napló frissítése',
		'zh': u'機器人:更新記錄',
		}

# If a template isn't a license but it's included on a lot of images, that can be skipped to
# analise the image without taking care of it. (the template must be in a list)
# Warning: Don't add template like "en, de, it" because they are already in (added in the code, below
# Warning 2: The bot will use regex, make the names compatible, please (don't add "Template:" or {{
# because they are already put in the regex).
HiddenTemplate = {
		'commons':['information'],
		'en':['information'],
		'it':['edp', 'informazioni[ _]file', 'information'],
		'ja':[u'Information'],
		'hu':[u'információ','enwiki', 'azonnali'],
		'zh':[u'information'],
		}

# Add your project (in alphabetical order) if you want that the bot start
project_inserted = ['commons', 'en','ja','hu', 'it','zh']

# Ok, that's all. What is below, is the rest of code, now the code is fixed and it will run correctly in your project.
#########################################################################################################################
# <------------------------------------------- Change only above! ----------------------------------------------------> #
#########################################################################################################################

class LogIsFull(wikipedia.Error):
	"""An exception indicating that the log is full and the Bot cannot add other data to prevent Errors."""

class NothingFound(wikipedia.Error):
	""" An exception indicating that a regex has return [] instead of results."""

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
                        
# When the page is not a wiki-page (as for untagged generator) you need that function
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
		self.site = site
		self.logFulNumber = logFulNumber
	def general(self, newtext, image, notification, head, botolist):
		""" This class can be called for two reason. So I need two different __init__, one with common data
			and another with the data that I required... maybe it can be added on the other function, but in this way
			seems more clear what parameters I need
		"""
		self.newtext = newtext
		self.image = image
		self.head = head
		self.notification = notification
		self.botolist = botolist
	def put_mex(self, put = True):
		# Adding no source. - I'm sure that the image exists, double check... but another can't be useless.
		try:
                        testoa = p.get()
		except wikipedia.NoPage:
			wikipedia.output(u'%s has been deleted...' % p.title())
		if put:
			p.put(testoa + self.newtext, comment = commento, minorEdit = True)
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
			self.report_image(rep_page, self.image, com, repme)
			# We have a problem! Report and exit!         
			return False
		try:
			nick = paginetta.getFileVersionHistory()[-1][1]
		except IndexError:
			wikipedia.output(u"Seems that %s hasn't the image at all, but there is something in the description..." % self.image)
			repme = "\n*[[:Image:%s]] seems to have problems ('''no data found in the image''')"
			# We have a problem! Report and exit!
			self.report_image(rep_page, self.image, com, repme)
			return False
		luser = wikipedia.url2link(nick, self.site, self.site)
		pagina_discussione = "%s:%s" % (self.site.namespace(3), luser)
		# Defing the talk page (pagina_discussione = talk_page ^__^ )
		talk_page = wikipedia.Page(self.site, pagina_discussione)
		self.talk_page = talk_page
		return True
	# There is the function to put the advise in talk page.
	def put_talk(self, notification, head, notification2 = None, commx = None):
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
			testoattuale = talk_page.get()
			# Find out the list of Bots that add no source tags.
			lang = config.mylang
			# Standard language
			self.lang = lang
			project = config.family
			bot = config.usernames[project]
			botnick = bot[lang]
			botolist = self.botolist + [botnick]
			for i in botolist:
				if latest_user == i:
					second_text = True
					# A block to prevent the second message if the bot also welcomed users...
					if latest_edit == history[-1]:
						second_text = False
		else:
			second_text = False
			testoattuale = ti_es_ti
		if commx == None:
			commentox = commento2
		else:
			commentox = commx
		if second_text == True:
			talk_page.put("%s\n\n%s" % (testoattuale, notification2), comment = commentox, minorEdit = False)
		elif second_text == False:
			talk_page.put(testoattuale + head + notification, comment = commentox, minorEdit = False)
			
	def untaggedGenerator(self, untaggedProject, rep_page, com):
		lang = untaggedProject.split('.', 1)[0]
		project = '.%s' % untaggedProject.split('.', 1)[1]
		if lang == 'commons':
			link = 'http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php?wikifam=commons.wikimedia.org&since=-100d&until=&img_user_text=&order=img_timestamp&max=100&order=img_timestamp&format=html'
		else:
			link = 'http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php?wikilang=%s&wikifam=%s&order=img_timestamp&max=%s&ofs=0&max=%s' % (lang, project, limit, limit)         
		text = pageText(link)
		#print text
		regexp = r"""<td valign='top' title='Name'><a href='http://.*?\.org/w/index\.php\?title=(.*?)'>.*?</a></td>"""
		results = re.findall(regexp, text)
		if results == []:
                        print link
			raise NothingFound('Nothing found! Try to use the tool by yourself to be sure that it works!')
		else:
			for result in results:
                                wikiPage = wikipedia.Page(self.site, result)
				yield wikiPage
	
	def regexGenerator(self, regexp, textrun):
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

	def checkImage(self, image):
		# Search regular expression to find links like this (and the class attribute is optional too)
		# title="Immagine:Nvidia.jpg"
		wikipedia.output(u'Checking if %s is on commons...' % image)
		commons = wikipedia.getSite('commons', 'commons') 
		if wikipedia.Page(commons, u'Image:%s' % image).exists():
			wikipedia.output(u'%s is on commons!' % image)
			imagePage = wikipedia.ImagePage(self.site, 'Image:%s' % image)
			on_commons_text = imagePage.getImagePageHtml()
			if "<div class='sharedUploadNotice'>" in on_commons_text:
				wikipedia.output(u"But, the image doesn't exist on your project! Skip...")
				# Problems? Yes! We have to skip the check part for that image!
				# Because it's on commons but someone has added something on your project.
				return False
			elif 'stemma' in image.lower() and self.site.lang == 'it':
				wikipedia.output(u'%s has "stemma" inside, means that it\'s ok.' % image)
				return False
			else:            
				repme = "\n*[[:Image:%s]] is also on '''Commons''': [[commons:Image:%s]]"
				self.report_image(rep_page, image, com, repme)
				# Problems? No, return True
				return True
		else:
			# Problems? No, return True
			return True

	def report_image(self, rep_page, image, com, rep):
		another_page = wikipedia.Page(self.site, rep_page)
		
		if another_page.exists():      
			text_get = another_page.get()
		else:
			text_get = str()
		if len(text_get) >= self.logFulNumber:
                        raise LogIsFull("The log page (%s) is full! Please delete the old images reported." % another_page.title())  
		pos = 0
		# The talk page includes "_" between the two names, in this way i replace them to " "
		regex = image
		n = re.compile(regex, re.UNICODE)
		y = n.search(text_get, pos)
		if y == None:
			# Adding the log :)
			if "\'\'\'Commons\'\'\'" in rep:
				rep_text = rep % (image, image)
			else:
				rep_text = rep % image
			another_page.put(text_get + rep_text, comment = com, minorEdit = False)
			wikipedia.output(u"...Reported...")
			reported = True
		else:
			pos = y.end()
			wikipedia.output(u"%s is already in the report page." % image)
			reported = False
		return reported
	
	def takesettings(self, settings):
		pos = 0
		if settings == None: lista = None
		else:
                        x = wikipedia.Page(self.site, settings)
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
def report(newtext, image, notification, head, notification2 = None, unver = True, commx = None):
	global botolist
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
		try:
			run.put_talk(notification, head, notification2, commx)
		except wikipedia.EditConflict:
			wikipedia.output(u"Edit Conflict! Retrying...")
			try:
				run.put_talk(notification, head, notification2, commx)
			except:
				wikipedia.output(u"Another error... skipping the user..")
				break
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

        # In this way i find what language, project and what bot do you use.
        lang = config.mylang
        project = config.family
        
        # Block of text to translate the parameters set above.
        image_n = site.image_namespace()
        image_namespace = "%s:" % image_n # Example: "User_talk:"
        unvertext = wikipedia.translate(site, n_txt)
        commento = wikipedia.translate(site, comm)
        commento2 = wikipedia.translate(site, comm2)
        ti_es_ti = wikipedia.translate(site, empty)
        unverf = wikipedia.translate(site, unver)
        di = wikipedia.translate(site, delete_immediately)
        dih = wikipedia.translate(site, delete_immediately_head)
        din = wikipedia.translate(site, delete_immediately_notification)
        nh = wikipedia.translate(site, nothing_head)
        nn = wikipedia.translate(site, nothing_notification)
        dels = wikipedia.translate(site, del_comm)
        botolist = wikipedia.translate(site, bot_list)
        smwl = wikipedia.translate(site, second_message_without_license)
        settings = wikipedia.translate(site, page_with_settings)
        rep_page = wikipedia.translate(site, report_page)
        rep_text = wikipedia.translate(site, report_text)
        com = wikipedia.translate(site, comm10)
        TextFind = wikipedia.translate(site, txt_find)
        hiddentemplate = wikipedia.translate(site, HiddenTemplate)
        # A template as {{en is not a license! Adding also them in the whitelist template...
        for langK in wikipedia.Family('wikipedia').knownlanguages:
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
        notallowed = ("xcf", "xls", "sxw", "sxi", "sxc", "sxd", "djvu")

        # A little block-statement to ensure that the bot will not start with en-parameters
        if lang not in project_inserted:
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
                        generator =  mainClass.untaggedGenerator(projectUntagged, rep_page, com)
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
                        tupla_written = mainClass.takesettings(settings)
                except wikipedia.Error:
                        # Error? Settings = None
                        wikipedia.output(u'Problems with loading the settigs, run without them.')
                        tupla_written = None
                        some_problem = False
                # Ensure that if the list given is empty it will be converted to "None"
                # (but it should be already done in the takesettings() function)
                if tupla_written == []:
                        tupla_written = None
                if tupla_written != None:
                        wikipedia.output(u'\t   >> Loaded the real-time page... <<')
                        # Save the settings not to lose them (FixMe: Make that part better)
                        filename = "settings.data"
                        f = file(filename, 'w')
                        cPickle.dump(tupla_written, f)
                        f.close()
                else:
                        # No settings found, No problem, continue.
                        wikipedia.output(u'\t   >> No additional settings found! <<')
                for image in generator:
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
                        imageName = image.title().split(image_namespace)[1] # Deleting the namespace (useless here)
                        # Skip block
                        if skip == True:
                                # If the images to skip are more the images to check, make them the same number
                                if skip_number > limit: skip_number = limit
                                if skip_list == []:
                                        if skip_number == 1:
                                                wikipedia.output(u'Skipping the first image:\n')
                                        else:
                                                wikipedia.output(u'Skipping the first %s images:\n' % skip_number)
                                if len(skip_list) < skip_number:
                                        wikipedia.output(u'Skipping %s...' % imageName)
                                        skip_list.append(imageName)
                                        if skip_number == 1:
                                                wikipedia.output('')
                                                skip = False 
                                        continue
                                else:
                                        wikipedia.output('1\n')
                                        skip = False					                                               
                        elif skip_list == []:
                                wikipedia.output(u'\t\t>> No images to skip...<<')
                                skip_list.append('skip = Off') # Only to print it once
                        if commonsActive == True:
                                response = mainClass.checkImage(imageName)
                                if response == False:
                                        continue
                        if tupla_written != None:
                                f = file(filename)
                                tuplaList = cPickle.load(f)
                        parentesi = False
                        delete = False
                        tagged = False
                        extension = imageName.split('.')[-1]
                        # Page => ImagePage
                        p = wikipedia.ImagePage(site, image.title())
                        # Skip deleted images
                        try:
                                g = p.get()
                        except wikipedia.NoPage:
                                wikipedia.output(u"Skipping %s because it has been deleted." % imageName)
                                continue
                        except wikipedia.IsRedirectPage:
                                wikipedia.output(u"The file description for %s is a redirect?!" % imageName )
                                continue
                        for i in TextFind:
                                if i.lower() in g:
                                        tagged = True				
                        for l in hiddentemplate:
                                if tagged == False:
                                        res = re.findall(r'\{\{(?:[Tt]emplate:|)%s(?: \n|\||\n)' % l.lower(), g.lower())
                                        if res != []:
                                                #print res
                                                wikipedia.output(u'A white template found, skipping the template...')
                                                # I don't delete the template, because if there is something to change the image page
                                                # will be reloaded. I delete it only for the next check part.
                                                if l != '' and l != ' ':
                                                        g = g.lower().replace('{{%s' % l, '')
                        for a_word in something:
                                if a_word in g:
                                        parentesi = True
                        for parl in notallowed:
                                if parl.lower() in extension.lower():
                                        delete = True
                        some_problem = False
                        if tupla_written != None:                 
                                for tupla in tuplaList:
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
                                        del tupla[0:8]
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
                        if p.exists():
                                # Here begins the check block.
                                if tagged == True:
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
                                                reported = mainClass.report_image(rep_page, imageName, com, rep_text)
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
                                        if lang == 'commons':
                                                head = nh % imageName
                                                notification = nn
                                        else:
                                                notification = nn % imageName
                                                head = nh 
                                        report(unvertext, imageName, notification, head, smwl)
                                        continue
                                else:
                                        wikipedia.output(u"%s has only text and not the specific license..." % imageName)
                                        if lang == 'commons':
                                                head = nh % imageName
                                                notification = nn
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
                        break
                
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
		sys.exit() # Be sure that the Bot will stop
