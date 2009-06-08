# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Gaiapedia. (gaia.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'gaia'
		self.langs              = { 'en': u'gaia.wikia.com', }
		self.wikia['projectns'] = 'Gaiapedia'
		
		wikia_basefamily.Family.initNamespaces(self)
		