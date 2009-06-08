# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Earthen Ring EU. (earthenringeu.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'earthenringeu'
		self.langs              = { 'en': u'earthenringeu.wikia.com', }
		self.wikia['projectns'] = 'Earthen Ring EU'
		
		wikia_basefamily.Family.initNamespaces(self)
		