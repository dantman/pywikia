# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Zatch Bell! Wiki. (zatchbell.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'zatchbell'
		self.langs              = { 'en': u'zatchbell.wikia.com', }
		self.wikia['projectns'] = 'Zatch_Bell!'
		
		wikia_basefamily.Family.initNamespaces(self)
		
