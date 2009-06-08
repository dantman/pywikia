# -*- coding: utf-8  -*-
import family, wikia_basefamily

# Yu-Gi-Oh! Wiki. (yugioh.wikia.com)

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
		self.name               = 'yugioh'
		self.langs              = { 'en': u'yugioh.wikia.com', }
		self.wikia['projectns'] = 'Yu-Gi-Oh!'
		self.namespaces[100]    = { '_default': u'Card Gallery'}
		self.namespaces[101]    = { '_default': u'Card Gallery talk'}
		self.namespaces[102]    = { '_default': u'Card Rulings'}
		self.namespaces[103]    = { '_default': u'Card Rulings talk'}
		self.namespaces[104]    = { '_default': u'Card Errata'}
		self.namespaces[105]    = { '_default': u'Card Errata talk'}
		self.namespaces[106]    = { '_default': u'Card Tips'}
		self.namespaces[107]    = { '_default': u'Card Tips talk'}
		self.namespaces[108]    = { '_default': u'Card Trivia'}
		self.namespaces[109]    = { '_default': u'Card Trivia talk'}
		self.namespaces[112]    = { '_default': u'Anime and Manga Appearances'}
		self.namespaces[113]    = { '_default': u'Anime and Manga Appearances talk'}
		self.namespaces[114]    = { '_default': u'Portal'}
		self.namespaces[115]    = { '_default': u'Portal talk'}
		self.namespaces[116]    = { '_default': u'Card Lores'}
		self.namespaces[117]    = { '_default': u'Card Lores talk'}
		self.namespaces[118]    = { '_default': u'Card Artworks'}
		self.namespaces[119]    = { '_default': u'Card Artworks talk'}
		self.namespaces[120]    = { '_default': u'Card Names'}
		self.namespaces[121]    = { '_default': u'Card Names talk'}
		self.namespaces[122]    = { '_default': u'Set Card Lists'}
		self.namespaces[123]    = { '_default': u'Set Card Lists talk'}
		self.namespaces[124]    = { '_default': u'Set Card Galleries'}
		self.namespaces[125]    = { '_default': u'Set Card Galleries talk'}
		self.namespaces[126]    = { '_default': u'Set Card Ratios'}
		self.namespaces[127]    = { '_default': u'Set Card Ratios talk'}
		self.wikia['smw']       = True
		
		wikia_basefamily.Family.initNamespaces(self)
		