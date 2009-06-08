# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Anime Project to keep templates standard across the wikia in the project.
Info: http://en.anime.wikia.com/wiki/Project:Bots/AutoTemplate
"""

import sys, sre, re
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'[[Anime:Project:Bots/AutoTemplate|AutoTemplateBot]].',
       }

def main():
	#Setup Familys for Wikia Involved
	anime = wikipedia.getSite(code=u'en', fam=u'anime')
	wikipedia.setAction(wikipedia.translate(anime, msg))
	siteList = []
	
	#Get Project Wiki Listing
	wikiaIds = []
	page = wikipedia.Page(anime, u'Bots/Wiki', None, None, 4)#4=Project Namespace
	try:
		text = page.get()
		r = sre.compile(u'^.*<!-- \|\|START\|\| -->\n?', sre.UNICODE | sre.DOTALL)
		text = sre.sub(r, u'', text)
		r = sre.compile(u'\n?<!-- \|\|END\|\| -->.*$', sre.UNICODE | sre.DOTALL)
		text = sre.sub(r, u'', text)
		r = sre.compile(u'\n', sre.UNICODE | sre.MULTILINE | sre.DOTALL)
		wikilist = sre.split(r, text)
		for wiki in wikilist:
			if wiki != u'':
				wikiaIds.append(wiki)
	except wikipedia.NoPage:
		moreYears = False
	
	for wiki in wikiaIds:
		siteList.append(wikipedia.getSite(code=u'en', fam=wiki))
	
	commonstart = u'@import "http://en.anime.wikia.com/index.php?title=MediaWiki:Anime-Common.css&action=raw&ctype=text/css";'
	monobookstart = u'@import "http://en.anime.wikia.com/index.php?title=MediaWiki:Anime-Monobook.css&action=raw&ctype=text/css";'
	
	for site in siteList:
		common = wikipedia.Page(site, u'Common.css', None, None, 8)#8=MediaWiki Namespace
		monobook = wikipedia.Page(site, u'Monobook.css', None, None, 8)#8=MediaWiki Namespace

				siteSource = u''
				try:
					siteSource = sitePage.get()
				except wikipedia.NoPage:
					wikipedia.output(u'Site %s has no %s template, creating it' % (site, template))
				if siteSource != templateSource:
					wikipedia.output(u'Site \'%s\' template status: Needs Updating' % site)
					wikipedia.output(u'Updating template on %s' % site)
					sitePage.put(templateSource)
				else:
					wikipedia.output(u'Site \'%s\' template status: Ok' % site)
	
	for template in templateList:
		wikipedia.output(u'Doing Template %s' % template)
		templatePage = wikipedia.Page(anime, template, None, None, 10)#10=Template Namespace
		templateSource = u''
		if template == u'AutoTemplate':
			templateSource = templatePage.get()
		else:
			templateSource = u'<noinclude>{{AutoTemplate}}</noinclude>%s' % templatePage.get()

		if templateSource != u'':
		else:
			wikipedia.output(u'Template %s is blank, skipping template' % template)


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()