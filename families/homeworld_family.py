# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Encyclopedia Hiigara. (homeworld.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'homeworld'
		self.langs              = { 'en': u'homeworld.wikia.com', }
		self.wikia['projectns'] = 'Encyclopedia Hiigara'
		
		wikia_basefamily.Family.initNamespaces(self)
		