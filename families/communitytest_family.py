# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Community Test Wiki. (communitytest.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name            = 'communitytest'
		self.langs           = { 'en':       u'communitytest.wikia.com', }
		self.wikia['projectns'] = 'CommunityTest'
		self.namespaces[112] = { '_default': u'Extra1'}
		self.namespaces[113] = { '_default': u'Extra1 talk'}
		self.namespaces[114] = { '_default': u'Extra2'}
		self.namespaces[115] = { '_default': u'Extra2 talk'}
		self.wikia['profile'] = 207
		self.wikia['smw']    = True
		
		wikia_basefamily.Family.initNamespaces(self)
		