# -*- coding: utf-8  -*-

import urllib
import family, config

# The wikimedia family that is known as Wikibooks

class Family(family.Family):
    name = 'mozilla'
    def __init__(self):
        for lang in ['en','nl']:
            self._addlang(lang,
			location = 'wiki.mozilla.org',
			namespaces = {-2: u'Media',
                                      -1: u'Special',
                                      0: None,
                                      1: u'Talk',
                                      2: u'User',
                                      3: u'User talk',
                                      4: u'MozillaWiki',
			              5: u'MozillaWiki talk',
                                      6: u'Image',
                                      7: u'Image talk',
                                      8: u'MediaWiki',
                                      9: u'MediaWiki talk',
                                      10: u'Template',
                                      11: u'Template talk',
                                      12: u'Help',
                                      13: u'Help talk',
                                      14: u'Category',
                                      15: u'Category talk'})
    def version(self, code):
        return "1.3.8"

    def put_address(self, code, name):
        return '/wiki?title=%s&action=submit'%name

    def get_address(self, code, name):
        return "/wiki?title="+name+"&redirect=no"

    def references_address(self, code, name):
        return "/wiki?title=%s:Whatlinkshere&target=%s&limit=%d" % (self.special_namespace_url(code), name, config.special_page_limit)

    def maintenance_address(self, code, maintenance_page, default_limit = True):
        if default_limit:
            return ('/wiki?title=%s:Maintenance&subfunction=' %
                    self.special_namespace_url(code)) + maintenance_page
        else:
            return ('/wiki?title=%s:Maintenance&subfunction=' %
                    self.special_namespace_url(code)) + maintenance_page + '&limit=' + str(config.special_page_limit)

    def allmessages_address(self, code):
        return ("/wiki?title=%s:Allmessages&ot=html" %
                self.special_namespace_url(code))

    def login_address(self, code):
        return ('/wiki?title=%s:Userlogin&amp;action=submit' %
                self.special_namespace_url(code))

    def move_address(self, code):
        return ('/wiki?title=%s:Movepage&action=submit' %
                self.special_namespace_url(code))

    def delete_address(self, code, name):
        return '/wiki?title=%s&action=delete' % name

    def export_address(self, code):
        return '/wiki/%s:Export' % self.special_namespace_url(code)
