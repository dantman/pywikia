""" This tool sets an email address on all bot accounts.
In the future it will also auto-confirm them."""

import sys, os, getpass
sys.path.append('..')

import poplib
import wikipedia, config

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint 
class FormParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_form = False
		self.data = {}
		self.select = None
	
	def handle_entityref(self, name):
		if name in name2codepoint: 
			self.handle_data(unichr(name2codepoint[name]))
		else:
			self.handle_data(u'&%s;' % name)
	def handle_charref(self, name):
		try:
			self.handle_data(unichr(int(name)))
		except ValueError:
			self.handle_data(u'&#$s;' % name)
	def handle_starttag(self, tag, attrs):
		if tag == 'form': 
			self.in_form = ('method', 'post') in attrs
		
		attrs = dict(attrs)
		if tag == 'input' and self.in_form:
			if attrs.get('type', 'text') in ('hidden', 'text'):
				if 'value' in attrs and 'name' in attrs:
					self.data[attrs['name']] = attrs['value']
			elif attrs.get('type') in ('radio', 'checkbox'):
				if 'checked' in attrs:
					self.data[attrs['name']] = attrs['value']
		if tag == 'select' and self.in_form:
			self.select = attrs['name']
		if tag == 'option' and self.in_form:
			if self.select and 'selected' in attrs:
				self.data[self.select] = attrs['value']
		
	def handle_endtag(self, tag):
		if self.in_form and tag == 'form': 
			self.in_form = False
		if self.select and tag == 'select':
			self.select = None

def set(email):
	site = wikipedia.getSite(lang, family, persistent_http = True)
	site.forceLogin()
	data = site.postForm(site.path(), {'title': 'Special:Preferences'})
	parser = FormParser()
	parser.feed(data[1])
	parser.close()
	
	old = parser.data.get('wpUserEmail', '')
	wikipedia.output(u'Old email for %s was: %s' % (site, old))
	parser.data['wpUserEmail'] = email
	parser.data['wpSaveprefs'] = '1'
	parser.data['title'] = 'Special:Preferences'
	for key in parser.data.keys():
		if not parser.data[key]: del parser.data[key]
	parser.data['wpEmailFlag'] = '1'
	if 'wpOpenotifusertalkpages' in parser.data:
		del parser.data['wpOpenotifusertalkpages']
	site.postForm(site.path(), parser.data)
	site.conn.close()

if __name__ == '__main__':
	email = wikipedia.input('Email?')
	host = wikipedia.input('Host?')
	port = wikipedia.input('Port (default: 110; ssl: 995)?')
	try:
		port = int(port)
	except ValueError:
		port = 0
	if not port:
		port = 110
	ssl = wikipedia.inputChoice('SSL? ', ['no', 'yes'], 
		['n', 'y'], (port == 995) and 'y' or 'n') == 'y'
		
	if os.path.exists('mail-done.txt'):
		f = open('mail-done.txt')
		already_done = [eval(l) for l in f if l]
		f.close()
	else:
		already_done = []
	f_done = open('mail-done.txt', 'a')
		
	for family in config.usernames:
		wikipedia.output(u'Doing %s' % family)
		for lang in config.usernames[family]:
			if (family, lang) not in already_done:
				set(email)
				print >>f_done, repr((family, lang))
