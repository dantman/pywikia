# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Mangapedia. (manga.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'manga'
		self.langs              = { 'en': u'manga.wikia.com', }
		self.wikia['projectns'] = 'MangaWiki'
		
		wikia_basefamily.Family.initNamespaces(self)
		