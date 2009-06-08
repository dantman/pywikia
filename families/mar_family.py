# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Marpedia. (mar.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'mar'
		self.langs              = { 'en': u'mar.wikia.com', }
		self.wikia['projectns'] = 'Marpedia'
		
		wikia_basefamily.Family.initNamespaces(self)
		