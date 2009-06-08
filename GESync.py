# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Graphical Entertainment Project as a base for the bots it uses to sync pages in the project.
Info: http://en.anime.wikia.com/wiki/Project:Bots
"""

import sys, re
import wikipedia, pagegenerators, catlib, config
from time import *

class GESyncBot:
	logPage = None
	coreWiki = None
	siteList = None
	logHeaderSet = False
	
	groupList = None
	groupAliasList = None
	
	def __init__(self):
		self.header = u'=='+__name__+'-'+strftime(u'%Y-%m-%d@%H:%M:%S (%Z)',gmtime())+u'=='
		self.coreWiki = wikipedia.getSite(code=u'en', fam=u'anime')
		self.logPage = wikipedia.Page(self.coreWiki, u'Bots/DefaultLog', None, 4)#4=Project Namespace
		wikipedia.setAction(wikipedia.translate(self.coreWiki, self.getSummaries()))
	
	def getSummaries(self):
		self.msg = {
			'en': u'[[w:c:Anime:Project:Bots|Bot]].',
		}
		return self.msg
	
	def doSyncBotCmds(self):
		self.groupAliasList = {}
		try:
			cmdPage = wikipedia.Page(site, u'Sync cmds', None, 8)#8=MediaWiki Namespace
			for cmdLine in [cmd.strip() for cmd in cmdPage.get().split('\n')]:
				if cmdLine.startswith('#') or cmdLine == '':
					continue
				cmd = cmdLine
				sub = ''
				if ' ' in cmdLine:
					cmd,sub = cmdLine.split(' ', 2)
				
				if cmd == 'ALIAS':
					type = sub
					if ' ' in sub:
						type,sub = sub.split(' ', 2)
					
					if type == 'GROUP' or type == 'GROUPS':
						if not ' TO ' in sub:
							self.log('Subcommand \'\'TO\'\' not found in ALIAS line "%s".' % cmdLine)
							continue
						alias,to = sub.split(' TO ', 2)
						for t in [t.strip() for t in to.split(',')]:
							self.groupAliasList[t] = [f.strip() for f in alias.split(',')]
								
					else:
						self.log('Unknown alias type "\'\'%s\'\'" found in ALIAS command.' % type)
						
				else:
					self.log('Unknown command "\'\'%s\'\'" found in [[MediaWiki:Sync cmds|]].' % cmd)
					continue
				
		except wikipedia.NoPage:
			pass
		
	def run(self):
		# Please overload this function with the running code.
		self.abort('This bot has not overloaded the run function.')
		
	def setLogHeader(self):
		if self.logHeaderSet:
			return
		text = None
		try:
			text = self.logPage.get(force=True)
		except wikipedia.NoPage:
			text = u''
		text += u'\n\n'+self.header+u'\n'
		self.logPage.put(text)
		
		self.logHeaderSet = True
		
	def log(self, msg = u''):
		self.setLogHeader()
		text = None
		try:
			text = self.logPage.get(force=True)
		except wikipedia.NoPage:
			print "ERROR: No log page found."
			wikipedia.stopme()
			exit(1)
		loc = text.find(self.header)
		if loc == -1:
			print "ERROR: No header found on log page."
			wikipedia.stopme()
			exit(1)
		loc += len(self.header)+1
		log = '\n'+strftime(u'%H:%M:%S - ')+msg+u'<br />'
		text = text[0:loc] + log + text[loc:]
		print "logging: "+log[1:len(log)]
		self.logPage.put(text)
		
	def abort(self, status = u'Ok', msg = None):
		log = u'Bot aborted with status: '+status
		if msg:
			log += u' and message: '+msg
		self.log(log)
		wikipedia.stopme()
		exit(1)
		
	def getSiteSections(self):
		self.getSiteList()
		return self.siteList.keys()
		
	def getSiteList(self, sections = '*', withCore = False, asText = False):
		if not self.siteList:
			self.siteList = {}
			wikiPage = wikipedia.Page(self.coreWiki, u'Bots/Wiki', None, 4)#4=Project Namespace
			try:
				textList = wikiPage.get()
				extractRE = re.compile(u'^.*<!-- \|\|START\|\| -->\n?(?P<list>.*?)\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
				m = extractRE.match(textList)
				if m:
					section = 'top'
					if not 'top' in self.siteList:
						self.siteList['top'] = []
					for wikiId in [id.strip() for id in m.group('list').split('\n')]:
						if wikiId[0] == '#' or wikiId == '' or wikiId[0] == 'anime':
							continue
						if wikiId[0] == '[':
							section = wikiId.strip('[]')
							if not section in self.siteList:
								self.siteList[section] = []
							continue
						self.siteList[section].append(wikipedia.getSite(code=u'en', fam=wikiId))
						
			except wikipedia.NoPage:
				pass
		
		returnList = []
		for name in self.siteList:
			if sections == '*' or name == sections or name in sections:
				returnList.extend(self.siteList[name])
				
		if withCore:
			returnList[0:0] = [self.coreWiki]
		if asText:
			return [site.fam().name for site in returnList]
		return returnList
		
	def getMainWiki(self):
		sl = self.getSiteList(withCore=True)
		return sl[0]
		
	def getSyncGroups(self, wiki):
		if not self.groupList:
			self.groupList = {}
			for site in self.getSiteList():
				self.groupList[site.fam().name] = []
				groupPage = wikipedia.Page(site, u'Sync groups', None, 8)#8=MediaWiki Namespace
				try:
					self.groupList[site.fam().name] = [group.strip() for group in groupPage.get().split(' ')]
				except wikipedia.NoPage:
					continue
		return self.groupList[wiki]