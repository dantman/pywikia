# -*- coding: utf-8  -*-
"""
This bot is used by Dantman to mirror his userpages across wikia.
"""

import sys, re
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'Automatic Bot Userpage Cloning',
       }

def main():
	#Setup Familys for Wikia Involved
	anime = wikipedia.getSite(code=u'en', fam=u'anime')
	wikipedia.setAction(wikipedia.translate(anime, msg))
	siteList = []
	pageList = [u'User:Dantman']
	killList = []
	
	#Page Listing
	page = wikipedia.Page(anime, u'Dantman/UserClone/Pages', None, 2)#2=User Namespace
	try:
		text = page.get()
		r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
		pagelist = re.split(r, text)
		r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
		for p in pagelist:
			if not re.match(r, p):
				if p.startswith('-'):
					killList.append(u'User:Dantman/%s' % p[1:])
				else:
					pageList.append(u'User:Dantman/%s' % p)
	except wikipedia.NoPage:
		return False;

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
		return False;
	page = wikipedia.Page(anime, u'Dantman/UserClone/Wiki', None, 2)#2=User Namespace
	try:
		text = page.get()
		r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
		wikilist = re.split(r, text)
		r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
		for wiki in wikilist:
			if not re.match(r, wiki):
				wikiaIds.append(wiki)
	except wikipedia.NoPage:
		return False;
	
	for wiki in wikiaIds:
		siteList.append(wikipedia.getSite(code=u'en', fam=wiki))
	
	for page in pageList:
		wikipedia.output(u'Doing Page %s' % page)
		pagePage = wikipedia.Page(anime, page)
		pageSource = pagePage.get()
		
		for site in siteList:
			sitePage = wikipedia.Page(site, page)
			siteSource = u''
			try:
				siteSource = sitePage.get()
			except wikipedia.NoPage:
				wikipedia.output(u'Site %s has no %s page, creating it' % (site, page))
			if siteSource != pageSource:
				wikipedia.output(u'Site \'%s\' page status: Needs Updating' % site)
				wikipedia.output(u'Updating page on %s' % site)
				sitePage.put(pageSource)
			else:
				wikipedia.output(u'Site \'%s\' page status: Ok' % site)
	
	for page in killList:
		wikipedia.output(u'Killing Page %s' % page)
		for site in siteList:
			sitePage = wikipedia.Page(site, page)
			if site.fam().name in ['central','wikia']:
				continue
			if not sitePage.exists():
				continue
			try:
				sitePage.delete(reason=msg['en'],prompt=False)
			except wikipedia.NoUsername:
				wikipedia.output(u'Not a sysop on %s cannot delete %s' % (site, page))
		

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()