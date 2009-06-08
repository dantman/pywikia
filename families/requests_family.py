# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Request Wiki. (requests.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'requests'
		self.langs              = { 'en': u'requests.wikia.com', }
		self.wikia['projectns'] = 'Request Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		