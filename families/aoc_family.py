# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The AoCWiki. (aoc.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'aoc'
		self.langs              = { 'en': u'aoc.wikia.com', }
		self.wikia['projectns'] = 'AoCWiki'
		self.wikia['userwiki']  = True
		self.wikia['profile']   = True
		self.wikia['smw']       = True
		self.wikia['video']     = True
		self.namespaces[112] = { '_default': u'Guild'}
		self.namespaces[113] = { '_default': u'Guild talk'}
		self.namespaces[500] = { '_default': u'Blog'}
		self.namespaces[501] = { '_default': u'Blog talk'}
		self.namespaces[600] = { '_default': u'UserBox'}
		self.namespaces[601] = { '_default': u'UserBox talk'}
		
		self.disambiguationTemplates = {'_default': u'Disambig',}
		self.disambcatname = {'_default': u'Disambiguation',}
		
		wikia_basefamily.Family.initNamespaces(self)
		