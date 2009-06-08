# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Desert Punk Wiki. (desertpunk.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'desertpunk'
		self.langs              = { 'en': u'desertpunk.wikia.com', }
		self.wikia['projectns'] = 'Desert Punk Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		