# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Megaman Knowledge Base. (megaman.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'megaman'
		self.langs              = { 'en': u'megaman.wikia.com', }
		self.wikia['projectns'] = 'The Mega Man Knowledge-base'
		
		wikia_basefamily.Family.initNamespaces(self)
		