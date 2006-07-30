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

    titles = True
    links = False
    aplimit = 500
    apfrom = ''
    title = None
    replace = False
    
    def __init__(self, args):    
        
        for arg in args:
            arg = wikipedia.argHandler(arg, 'casechecker')
            if arg:
                if arg.startswith('-from:'):
                    self.apfrom = arg[6:]
                elif arg.startswith('-from'):
                    self.apfrom = wikipedia.input(u'Which page to start from: ')
                elif arg.startswith('-limit:'):
                    self.aplimit = int(arg[7:])
                elif arg == '-links':
                    self.links = True
                elif arg == '-linksonly':
                    self.links = True
                    self.titles = False
                elif arg == '-replace':
                    self.replace = True
                else:
                    wikipedia.output(u'Unknown argument %s' % arg)
                    sys.exit()

        self.params = {'what'         : 'allpages',
                      'aplimit'       : self.aplimit, 
                      'apfilterredir' : 'nonredirects',
                      'noprofile'     : '' }

        if self.links:
            self.params['what'] += '|links';
            
        self.site = wikipedia.getSite()
        
    def Run(self):
        try:
            for namespace in [0, 10, 12, 14]:
                self.params['apnamespace'] = namespace
                self.apfrom = self.apfrom
                title = None
                
                while True:                
                    # Get data
                    self.params['apfrom'] = self.apfrom
                    data = query.GetData( self.site.lang, self.params)
                    try:
                        self.apfrom = data['query']['allpages']['next']
                    except:
                        self.apfrom = None
    
                    # Process received data
                    if 'pages' in data:
                        for pageID, page in data['pages'].iteritems():
                            printed = False
                            title = page['title']
                            if self.titles:
                                err = self.ProcessTitle(title)
                                if err:
                                    changed = False
                                    if self.replace and namespace != 14 and len(err) == 2:
                                        src = wikipedia.Page(self.site, title)
                                        dst = wikipedia.Page(self.site, err[1])
                                        if not dst.exists():
                                            # choice = wikipedia.inputChoice(u'Move %s to %s?' % (title, err[1]), ['Yes', 'No'], ['y', 'n'])
                                            src.move( err[1], u'mixed case rename')
                                            changed = True
                                    
                                    if not changed:
                                        wikipedia.output(u"* " + err[0])
                                        printed = True
                                                                    
                            if self.links:
                                if 'links' in page:
                                    pageObj = None
                                    pageTxt = None
                                    msg = []
                                    for l in page['links']:
                                        ltxt = l['*']
                                        err = self.ProcessTitle(ltxt)
                                        if err:
                                            if self.replace and len(err) == 2:
                                                if pageObj is None:
                                                    pageObj = wikipedia.Page(self.site, title)
                                                    pageTxt = pageObj.get()
                                                # choice = wikipedia.inputChoice(u'Rename link from %s to %s?' % (title, err[1]), ['Yes', 'No'], ['y', 'n'])
                                                msg.append(u'[[%s]] => [[%s]]' % (ltxt, err[1]))
                                                pageTxt = pageTxt.replace(ltxt, err[1])
                                                pageTxt = pageTxt.replace(ltxt[0].lower() + ltxt[1:], err[1][0].lower() + err[1][1:])
                                            else:
                                                if not printed:
                                                    wikipedia.output(u"* [[%s]]: link to %s" % (title, err[0]))
                                                    printed = True
                                                else:
                                                    wikipedia.output(u"** link to %s" % err[0])
                                                
        
                                    if pageObj is not None:
                                        if pageObj.get() == pageTxt:
                                            wikipedia.output(u"* Error: Could not auto-replace [[%s]]" % title)
                                        else:
                                            wikipedia.output(u'Case Replacements: %s' % u', '.join(msg))
                                            pageObj.put(pageTxt, u'Case Replacements: %s' % u', '.join(msg))
                
                    if self.apfrom is None:
                        break

            print "***************************** Done"
                
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
                alternativeLines = [ title[0:m.span()[0]] + t + title[m.span()[1]:] for t in possibleWords ]

            count += 1

        if count == 0:
            return None
        
        res = self.MakeLink(title)
        if len(possibleWords) > 0:
            res += u", sugestions: "
            if count == 1:
                res += u', '.join([self.MakeLink(t) for t in alternativeLines])
            else:
                res += u', '.join([self.ColorCodeWord(t) for t in possibleWords])

        if count == 1 and len(alternativeLines) > 0:
            return [res] + alternativeLines
        else:
            return [res]
    
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
        return u"[[:%s|««« %s »»»]]" % (title, self.ColorCodeWord(title))
        
if __name__ == "__main__":
    bot = CaseChecker(sys.argv[1:])
    bot.Run()