# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Inside Wikia. (inside.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'inside'
		self.langs              = { 'en': u'inside.wikia.com', }
		self.wikia['projectns'] = 'Inside Wikia'
		
		wikia_basefamily.Family.initNamespaces(self)
		