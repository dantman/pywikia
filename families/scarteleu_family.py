# -*- coding: utf-8  -*-
import family, wikia_basefamily

# European Steamwheedle Cartel. (scarteleu.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'scarteleu'
		self.langs              = { 'en': u'scarteleu.wikia.com', }
		self.wikia['projectns'] = 'European Steamwheedle Cartel'
		
		wikia_basefamily.Family.initNamespaces(self)
		