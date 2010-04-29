# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Code Geass Fanon Wiki. (codegeassfanon.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'codegeassfanon'
		self.langs              = { 'en': u'codegeassfanon.wikia.com', }
		self.wikia['projectns'] = 'Code Geass Fanon Wiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		
