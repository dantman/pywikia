# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Ghost in the Shell Wiki. (en.ghostintheshell.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'ghostintheshell'
		self.langs              = { 'en': u'ghostintheshell.wikia.com', }
		self.wikia['projectns'] = 'Ghost in the Shell Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		