# -*- coding: utf-8  -*-
import family, config

# SouthernApproachWiki, a wiki about Zürich Airport.

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'southernapproach'
        
        self.langs = {
            'de':'www.southernapproach.ch',
        }
            
        # Most namespaces are inherited from family.Family.
        
        self.namespaces[4] = {
            '_default': u'SouthernApproachWiki',
        }
        self.namespaces[5] = {
            '_default': u'SouthernApproachWiki Diskussion',
        }

    def version(self, code):
        return "1.4"

    def path(self, code):
        return '/wiki/index.php'