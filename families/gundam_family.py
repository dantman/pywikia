# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Gundam Wiki. (gundam.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'gundam'
		self.langs              = { 'en': u'gundam.wikia.com', }
		self.wikia['projectns'] = 'Gundam Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		