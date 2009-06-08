# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Dragon Ball Wiki. (dragonball.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'dragonball'
		self.langs              = { 'en': u'dragonball.wikia.com', }
		self.wikia['projectns'] = 'Dragon Ball'
		
		wikia_basefamily.Family.initNamespaces(self)
		