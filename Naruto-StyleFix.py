#!/usr/bin/env python
# -*- coding: utf-8  -*-
import sys, re
import wikipedia, pagegenerators, catlib, config
from time import *

class NarutoStyleFixBot:
	generator = None
	wiki = None
	acceptall = False
	
	def __init__(self):
		self.wiki = self.coreWiki = wikipedia.getSite(code=u'en', fam=u'naruto')
		wikipedia.setAction(wikipedia.translate(self.wiki, self.getSummaries()))
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
			pages = [wikipedia.Page(self.wiki, PageTitle) for PageTitle in PageTitles]
			gen = iter(pages)
		
		self.generator = gen
	
	def getSummaries(self):
		self.msg = {
			'en': u'Naruto stylefix bot',
		}
		return self.msg
	
	def run(self):
		wikipedia.output(u'\03{lightblue}Starting Tag Sync Bot\03{default}')
		for page in self.generator:
			self.do_page(page)
			
	def do_page(self, page):
		wikipedia.output(u'\03{lightred}>\03{lightgreen}Starting with page [[%s]]\03{default}' % page.title())
		
		try:
			# Load the page's text from the wiki
			original_text = page.get(get_redirect=True)
			if not page.canBeEdited():
				wikipedia.output(u"You can't edit page [[%s]]" % page.title())
				return
		except wikipedia.NoPage:
			wikipedia.output(u'Page [[%s]] not found' % page.title())
			return
		
		new_text = self.do_replacements(original_text)
		
		if new_text == original_text:
			wikipedia.output(u'\03{lightred}>>\03{lightpurple}No changes were necessary in [[%s]]\03{default}' % page.title())
			return
		
		# Show the title of the page we're working on.
		# Highlight the title in purple.
		wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
		wikipedia.showDiff(original_text, new_text)
		
		choice = False
		if not self.acceptall:
			choice = wikipedia.inputChoice(
				u'Do you want to accept these changes?',
				['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
		if choice in ['a', 'A']:
			self.acceptall = True
		if self.acceptall or choice in ['y', 'Y']:
			try:
				page.put_async(new_text)
			except wikipedia.EditConflict:
				wikipedia.output(u'Skipping %s because of edit conflict' % (page.title(),))
			except wikipedia.SpamfilterError, e:
				wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
			except wikipedia.PageNotSaved, error:
				wikipedia.output(u'Error putting page: %s' % (error.args,))
			except wikipedia.LockedPage:
				wikipedia.output(u'Skipping %s (locked page)' % (page.title(),))
		
	def do_replacements(self, text):
		# Village no Sato
		text = replace(text, "(\w+) no [Ss]ato", "\\1")
		# [[First Last|First]]
		#text = replace(text, "\[\[(\w+) \w+\\|\\1\]\]", "[[\\1]]")
		#text = replace(text, "\[\[\w+ (\w+)\\|\\1\]\]", "[[\\1]]")
		# [[Tobi/Madara Uchiha]]
		text = replace(text, "\[\[Tobi\\|(Madara(?: Uchiha)?)\]\]", "[[\\1]]")
		text = replace(text, "\[\[(?:Madara(?: Uchiha)?)\\|(Tobi)\]\]", "[[\\1]]")
		# [[Name|Name's]]
		text = replace(text, "\[\[(.+?)\|\\1's\]\]", "[[\\1]]'s")
		# [[Name|Name]]
		text = replace(text, "\[\[(.+?)\|\\1\]\]", "[[\\1]]")
		# [[Nagato/Pain]]
		text = sub(text, "[[Nagato|Pain]]", "[[Pain]]")
		# Capitalized "Path" in path names
		for path in ["Deva", "Preta", "Animal", "Human", "Naraka", "Asura"]:
			text = sub(text, path.lower() + " path", path + " path")
		text = replace(text, "(Deva|Preta|Animal|Human|Naraka|Asura) Path", "\\1 path")
		# Old Nagato/Pain path section links
		text = replace(text, "\[\[([Nn]agato|[Pp]ain)#(Deva|Preta|Animal|Human|Naraka|Asura) path\|\\2 path\]\]", "[[\\2 path]]")
		# Things like [[Genjutsu|genjutsu]]
		text = replace(text, "\[\[([^\|\]]+)\|([^\|\]]+)\]\]", iname)
		# Shippūden
		text = replace(text, u'Shipp?(uu?|ū)den', u'Shippūden')
		
		return text

def iname(m):
	if m.group(1) != m.group(2) and m.group(1).lower() == m.group(2).lower():
		return "[[%s]]" % m.group(2)
	return m.group(0)

def sub(text, old, new):
	return text.replace(old, new)
def replace(text, old, new, flags=0):
	r = re.compile(old, re.UNICODE | flags)
	return r.sub(new, text)

def main():
	bot = NarutoStyleFixBot()
	bot.run()
	
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
