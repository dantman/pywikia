# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Scratchpad. (scratchpad.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'scratchpad'
		self.langs              = { 'en': u'scratchpad.wikia.com', }
		self.wikia['projectns'] = 'Scratchpad'
		
		wikia_basefamily.Family.initNamespaces(self)
		