# -*- coding: utf-8  -*-
import family, wikia_basefamily

# CompuWiki. (computing.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'computing'
		self.langs              = { 'en': u'computing.wikia.com', }
		self.wikia['projectns'] = 'CompuWiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		