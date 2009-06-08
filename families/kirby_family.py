# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Kirby Wiki. (kirby.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'kirby'
		self.langs              = { 'en': u'kirby.wikia.com', }
		self.wikia['projectns'] = 'Kirby Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		