# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Negima! Wiki. (negima.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'negima'
		self.langs              = { 'en': u'negima.wikia.com', }
		self.wikia['projectns'] = 'Negima! Wiki'
		self.wikia['smw']       = True
		
		wikia_basefamily.Family.initNamespaces(self)
		