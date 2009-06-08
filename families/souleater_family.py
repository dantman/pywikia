# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Soul Eater Wiki. (souleater.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'souleater'
		self.langs              = { 'en': u'souleater.wikia.com', }
		self.wikia['projectns'] = 'Soul_Eater_Wiki'
		self.wikia['smw']       = True
		
		wikia_basefamily.Family.initNamespaces(self)
		