# -*- coding: utf-8  -*-

import config, urllib, family

# The meta family

# Known wikipedia languages, given as a dictionary mapping the language code
# to the hostname of the site hosting that wikipedia. For human consumption,
# the full name of the language is given behind each line as a comment

class Family(family.Family):
    def __init__(self):
        self.langs = {'meta': 'meta.wikimedia.org'}
