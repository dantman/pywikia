# -*- coding: utf-8  -*-
import family, wikia_basefamily

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'kyokaramaoh'
		self.langs              = { 'en': u'kyokaramaoh.wikia.com', }
		self.wikia['projectns'] = 'Kyo_Kara_Maoh!'
		
		wikia_basefamily.Family.initNamespaces(self)
		
