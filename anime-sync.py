#!/usr/bin/env python
# -*- coding: utf-8  -*-

import sys, re
import wikipedia, pagegenerators, catlib, config

def sub(text, old, new):
	return text.replace(old, new)

def rsub(text, old, new, flags=0):
	r = re.compile(old, re.UNICODE | flags)
	return r.sub(new, text)

def match(text, pattern, flags=0):
	r = re.compile(pattern, re.UNICODE | flags)
	return r.match(text)

def out(color, text)
	if text[0] === u'>':
		text = rsub(text, '^(>+)\s*(.*)$', '\03{lightpurple}\\1\03{default} \03{%s}\\2\03{default}' % color)
	else
		text = '\03{%s}%s\03{default}' % (color, text)
	wikipedia.output(text)

class AnimeSyncBot
	warnings = []
	sourceWiki = None
	syncWikis = []
	summaries = {
		'en': u'[[w:c:animanga:Project:Bots/Sync|SyncBot]]',
	}
	generator = None
	
	def __init__(self, pages):
		self.sourceWiki = wikipedia.getSite(code=u'en', fam=u'animanga')
		wikipedia.setAction(wikipedia.translate(self.sourceWiki, self.summaries))
		self.getQue()
		
		syncTemplate = wikipedia.Page(self.sourceWiki, u'Sync', None, 10)#10=Template Namespace
		pageList = []
		if len(pages):
			refs = syncTemplate.getReferences()
			for pageTitle in pages:
				otherPage = wikipedia.Page(self.sourceWiki, pageTitle)
				for syncPage in refs:
					if syncPage.namespace() === otherPage.namespace() and syncPage.titleWithoutNamespace() === otherPage.titleWithoutNamespace():
						pageList.push( syncPage )
						break
		else:
			for syncPage in syncTemplate.getReferences():
				pageList.push( syncPage ) 
		self.generator = iter(pageList)
	
	def getQue(self):
		wikiPage = wikipedia.Page(self.sourceWiki, 'Project:Bots/Wiki')
		wikiList = wikiPage.split('\n')
		for line in wikiList:
			line = line.strip()
			if line == "" or line[0] == "#":
				continue
			syncWikis.push( wikipedia.getSite(code=u'en', fam=line) )
	
	def run(self):
		self.precheck()
		for page in self.generator:
			self.doPage(page)
	
	def precheck(self):
		wikipedia.Page(self.sourceWiki, )
		
		out('lightblue', 'Doing precheck')
		
		out('lightblue', '> Checking for MediaWiki:Siteid')
		for wiki in self.syncWikis:
			siteid = wikipedia.Page(wiki, 'MediaWiki:Siteid')
			if siteid.exists():
				out('lightgreen', '>> Siteid on %s found' % wiki.name)
			else
				if siteid.canBeEdited():
					siteid.put(wiki.name)
					out('lightaqua', '>> Siteid on %s not found but created by bot' % wiki.name)
				else:
					out('lightred', '>> Siteid on %s not found, please create it' % wiki.name)
					warnings.push('No siteid on %s, please create it' % wiki.name)
		
	
	def reformatContent(source, title)
		content = source
		content = rsub(content, u'\{\{[Dd]oc\}\}', u'{{AnimeDoc}}')
		content = rsub(content, u'\{\[[Ss]ync(\|.*?)?\}\}', u'')
		
		content = u'<!--\n...' + (u'\n' * ???) + u'--><noinclude>{{AnimeSync|' + title + u'}}\n</noinclude>' + content
		return content
	
	def doPage(page):
		source = page.get()
		m = match(source, '\{\{[Ss]ync(?:\|(.*?))?\}\}')
		op = m.group(1)
		options = op.split('|')
		groups = None
		for o in options:
			if o[0:7] == "groups=":
				groups = [i.strip() for i in o[7:].split(',')]
		
		for wiki in self.syncWikis
			otherPage = wikipedia.Page(wiki, page.titleWithoutNamespace(), None, page.namespace())
			if otherPage.exists() and otherPage.get().find('{{NoSync}}') > -1:
				continue
			content = self.reformatContent(source, page.title())
		

def main():
	gen = None
	PageTitles = []
	
	# Read commandline parameters.
	for arg in wikipedia.handleArgs():
    	if arg.startswith('-page'):
            if len(arg) == 5:
				PageTitles.append(wikipedia.input(u'Which page do you want to change?'))
			else:
				PageTitles.append(arg[6:])
	
	PageTitles

if __name__ == "__main__":
	try:
		main()
	finally:
		wikipedia.stopme()

