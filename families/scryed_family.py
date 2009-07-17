# -*- coding: utf-8  -*-
import family, wikia_basefamily

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'scryed'
		self.langs              = { 'en': u'scryed.wikia.com', }
		self.wikia['projectns'] = 'S-CRY-ed_Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		
