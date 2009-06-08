# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Full Metal Alchemist Wiki. (fma.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'fma'
		self.langs              = { 'en': u'fma.wikia.com', }
		self.wikia['projectns'] = 'Full Metal Alchemist'
		
		wikia_basefamily.Family.initNamespaces(self)
		