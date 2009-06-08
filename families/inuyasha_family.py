# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The InuYasha Wiki. (inuyasha.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'inuyasha'
		self.langs              = { 'en': u'inuyasha.wikia.com', }
		self.wikia['projectns'] = 'InuYasha'
		
		wikia_basefamily.Family.initNamespaces(self)
		