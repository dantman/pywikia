# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Graphical Entertainment Project to generate Sidebars and MediaWiki messages on project wiki.
Info: http://en.anime.wikia.com/wiki/Project:Bots/MessageBot
"""

import sys, re, copy
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'[[Anime:Project:Bots/MessageBot|MessageBot]].',
       }

def main():
	#Setup Familys for Wikia Involved
	anime = wikipedia.getSite(code=u'en', fam=u'anime')
	wikipedia.setAction(wikipedia.translate(anime, msg))
	siteList = [anime]
	
	#Get Project Wiki Listing
	wikiaIds = []
	page = wikipedia.Page(anime, u'Bots/Wiki', None, 4)#4=Project Namespace
	try:
		text = page.get()
		r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
		wikilist = re.split(r, text)
		r = re.compile(u'^#|^\s*$|^\[', re.UNICODE | re.MULTILINE | re.DOTALL)
		for wiki in wikilist:
			if not re.match(r, wiki):
				wikiaIds.append(wiki)
	except wikipedia.NoPage:
		return False
	
	for wiki in wikiaIds:
		siteList.append(wikipedia.getSite(code=u'en', fam=wiki))
	
	#Build Base Sidebar
	sidebarBaseKeys = []
	sidebarBaseItems = [];
	current = None
	sectionRE = re.compile(u'^\*', re.UNICODE | re.DOTALL)
	itemRE = re.compile(u'^\*\*', re.UNICODE | re.DOTALL)
	complexRE = re.compile(u'^(?P<mode>[-+])(?P<name>[^-+]+)(?P<rel>[-+])', re.UNICODE | re.DOTALL)
	contentRE = re.compile(u'^((?P<link>[^\|]*)\|)?(?P<text>.*?)$', re.UNICODE | re.DOTALL)
	page = wikipedia.Page(anime, u'Bots/MessageBot/Sidebar', None, 4)#4=Project Namespace
	try:
		text = page.get()
		r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
		lines = re.split(r, text)
		r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
		for line in lines:
			if not re.match(r, line):
				if re.match(itemRE, line):
					m = re.match(contentRE,re.sub(itemRE, u'', line))
					link = (m.group(u'link') or m.group(u'text')).strip(' 	_')
					text = m.group(u'text').strip(' 	_')
					sidebarBaseItems[current].append({ 'link': link, 'text': text })
				elif re.match(sectionRE, line):
					text = re.sub(sectionRE, u'', line).strip(' 	_')
					sidebarBaseKeys.append(text)
					current = sidebarBaseKeys.index(text)
					sidebarBaseItems.insert(current, [])
		wikipedia.output( u'Sidebar Base:\n%s' % genBar(sidebarBaseKeys, sidebarBaseItems))
	except wikipedia.NoPage:
		return False
	
	for site in siteList:
		current = None
		sidebarKeys = copy.deepcopy(sidebarBaseKeys)
		sidebarItems = copy.deepcopy(sidebarBaseItems)
		gendata = []
		page = wikipedia.Page(site, u'Sidebar/gen', None, 8)#8=MediaWiki Namespace
		try:
			text = page.get()
			r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
			text = re.sub(r, u'', text)
			r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
			text = re.sub(r, u'', text)
			r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
			genlist = re.split(r, text)
			r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
			for gen in genlist:
				if not re.match(r, gen):
					gendata.append(gen)
		except wikipedia.NoPage:
			gendata = []
		#Start Building
		for gen in gendata:
			if re.match(itemRE, gen):
				line = re.sub(itemRE, u'', gen)
				mode = u'!'
				name = None
				rel  = None
				id   = None
				if re.match(complexRE, line):
					c = re.match(complexRE, line)
					mode = c.group(u'mode')
					name = c.group(u'name').strip(' 	_')
					rel  = c.group(u'rel')
					for item in sidebarItems[current]:
						if item['text'] == name:
							id = sidebarItems[current].index(item)
							break
					else:
						id = None
					line = re.sub(complexRE, u'', line)
				m = re.match(contentRE,line)
				link = (m.group(u'link') or m.group(u'text')).strip(' 	_')
				text = m.group(u'text').strip(' 	_')
				if not id == None:
					if mode == '-':
						if rel == '+' and text != None:
							sidebarItems[current][id] = { 'link': link, 'text': text }
						else:
							sidebarItems[current].remove(id)
					elif mode == '+':
						pos = id + 1
						if rel == '-':
							pos-=1
						sidebarItems[current].insert(pos,{ 'link': link, 'text': text })
				else:
					for item in sidebarItems[current]:
						if item['text'] == text:
							item['link'] = link
							break
					else:
						sidebarItems[current].append({ 'link': link, 'text': text })
			elif re.match(sectionRE, gen):
				line = re.sub(sectionRE, u'', gen)
				mode = u'!'
				name = None
				rel  = None
				id   = None
				if re.match(complexRE, line):
					c = re.match(complexRE, line)
					mode = c.group(u'mode')
					name = c.group(u'name').strip(' 	_')
					rel  = c.group(u'rel')
					
					if name in sidebarKeys:
						id = sidebarKeys.index(name)
					line = re.sub(complexRE, u'', line)
				text = line.strip(' 	_')
				if not id == None:
					if mode == '-':
						if rel == '+' and text != None:
							sidebarKeys[id] = text
						else:
							sidebarKeys.remove(id)
							sidebarItems.remove(id)
					elif mode == '+':
						pos = id + 1
						if rel == '-':
							pos-=1
						sidebarKeys.insert(pos, text)
						sidebarItems.insert(pos, [])
				else:
					if not text in sidebarKeys:
						sidebarKeys.append(text)
						current = sidebarKeys.index(text)
						sidebarItems.insert(current, [])
				current = sidebarKeys.index(text)
		
		#Display
		wikipedia.output( u'Site: %s:\n%s' % (site.family.name,genBar(sidebarKeys, sidebarItems)))

def genBar(keys = [], items = []):
	text = u''
	for key in keys:
		text += u'* %s\n' % key
		for item in items[keys.index(key)]:
			text += u'** %s|%s\n' % (item['link'],item['text'])
	text.rstrip(u'\n')
	return text
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()