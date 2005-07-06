# -*- coding: utf-8  -*-
import family

# MediaPedia is a wiki used by the MIT Media Lab.

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'mediapedia'
        
        self.langs = {
            'en':'pedia.media.mit.edu',
        }
            
        # Most namespaces are inherited from family.Family.
        
        self.namespaces[4] = {
            '_default': u'MLPedia',
        }
        self.namespaces[5] = {
            '_default': u'MLPedia talk',
        }

    def version(self, code):
        return "1.3.3"

    def path(self, code):
        return '/wiki'