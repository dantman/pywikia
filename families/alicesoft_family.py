# -*- coding: utf-8  -*-
import family, wikia_basefamily

# AliceSoftWiki. (alicesoft.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'alicesoft'
		self.langs              = { 'en': u'alicesoft.wikia.com', }
		self.wikia['projectns'] = 'AliceSoftWiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		