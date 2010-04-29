# -*- coding: utf-8  -*-
import family, wikia_basefamily

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'opartshunter'
		self.langs              = { 'en': u'opartshunter.wikia.com', }
		self.wikia['projectns'] = 'O-Parts_Hunter_Wiki'
		self.wikia['smw']       = True
		
		wikia_basefamily.Family.initNamespaces(self)
		
