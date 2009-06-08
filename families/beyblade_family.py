# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Beyblade Wiki. (beyblade.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'beyblade'
		self.langs              = { 'en': u'beyblade.wikia.com', }
		self.wikia['projectns'] = 'Beyblade Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		