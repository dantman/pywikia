#!/usr/bin/python
# -*- coding: utf-8  -*-
""" Script to enumerate all pages in the wikipedia and find all titles
with mixed latin and cyrilic alphabets.
"""

import sys, query, wikipedia, re

apfrom = ''
aplimit = 500
apnamespace = 0
links = False

cyrLtr = u'[а-яА-Я]'
#cyrLtr = u'[АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя]'
latLtr = u'[a-zA-Z]'
pattern = re.compile(u'(%s%s|%s%s)' % (latLtr, cyrLtr, cyrLtr, latLtr) )
apfrom = None
title = None

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg, 'casechecker')
    if arg:
        if arg.startswith('-from:'):
            apfrom = arg[6:]
        elif arg.startswith('-limit:'):
            aplimit = int(arg[7:])
        elif arg.startswith('-ns:'):
            apnamespace = int(arg[4:])
        elif arg == '-links':
            links = True
    
try:
    while True:
    
        params = {'apnamespace' : apnamespace, 
                  'aplimit' : aplimit, 
                  'apfrom' : apfrom,
                  'apfilterredir' : 'nonredirects',
                  'noprofile':''}
        if links:
            params['what'] = 'allpages|links';
        else:
            params['what'] = 'allpages';

        data = query.GetData( wikipedia.getSite().lang, params)
        try:
            apfrom = data['query']['allpages']['next']
        except:
            apfrom = None
    
    
        for pageID, page in data['pages'].iteritems():
            title = page['title']
            m = pattern.search(title)
            printed = False
            if m is not None:
                wikipedia.output(u'* [[%s]] @ %d' % (title, m.span()[0]+2))
                printed = True
                
            if links:
                if 'links' in page:
                    for l in page['links']:
                        m = pattern.search(l['*'])
                        if m is not None:
                            if not printed:
                                wikipedia.output(u'* [[%s]]: link to [[%s]] @ %d' % (title, l['*'], m.span()[0]+2))
                                printed = True
                            else:
                                wikipedia.output(u'** link to [[%s]] @ %d' % (l['*'], m.span()[0]+2))
    
        if apfrom is None:
            break
        
except:
    if apfrom is not None:
        wikipedia.output(u'Exception at Title = %s, Next = %s' % (title, apfrom))
    wikipedia.stopme()
    raise