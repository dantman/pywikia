# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Central Wikia. (www.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'central'
		self.langs              = { 'en': u'www.wikia.com', }
		self.wikia['projectns'] = 'Wikia'
		self.namespaces[100] = { '_default': u'Blog'}
		self.namespaces[101] = { '_default': u'Blog comment'}
		self.namespaces[102] = { '_default': u'Pomoc'}
		self.namespaces[103] = { '_default': u'Dyskusja pomocy'}
		
		wikia_basefamily.Family.initNamespaces(self)
		