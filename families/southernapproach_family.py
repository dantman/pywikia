# -*- coding: utf-8  -*-
import family, config

# SouthernApproachWiki, a wiki about Zürich Airport.

class Family(family.Family):
    name = 'southernapproach'
    
    langs = {
        'de':'www.southernapproach.ch',
        }

    # A few selected big languages for things that we do not want to loop over
    # all languages. This is only needed by the titletranslate.py module, so
    # if you carefully avoid the options, you could get away without these
    # for another wikimedia family.

    biglangs = ['de']

    def version(self, code):
        return "1.4"

    def path(self, code):
        return '/wiki/index.php'

