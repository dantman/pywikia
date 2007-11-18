""" This module contains a read-write class that represents the user preferences. """
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint 

class Checkbox(object):
	def __init__(self, value, state):
		self.value = value
		self.state = state
	def set(self):
		self.state = True
	def unset(self):
		self.state = False
	def __bool__(self):
		return self.state
	def __str__(self):
		return str(self.state)
		
class Select(list):
	def __init__(self):
		list.__init__(self, ())
		self.value = u''
	def set(self, value):
		self.value = value
	def __bool__(self):
		return bool(self.value)
	def __str__(self):
		return str(self.value)
	def __unicode__(self):
		return unicode(self.value)

class Preferences(HTMLParser, dict):
	def __init__(self, site = None):
		HTMLParser.__init__(self)
		dict.__init__(self, ())
		self.in_form = False
		self.select = None
		
		if site: self.load(site)
	
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
					self[attrs['name']] = attrs['value']
			elif attrs.get('type') == 'checkbox':
				self[attrs['name']] = Checkbox(attrs['value'],
					'checked' in attrs)
			elif attrs.get('type') == 'radio':
				if attrs['name'] not in self:
					self[attrs['name']] = Select()
				self[attrs['name']].append(attrs['value'])
				if 'checked' in attrs:
					self[attrs['name']].set(attrs['value'])
		if tag == 'select' and self.in_form:
			self.select = Select()
			self[attrs['name']] = self.select
		if tag == 'option' and self.in_form:
			if self.select:
				self.select.append(attrs['value'])
				if 'selected' in attrs:
					self.select.set(attrs['value'])
		
	def handle_endtag(self, tag):
		if self.in_form and tag == 'form': 
			self.in_form = False
		if self.select and tag == 'select':
			self.select = None
			
	
	def load(self, site):
		site.forceLogin()
		data = site.getUrl(site.path() + '?title=Special:Preferences')
		self.feed(data)
		self.close()
		self.site = site
		
	def save(self):
		predata = {'wpSaveprefs': '1', 'title': 'Special:Preferences'}
		for key, value in self.iteritems():
			if value:
				if type(value) in (Checkbox, Select):
					predata[key] = value.value
				else:
					predata[key] = value
		self.site.postForm(self.site.path(), predata)
	def set(self, key, value):
		if key in self:
			if type(self[key]) is Select:
				return self.key.set(value)
			elif type(self[key]) is Checkbox:
				if value:
					return self[key].set()
				else:
					return self[key].unset()
		self[key] = value


def table_cell(value, length):
	s = u'| ' + unicode(value)
	tabs = length - (len(s) / 8)
	if tabs < 0: tabs = 0
	s = s + '\t' * tabs
	return s
	
def set_all(keys, values, verbose = False):
	import wikipedia, config
	for family in config.usernames:
		for lang in config.usernames[family]:
			site = wikipedia.getSite(lang, family, persistent_http = True)
			prefs = Preferences(site)
			for key, value in zip(keys, values):
				prev = unicode(prefs.get(key, ''))
				if verbose: wikipedia.output(u"Setting '%s' on %s from '%s' to '%s'." % \
						(key, site, prev, value))
				prefs.set(key, value)
			prefs.save()
			site.conn.close()

def main():
	import wikipedia, config
	
	wikipedia.output(u'Warning! This script will set preferences on all configured accounts!')
	wikipedia.output(u'You have %s accounts configured.' % \
		sum(map(len, filter(lambda key: bool(config.usernames[key]), config.usernames.iterkeys()))))
	
	if wikipedia.inputChoice(u'Do you wish to continue?', ['no', 'yes'], ['n', 'y'], 'n') == 'n': return
	
	if wikipedia.inputChoice(u'Do you already know which preference you wish to set?', 
			['no', 'yes'], ['n', 'y'], 'y') == 'n':
		site = wikipedia.getSite()
		wikipedia.output(u'Getting list of available preferences from %s.' % site)
		prefs = Preferences(site)
		
		wikipedia.output(u'-------------------------------------------------------------------------')
		wikipedia.output(u'| Name				| Value					|')
		wikipedia.output(u'-------------------------------------------------------------------------')
		pref_data = prefs.items()
		pref_data.sort()
		for key, value in pref_data:
			wikipedia.output(table_cell(key, 4) + table_cell(value, 5) + '|')
		wikipedia.output(u'-------------------------------------------------------------------------')
	wikipedia.output(u'')
	wikipedia.output(u'(For checkboxes: An empty string evaluates to False; all others to True)')
	wikipedia.output(u'')
	
	while True:
		keys, values = [], []
		while True:
			try:
				keys.append(wikipedia.input(u'Which preference do you wish to set?'))
			except KeyboardInterrupt:
				return
			values.append(wikipedia.input(u"To what value do you wish to set '%s'?" % keys[-1]))
			if wikipedia.inputChoice(u"Set more preferences?", 
					['no', 'yes'], ['n', 'y'], 'n') == 'n': break
						
		if wikipedia.inputChoice(u"Set %s?" % u', '.join((u'%s:%s' % (key, value)
				for key, value in zip(keys, values))), 
				['yes', 'no'], ['y', 'n'], 'n') == 'y':
			set_all(keys, values, verbose = True)
			wikipedia.output(u"Preferences have been set on all wikis.")
	
if __name__ == '__main__':
	import sys
	sys.path.append('..')
	import wikipedia
	try:
		wikipedia.handleArgs()
		main()
	finally:
		wikipedia.stopme()