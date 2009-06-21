#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Graphical Entertainment Project to keep things synced across the wikia in the project.
Info: http://en.anime.wikia.com/wiki/Project:Bots/TagSync
"""

from GESync import *

msg = {
		'en': u'[[Anime:Project:Bots/TagSync|TagSyncBot]].',
    }

class GETagSyncBot(GESyncBot):
	generator = None
	
	def __init__(self):
		GESyncBot.__init__(self)
		self.header = u'=='+__name__+'-'+strftime(u'%Y-%m-%d@%H:%M:%S (%Z)',gmtime())+u'=='
		
		# This factory is responsible for processing command line arguments
		# that are also used by other scripts and that determine on which pages
		# to work on.
		genFactory = pagegenerators.GeneratorFactory()
		gen = None
		PageTitles = []
		for arg in wikipedia.handleArgs():
			if arg.startswith('-page'):
				if len(arg) == 5:
					PageTitles.append(wikipedia.input(u'\03{lightblue}Which page do you want to chage?\03{default}'))
				elif len(arg) > 6:
					PageTitles.append(arg[6:])
			else:
				generator = genFactory.handleArg(arg)
				if generator:
					gen = generator
		if not gen and PageTitles:
			pages = [wikipedia.Page(self.getMainWiki(), PageTitle) for PageTitle in PageTitles]
			gen = iter(pages)
		
		self.generator = gen
	
	def getSummaries(self):
		self.msg = {
			'en': u'[[Anime:Project:Bots/TagSync|TagSyncBot]].',
		}
		return self.msg
	
	def run(self):
		wikipedia.output(u'\03{lightblue}Starting Tag Sync Bot\03{default}')
		syncTemplate = wikipedia.Page(self.getMainWiki(), u'TagSync', None, 10)#10=Template Namespace
		if self.generator:
			self.generator = [page.title() for page in self.generator]
		for syncPage in syncTemplate.getReferences():
			if self.generator and not syncPage.title() in self.generator:
				continue
			siteSyncList = []
			wikipedia.output(u'\03{lightpurple}>\03{default} \03{lightaqua}Doing \03{lightpurple}%s\03{default}' % syncPage.aslink())
			try:
				r = re.compile(u'{{[Tt]agSync\|(?P<params>.*?)}}', re.UNICODE | re.DOTALL)
				pageText = syncPage.get(force=True,get_redirect=True)
				m = r.search(pageText)
				if not m:
					wikipedia.output(u'\03{lightpurple}>>\03{default} \03{lightyellow}Skipping page, no visible template inclusion.\03{default}')
					continue
				params = m.group('params').split('|')
				for param in params:
					if '=' in param or not ':' in param:
						continue
					key,val = [i.strip() for i in param.split(':', 2)]
					key = key.lower()
					if key == 'include':
						for tag in [v.strip() for v in val.split(',')]:
							if tag == '*' or tag in self.getSiteSections():
								siteSyncList.extend(self.getSiteList(sections=tag))
							elif tag.startswith('group-'):
								for site in self.getSiteList():
									if tag[6:] in self.getSyncGroups(site.fam().name):
										siteSyncList.append(site)
							else:
								for site in self.getSiteList():
									if tag == site.fam().name:
										siteSyncList.append(site)
					elif key == 'exclude':
						for tag in [v.strip() for v in val.split(',')]:
							if tag == '*':
								siteSyncList = []
							elif tag in self.getSiteSections():
								for site in self.getSiteList(sections=tag):
									while site in siteSyncList:
										siteSyncList.remove(site)
							elif tag.startswith('group-'):
								for site in self.getSiteList():
									if tag[6:] in self.getSyncGroups(site.fam().name):
										siteSyncList.remove(site)
							elif tag in self.getSiteList(asText=True):
								for site in self.getSiteList():
									if tag == site.fam().name:
										while site in siteSyncList:
											siteSyncList.remove(site)
					
					
				self.doPageSync(syncPage, siteSyncList)
			except wikipedia.NoPage:
				continue
			
	def doPageSync(self, syncPage, siteSyncList):
		syncText = ''
		try:
			pageText = syncPage.get(force=True)
			syncText = u'<noinclude>{{TagSyncPage}}\n</noinclude>'+pageText
		except wikipedia.IsRedirectPage:
			pageText = syncPage.get(force=True,get_redirect=True)
			syncText = pageText+u'<noinclude>\n{{TagSyncPage}}</noinclude>'
		except wikipedia.NoPage:
			return
		wikipedia.output(u'\03{lightpurple}>>\03{default} \03{lightaqua}Syncing page to %s.\03{default}' % ', '.join([site.fam().name for site in siteSyncList]))
		# Create page to sync as
		for site in siteSyncList:
			wikipedia.output(u'\03{lightpurple}>>\03{default} \03{lightaqua}Syncing on %s.\03{default}' % site.fam().name)
			localPage  = wikipedia.Page(site, syncPage.titleWithoutNamespace(), None, syncPage.namespace())
			doSync = False
			try:
				localText = localPage.get(get_redirect=True)
				if localText != syncText:
					wikipedia.output(u'\03{lightpurple}>>>\03{default} \03{lightred}%s does not match %s.\03{default}' % (localPage.aslink(forceInterwiki=True),syncPage.aslink()))
					doSync = True
			except wikipedia.NoPage:
				wikipedia.output(u'\03{lightpurple}>>>\03{default} \03{lightred}%s does not exist.\03{default}' % localPage.aslink(forceInterwiki=True))
				doSync = True
			if not doSync:
				wikipedia.output(u'\03{lightpurple}>>>\03{default} \03{lightgreen}%s is ok, moving to next wiki.\03{default}' % localPage.aslink(forceInterwiki=True))
				continue
			
			wikipedia.output(u'\03{lightpurple}>>>\03{default} \03{lightblue}Syncing %s to %s.\03{default}' % (syncPage.aslink(),localPage.aslink(forceInterwiki=True)))
			localPage.put(syncText)
			
def main():
	bot = GETagSyncBot()
	bot.run()
	
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
