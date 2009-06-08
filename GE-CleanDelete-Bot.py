# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Graphical Entertainment Project to delete old pages which used to be shared.
Info: http://en.anime.wikia.com/wiki/Project:Bots/CleanDelete
"""

import sys, re
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'[[Anime:Project:Bots/CleanDelete|CleanDeleteBot]].',
       }

def main():
	#Setup Familys for Wikia Involved
	anime = wikipedia.getSite(code=u'en', fam=u'anime')
	wikipedia.setAction(wikipedia.translate(anime, msg))
	siteList = []
	pageList = []
	
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
		moreYears = False
	
	
	for wiki in wikiaIds:
		siteList.append(wikipedia.getSite(code=u'en', fam=wiki))
	
	#Get Page List
	page = wikipedia.Page(anime, u'Bots/CleanDelete/Pages', None, 4)#4=Project Namespace
	try:
		text = page.get()
		r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
		pages = re.split(r, text)
		r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
		for p in pages:
			if not re.match(r, p ):
				pageList.append(p)
	except wikipedia.NoPage:
		moreYears = False
	
	for page in pageList:
		wikipedia.output(u'Doing Page %s' % page)
		for site in siteList:
			p = wikipedia.Page(site, page)
			if p.exists():
				wikipedia.output(u'Page %s exists on %s.' % (p.title(),site.family.name))
				wikipedia.output(u'Deleting %s' % p.title())
				p.delete(wikipedia.translate(anime, msg), True);
			else:
				wikipedia.output(u'Page %s does not exist on %s, skipping page on site.' % (p.title(),site.family.name))

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()