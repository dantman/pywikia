# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Animepedia. (anime.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'anime'
		self.langs              = { 'en': u'anime.wikia.com', }
		self.wikia['projectns'] = 'Animepedia'
		self.wikia['smw']       = True
		self.namespaces[112]    = { '_default': u'World'}
		self.namespaces[113]    = { '_default': u'World talk'}
		
		wikia_basefamily.Family.initNamespaces(self)
		