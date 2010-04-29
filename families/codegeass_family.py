# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Code Geass Wiki. (codegeass.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'codegeass'
		self.langs              = { 'en': u'codegeass.wikia.com', }
		self.wikia['projectns'] = 'Code Geass Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		
