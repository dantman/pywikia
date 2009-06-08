# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Graphical Entertainment Project to keep templates standard across the wikia in the project.
Info: http://en.anime.wikia.com/wiki/Project:Bots/AutoTemplate
"""

import sys, re
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'[[Anime:Project:Bots/AutoTemplate|AutoTemplateBot]].',
       }

def main():
	#Setup Familys for Wikia Involved
	anime = wikipedia.getSite(code=u'en', fam=u'anime')
	wikipedia.setAction(wikipedia.translate(anime, msg))
	siteList = []
	templateList = []
	
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
	
	#Get Template List
	page = wikipedia.Page(anime, u'Bots/AutoTemplate/Templates', None, 4)#4=Project Namespace
	try:
		text = page.get()
		r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
		text = re.sub(r, u'', text)
		r = re.compile(u'\n', re.UNICODE | re.MULTILINE | re.DOTALL)
		templates = re.split(r, text)
		r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
		for template in templates:
			if not re.match(r, template ):
				templateList.append(template)
	except wikipedia.NoPage:
		return False
	
	#Mirror the Templates category and all subcategorys to all the wiki.
	TemplateCategorys = []
	cat = catlib.Category(anime, u'Category:Templates')
	TemplateCategorys.append(cat)

	catlist = cat.subcategories(True)

	starts = re.compile(u'^Category:Templates', re.UNICODE | re.DOTALL)
	for category in catlist:
		if re.match(starts, category.title()):
			TemplateCategorys.append(category)

	for category in TemplateCategorys:
		categorySource = u'{{networkMirror|%s|anime|category}}\n%s' % (category.title(),category.get())

		if categorySource != u'':
			for site in siteList:
				siteCategory = catlib.Category(site, category.title())
				siteSource = u''
				try:
					siteSource = siteCategory.get()
				except wikipedia.NoPage:
					wikipedia.output(u'Site %s has no %s category, creating it' % (site, category.title()))
				if siteSource != categorySource:
					wikipedia.output(u'Site \'%s\' category status: Needs Updating' % site)
					wikipedia.output(u'Updating category on %s' % site)
					siteCategory.put(categorySource)
				else:
					wikipedia.output(u'Site \'%s\' category status: Ok' % site)
		else:
			wikipedia.output(u'Category %s is blank, skipping category' % category.title())
	
	for template in templateList:
		wikipedia.output(u'Doing Template %s' % template)
		templatePage = wikipedia.Page(anime, template, None, 10)#10=Template Namespace
		templateSource = u''
		if template == u'AutoTemplate':
			templateSource = templatePage.get()
		else:
			templateSource = u'<noinclude>{{AutoTemplate}}\n</noinclude>%s' % templatePage.get()

		if templateSource != u'':
			for site in siteList:
				sitePage = wikipedia.Page(site, template, None, 10)#10=Template Namespace
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
		else:
			wikipedia.output(u'Template %s is blank, skipping template' % template)


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()