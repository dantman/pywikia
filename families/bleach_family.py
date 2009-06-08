# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Bleach Wiki. (bleach.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'bleach'
		self.langs              = { 'en': u'bleach.wikia.com', }
		self.wikia['projectns'] = 'Bleach Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		