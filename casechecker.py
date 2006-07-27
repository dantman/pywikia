#!/usr/bin/python
# -*- coding: utf-8  -*-
""" Script to enumerate all pages in the wikipedia and find all titles
with mixed latin and cyrilic alphabets.
"""

import sys, query, wikipedia, re

class CaseChecker( object ):

    cyrSuspects = u'АаВЕеКкМмНОоРрСсТУуХх'
    latSuspects = u'AaBEeKkMmHOoPpCcTYyXx'

    cyrToLatDict = dict([(ord(cyrSuspects[i]), latSuspects[i]) for i in range(len(cyrSuspects))])
    latToCyrDict = dict([(ord(latSuspects[i]), cyrSuspects[i]) for i in range(len(cyrSuspects))])

    cyrLtr = u'АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя'
    latLtr = u'abcdefghijklimnopqrstuvwxyzABCDEFGHIJKLIMNOPQRSTUVWXYZ'
    
    badPtrnStr = u'([%s][%s]|[%s][%s])' % (latLtr, cyrLtr, cyrLtr, latLtr)
    badPtrn = re.compile(badPtrnStr)
    badWordPtrn = re.compile(u'[%s%s]*%s[%s%s]*' % (latLtr, cyrLtr, badPtrnStr, latLtr, cyrLtr) )

    cyrClrFnt = u'<font color=green>'
    latClrFnt = u'<font color=brown>'
    suffixClr = u'</font>'

    links = False
    apfrom = ''
    aplimit = 500
    apnamespace = 0
    apfrom = None
    title = None
    
    def __init__(self, args):    
        
        for arg in args:
            arg = wikipedia.argHandler(arg, 'casechecker')
            if arg:
                if arg.startswith('-from:'):
                    self.apfrom = arg[6:]
                elif arg.startswith('-limit:'):
                    self.aplimit = int(arg[7:])
                elif arg.startswith('-ns:'):
                    self.apnamespace = int(arg[4:])
                elif arg == '-links':
                    self.links = True

        self.params = {'what'          : 'allpages',
                  'apnamespace'   : self.apnamespace, 
                  'aplimit'       : self.aplimit, 
                  'apfilterredir' : 'nonredirects',
                  'noprofile'     : '' }

        if self.links:
            self.params['what'] += '|links';
        
    def Run(self):
        try:
            while True:
            
                # Get data
                self.params['apfrom'] = self.apfrom;        
                data = query.GetData( wikipedia.getSite().lang, self.params)
                try:
                    self.apfrom = data['query']['allpages']['next']
                except:
                    self.apfrom = None

                # Process received data
                for pageID, page in data['pages'].iteritems():
                    printed = False
                    title = page['title']
                    err = self.ProcessTitle(title)
                    if err:
                        wikipedia.output(u"* " + err)
                        printed = True
                        
                    if self.links:
                        if 'links' in page:
                            for l in page['links']:
                                err = self.ProcessTitle(l['*'])
                                if err:
                                    if not printed:
                                        wikipedia.output(u"* [[%s]]: link to %s" % (title, err))
                                        printed = True
                                    else:
                                        wikipedia.output(u"** link to %s" % err)
            
                if self.apfrom is None:
                    print "***************************** Done"
                    break
                
        except:
            if self.apfrom is not None:
                wikipedia.output(u'Exception at Title = %s, Next = %s' % (title, self.apfrom))
            wikipedia.stopme()
            raise
        
    def ProcessTitle(self, title):
        
        possibleWords = []
        tempWords = []
        count = 0
        
        for m in self.badWordPtrn.finditer(title):
        
            badWord = title[m.span()[0] : m.span()[1]]
            # See if it would make sense to treat the whole word as either cyrilic or latin
            mightBeLat = mightBeCyr = True
            for l in badWord:
                if l in self.cyrLtr:
                    if mightBeLat and l not in self.cyrSuspects:
                        mightBeLat = False
                else:
                    if mightBeCyr and l not in self.latSuspects:
                        mightBeCyr = False
                    if l not in self.latLtr: raise "Assert failed"
            
            if mightBeCyr:
                possibleWords.append(badWord.translate(self.latToCyrDict))
            if mightBeLat:
                possibleWords.append(badWord.translate(self.cyrToLatDict))
            
            if count == 0:
                # There is only one bad word, create links
                alternativeLines = [ self.MakeLink( title[0:m.span()[0]] + t + title[m.span()[1]:] ) for t in possibleWords ]

            count += 1

        if count == 0:
            return None
        
        res = self.MakeLink(title)
        if len(possibleWords) > 0:
            res += u", sugestions: "
            if count == 1:
                res += u', '.join(alternativeLines)
            else:
                res += u', '.join([self.ColorCodeWord(t) for t in possibleWords])
    
        return res
    
    def ColorCodeWord(self, word):
        
        res = u"<b>"
        lastIsCyr = word[0] in self.cyrLtr
        if lastIsCyr:
            res += self.cyrClrFnt
        else:
            res += self.latClrFnt

        for l in word:
            if l in self.cyrLtr:
                if not lastIsCyr:
                    res += self.suffixClr + self.cyrClrFnt
                    lastIsCyr = True
            elif l in self.latLtr:
                if lastIsCyr:
                    res += self.suffixClr + self.latClrFnt
                    lastIsCyr = False
            res += l
        
        return res + self.suffixClr + u"</b>"

    def MakeLink(self, title):
        return u"[[%s|««« %s »»»]]" % (title, self.ColorCodeWord(title))
        
if __name__ == "__main__":
    bot = CaseChecker(sys.argv[1:])
    bot.Run()