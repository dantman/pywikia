# -*- coding: utf-8  -*-
"""
This bot is used by the Narutopedia to format jutsu lists.
Info: http://en.anime.wikia.com/wiki/Project:Bots/Narutopedia/JutsuFormat
"""

import sys, re
import wikipedia, pagegenerators, catlib, config

msg = {
		'en':u'[[Anime:Project:Bots/Narutopedia/JutsuFormat|NarutopediaJutsuFormatBot]].',
		}

class JutsuBot:
	def __init__(self):
		#Setup Familys for Wikia Involved
		self.naruto = wikipedia.getSite(code=u'en', fam=u'naruto')
		wikipedia.setAction(wikipedia.translate(self.naruto, msg))
		self.jutsuList = [u'List of Ninjutsu', u'List of Taijutsu', u'List of Genjutsu']
	
	def run(self):
		for jutsuPage in self.jutsuList:
			self.do_jutsuPage(jutsuPage)

	def do_jutsuPage(self, jutsuPage):
		page = wikipedia.Page(self.naruto, u'%s/list' % jutsuPage)
		jutsuList = []
		jutsus = []
		try:
			text = page.get()
			r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
			text = re.sub(r, u'', text)
			r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
			text = re.sub(r, u'', text)
			r = re.compile(u'\n', re.UNICODE | re.DOTALL)
			jutsulines = re.split(r, text)
			r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
			for jutsu in jutsulines:
				if not re.match(r, jutsu):
					jutsuList.append(jutsu)
		except wikipedia.NoPage:
			return False
		pageFormat = None
		page = wikipedia.Page(self.naruto, u'%s/format' % jutsuPage)
		try:
			pageFormat = page.get()
		except wikipedia.NoPage:
			return False
		
		headBlock = None
		itemBlock = None
		
		r = re.compile(u'<block head>(?P<block>.*?)</block>', re.UNICODE | re.DOTALL)
		m = r.search(pageFormat)
		try:
			headBlock = m.group('block')
		except AttributeError:
			wikipedia.output(pageFormat)
			wikipedia.output(u'Getting Head Block Failed')
			return False
		pageFormat = re.sub(r, u'', pageFormat)
		
		r = re.compile(u'<block item>(?P<block>.*?)</block>', re.UNICODE | re.DOTALL)
		m = r.search(pageFormat)
		try:
			itemBlock = m.group('block')
		except AttributeError:
			wikipedia.output(pageFormat)
			wikipedia.output(u'Getting Head Block Failed')
			return False
		pageFormat = re.sub(r, u'', pageFormat)
		
		for jutsu in jutsuList:
			eng = None
			jap = None
			rom = None
			r = re.compile(u'^(?P<eng>[^\|]*?)(\|(?P<jap>[^\|]*?)(\|(?P<rom>.*?))?)?$', re.UNICODE | re.DOTALL)
			m = r.search(jutsu)
			try:
				eng = m.group('eng')
			except AttributeError:
				eng = u''
			try:
				jap = m.group('jap')
			except AttributeError:
				jap = u''
			try:
				rom = m.group('rom')
			except AttributeError:
				rom = u''
			jutsus.append({'eng': eng, 'jap': jap, 'rom': rom})
		
		jutsus.sort(key=self.getKey)
		let = u''
		listContent = u''
		empty = re.compile(u'^[ 	]*$')
		for jutsu in jutsus:
			
			thisLet = jutsu['eng'][0].upper()
			
			if thisLet != let:
				let = thisLet
				r = re.compile(u'<head>', re.UNICODE | re.DOTALL)
				listContent += re.sub(r, let, headBlock)
			
			item = itemBlock
			
			r = re.compile(u'<eng>', re.UNICODE | re.DOTALL)
			t = re.compile(u'<if eng>(.*?)</if>', re.UNICODE | re.DOTALL)
			f = re.compile(u'<ifnot eng>(.*?)</ifnot>', re.UNICODE | re.DOTALL)
			item = re.sub(r, jutsu['eng'], item)
			if not empty.match(jutsu['eng']):
				item = re.sub(t, u'\\1', item)
				item = re.sub(f, u'', item)
			else:
				item = re.sub(t, u'', item)
				item = re.sub(f, u'\\1', item)
			
			r = re.compile(u'<jap>', re.UNICODE | re.DOTALL)
			t = re.compile(u'<if jap>(.*?)</if>', re.UNICODE | re.DOTALL)
			f = re.compile(u'<ifnot jap>(.*?)</ifnot>', re.UNICODE | re.DOTALL)
			item = re.sub(r, jutsu['jap'], item)
			if not empty.match(jutsu['jap']):
				item = re.sub(t, u'\\1', item)
				item = re.sub(f, u'', item)
			else:
				item = re.sub(t, u'', item)
				item = re.sub(f, u'\\1', item)
			
			r = re.compile(u'<rom>', re.UNICODE | re.DOTALL)
			t = re.compile(u'<if rom>(.*?)</if>', re.UNICODE | re.DOTALL)
			f = re.compile(u'<ifnot rom>(.*?)</ifnot>', re.UNICODE | re.DOTALL)
			item = re.sub(r, jutsu['rom'], item)
			if not empty.match(jutsu['rom']):
				item = re.sub(t, u'\\1', item)
				item = re.sub(f, u'', item)
			else:
				item = re.sub(t, u'', item)
				item = re.sub(f, u'\\1', item)
			
			listContent += item
		
		r = re.compile(u'<strip nowiki>(?P<block>.*?)</strip>', re.UNICODE | re.DOTALL)
		pageContent = re.sub(r, self.strip_nowiki, pageFormat)
		
		r = re.compile(u'<pagewarning>', re.UNICODE | re.DOTALL)
		pageContent = re.sub(r, u'<!-- Please do not edit this page. This page is dynamicly created by Bot Please edit the [[/list]] subpage instead. -->', pageContent)
		
		r = re.compile(u'<list>', re.UNICODE | re.DOTALL)
		pageContent = re.sub(r, listContent, pageContent)
		
		page = wikipedia.Page(self.naruto, jutsuPage)
		page.put(pageContent)
		
	def getKey(self, item):
		return item['eng']
		
	def strip_nowiki(self, match):
		r = re.compile(u'</?nowiki>', re.UNICODE | re.DOTALL)
		return re.sub(r, u'', match.group('block'))
	
if __name__ == "__main__":
	try:
		  bot = JutsuBot()
		  bot.run()
	finally:
		wikipedia.stopme()
