#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This utility runs through all known languages in a family.
Its primary use is to find all mismatches between the namespace naming in the family files
and the language files on the wiki servers.

Most common scenario usage scenario:

   python testfamily.py -log:logfilename.txt -family:familyname

"""
#
# (C) Yuri Astrakhan, 2005
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys, wikipedia, traceback


#===========
		
if __name__ == "__main__":
	try:
		for arg in sys.argv[1:]:
			arg = wikipedia.argHandler(arg, 'testfamily')
		
		
		site = wikipedia.getSite()
		fam = site.family

		for lang in fam.knownlanguages:
			try:
				langsite = wikipedia.getSite(lang)
				wikipedia.getall( langsite, [wikipedia.Page( langsite, 'Any page name' )])
			except:
				wikipedia.output( u'Error processing language %s' % lang )
				wikipedia.output( u''.join(traceback.format_exception(*sys.exc_info())))

		if False:
			# skip until the family gets global fixing
			
			wikipedia.output(u"\n\n------------------ namespace table -------------------\n");

			wikipedia.output(u"        self.namespaces = {")
			for k,v in sorted(fam.namespaces.iteritems()):
				wikipedia.output(u"            %i: {" % k)
				for k2,v2 in sorted(v.iteritems()):
					if v2 is not None:
						v2 = u"u'%s'" % v2
					wikipedia.output(u"                '%s': %s," % (k2,v2))
				wikipedia.output(u"            },")
			wikipedia.output(u"        }")

	finally:
		wikipedia.stopme()
