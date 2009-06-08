#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
This bot is used to Export pages from Wikipedia, alter them, then Import them to another wiki.
Info: http://en.anime.wikia.com/wiki/Project:Bots/ExportImport
"""

import sys, re
import wikipedia, pagegenerators, catlib, config
from time import *
import xml
import xml.dom.minidom as minidom
from xml.dom.minidom import Node

class GEExport:
	def __init__(self, pageGenerator):
		self.pageGenerator = pageGenerator
		
	def exportPage(self, page):
		response = None
		data = None
		wp = wikipedia.getSite(code=u'en', fam=u'wikipedia')
		address = wp.export_address()
		title = page.sectionFreeTitle().encode(wp.encoding())
		predata = {
			'action': 'submit',
			'pages': title,
			'offset': '1',
		}
		#if True is True:#Future Loop marker
		while True:
			wikipedia.get_throttle()
			wikipedia.output('\03{lightpurple}>>\03{default} \03{lightaqua}Exporting revisions.\03{default}')
			# Now make the actual request to the server
			now = time()
			if wp.hostname() in config.authenticate.keys():
				predata["Content-type"] = "application/x-www-form-urlencoded"
				predata["User-agent"] = wikipedia.useragent
				data = wp.urlEncode(predata)
				response = urllib2.urlopen(urllib2.Request(wp.protocol() + '://' + wp.hostname() + address, data))
				data = response.read()
			else:
				response, data = wp.postForm(address, predata)
			data = data.encode(wp.encoding())
			wikipedia.get_throttle.setDelay(time() - now)
			
			doc = minidom.parseString(data)
			revs = doc.getElementsByTagName('revision')
			revCount = len(revs)
			if revCount > 0:
				lastRev = revs[len(revs)-1].getElementsByTagName('timestamp')[0]
				timestamp = ''
				for nodes in lastRev.childNodes:
					if nodes.nodeType == Node.TEXT_NODE:
						timestamp += nodes.data
				wikipedia.output('\03{lightpurple}>>\03{default} \03{lightaqua}Got %s revisions up to %s.\03{default}' % (revCount,timestamp))
				fileName = 'wpdumps/%s-%s.xml' % (title.replace('/','-'),predata['offset'].replace(':','-'))
				wikipedia.output('\03{lightpurple}>>\03{default} \03{lightblue}Saving to %s.\03{default}' % fileName)
				f = open(fileName, 'w')
				f.write(data)
				f.close()
				predata['offset'] = timestamp
			else:
				wikipedia.output('\03{lightpurple}>>\03{default} \03{lightaqua}Returned no revisions, exporting for this page is complete.\03{default}')
				break
		
	def run(self):
        
		wikipedia.output(u'\03{lightblue}Running Export bot.\03{default}')
		for page in self.pageGenerator:
			wikipedia.output('\03{lightpurple}>\03{default} \03{lightaqua}Doing \03{lightpurple}%s\03{default}' % page.aslink())
			self.exportPage(page)
	
class GEImport:
	def run(self):
		wikipedia.output(u'\03{lightblue}Running Import bot.\03{default}')
	
def main():
	bot = None
	action = None
	
	# This factory is responsible for processing command line arguments
	# that are also used by other scripts and that determine on which pages
	# to work on.
	genFactory = pagegenerators.GeneratorFactory()
	gen = None
	
	for arg in wikipedia.handleArgs():
		if action == None:
			action = arg
		else:
			generator = genFactory.handleArg(arg)
			if generator:
				gen = generator
	
	if action == 'export':
		if gen == None:
			wikipedia.output(u'\03{lightred}Export bot needs a page generator to itterate over.\03{default}')
			return
		bot = GEExport(gen)
	elif action == 'import':
		bot = GEImport()
	if bot == None:
		wikipedia.output(u'\03{lightred}Invalid bot action to run.\03{default}')
		return
	bot.run()
	
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()