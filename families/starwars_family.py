# -*- coding: utf-8  -*-
import family, wikia_basefamily

# The Star Wars(Wookieepedia) Wikia

class Family(wikia_basefamily.Family):

	def __init__(self):
		
		wikia_basefamily.Family.__init__(self)
		
        self.name          = 'starwars'
        self.langs         = {
                               'en': 'starwars.wikia.com',
                               'fr': 'fr.starwars.wikia.com',
                               'es': 'es.starwars.wikia.com',
                               'pt': 'pt.starwars.wikia.com',
                               'ru': 'ru.starwars.wikia.com',
                               'pl': 'pl.starwars.wikia.com',
                               'hu': 'hu.starwars.wikia.com',
                               'nl': 'nl.starwars.wikia.com',
                               'bg': 'bg.starwars.wikia.com',
                               'sl': 'sl.starwars.wikia.com',
                               'zh': 'zh-hk.starwars.wikia.com',
                               'da': 'da.starwars.wikia.com',
                               'fi': 'fi.starwars.wikia.com',
                             }
      # Most namespaces are inherited from family.Family.
        self.namespaces[4] = {
                               '_default': u'Wookieepedia',
                               'fr': u'Star Wars Wiki',
                               'es': u'Star Wars',
                               'pt': u'Star Wars Wiki',
                               'ru': u'Star Wars',
                               'pl': u'Empirepedia',
                               'hu': u'Csillagok Háborúja',
                               'nl': u'Star Wars Wiki',
                               'bg': u'Star Wars',
                               'sl': u'SWikoopedia',
                               'zh': u'????',
                               'da': u'Wookieepedia',
                               'fi': u'Jedipedia',
                             }
        self.namespaces[5] = {
                               '_default': u'Wookieepedia talk',
                               'fr': u'Discussion Star Wars Wiki',
                               'es': u'Star Wars Discusión',
                               'pt': u'Star Wars Wiki Discussão',
                               'ru': u'?????????? Star Wars',
                               'pl': u'Dyskusja Empirepedia',
                               'hu': u'Csillagok Háborúja vita',
                               'nl': u'Overleg Star Wars Wiki',
                               'bg': u'Star Wars ??????',
                               'sl': u'Pogovor o SWikoopedia',
                               'zh': u'??????',
                               'da': u'Wookieepedia-diskussion',
                               'fi': u'Keskustelu Jedipediasta',
                             }
        
        wikia_basefamily.Family.initNamespaces(self)
		