#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Script to follow new articles on a wikipedia and flag them
with a template or eventually blank them.

There must be A LOT of bugs ! Use with caution and verify what
it is doing !
"""

__version__='$Id$'

import sys
import wikipedia
import datetime
import time
import traceback

__metaclass__ = type

# The question asked
question = u"""
b) blank page
d) delete page (need sysop right)

q) quit cleaningbot
Enter) OK
What is it? """

# templates that can be used followed by the message used as comment
# templates contains list of languages code
#   languages code contains list of templates to be used
#       templates contains a message and its position 
templates = {
	'en':{'{{delete}}' :{ 'msg' : 'This article should be deleted' ,
                          'pos': 'top'},
          '{{cleanup}}':{ 'msg' : 'This article need cleanup',
                          'pos': 'top'},
          '{{stub}}'   :{ 'msg' : 'This article is a stub',
                          'pos': 'bottom'},
          },
    'fr':{u'{{suppression}}' :{ 'msg' : u'Cet article devrait être supprimé',
                                'pos': 'top'},
          u'{{à vérifier}}'  :{ 'msg': u'Cet article est à vérifier',
                                'pos': 'top'},
          u'{{ébauche}}'     :{ 'msg': u'Cet article est une ébauche',
                                'pos': 'bottom'},
          },
	'ia':{'{{Eliminar}}' :{ 'msg' : 'Iste articulo debe esser eliminate' ,
                          'pos': 'top'},
          '{{Revision}}':{ 'msg' : 'Iste articulo require revision',
                          'pos': 'top'},
          '{{Stub}}'   :{ 'msg' : 'Iste articulo es in stato embryonic',
                          'pos': 'bottom'},
          },
        'nl':{u'{{weg}}' :{ 'msg' : '',
                            'pos' : 'top'},
              u'{{nuweg}}' :{ 'msg' : '',
                              'pos' : 'top'},
              u'{{wiu}}' :{ 'msg' : '',
                            'pos' : 'top'},
              u'{{beg}}' :{ 'msg' : '',
                            'pos' : 'bottom'},
              u'{{wikify}}' :{ 'msg' : '',
                               'pos' : 'top'},
              u'{{wb}}' :{ 'msg' : '',
                           'pos' : 'top'},
              },
    }

# Message used when blanking an article
blanking = {
    'en': 'blanked, content was "%s"',
    'fr': u'blanchit, le contenu était "%s"',
}


# do nothing if this is in it
done = {
    'en':('{{delete}}', '{{speedy}}', '{{VfD}}', '{{cleanup}}', '{{nonsense}}'),
    'fr':('{{suppression}}', u'{{à vérifier}}'),
    'nl':('{{nuweg}}', '{{weg}}', '{{wb}}', '{{wiu}}', '{{nocat}}')
}
# TODO: merge 'done' with 'templates' above

class PageHandler:
    # Initialization stuff
    def __init__(self, page, date, length, loggedIn, user, comment):
        self.page = page
        self.date = date
        self.length = length
        self.loggedIn = loggedIn
        self.user = user
        self.comment = comment

    # Display informations about an article    
    def showpageinfo(self):
        wikipedia.output(u'[[%s]] %s ' % (self.page.title(), self.date))
        print 'Length: %i bytes' % self.length
        wikipedia.output(u'User  : %s' % self.user)

    def couldbebad(self):
        return self.length < 250 or not self.loggedIn

    def handlebadpage(self):
        try:
            self.content = self.page.get()
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'Already redirected, skipping.')
            return
        except wikipedia.NoPage:
            wikipedia.output(u'Already deleted')
            return

        for d in wikipedia.translate(wikipedia.getSite(), done):
            if d in self.content:
                wikipedia.output(u'Found: "%s" in content, nothing necessary'%d)
                return
        print "---- Start content ----------------"
        wikipedia.output(u""+self.content)
        print "---- End of content ---------------"

        # Loop other user answer
        answered = False
        while not answered:
            answer = wikipedia.input(question)

            if answer == 'q':
                sys.exit("Exiting")
            if answer == 'd':
                wikipedia.output(u'Trying to delete page [[%s]].' % self.page.title())
                self.page.delete()
                return
            if answer == 'b':
                wikipedia.output(u'Blanking page [[%s]].' % self.page.title())
                try:
                    self.page.put('', comment = wikipedia.translate(wikipedia.getSite(), blanking) % self.content )
                except EditConflict:
                    print "An edit conflict occured ! Automaticly retrying"
                    handlebadpage(self)
                return
            if answer == '':
                print 'Page correct ! Proceeding with next pages.'
                return
            # Check user input:
            if answer[0] == 'u':
                # Answer entered as an utf8 string
                try:
                    answer=int(answer[1:])
                except ValueError:
                    # User entered wrong value
                    wikipedia.output(u'ERROR: "%s" is not valid' % answer)
                    continue
                answered=True
            else:
                try:
                    answer=int(answer)
                except ValueError:
                    # User entered wrong value
                    wikipedia.output(u'ERROR: "%s" is not valid' % answer)
                    continue
                answered=True

        # grab the template parameters
        tpl = wikipedia.translate(wikipedia.getSite(), templates)[questionlist[answer]]
        if tpl['pos'] == 'top':
            wikipedia.output(u'prepending %s...' % questionlist[answer])
            newcontent = questionlist[answer] + '\n' + self.content
            self.page.put(newcontent, comment = tpl['msg'])
        elif tpl['pos'] == 'bottom':
            wikipedia.output(u'appending %s...' % questionlist[answer])
            newcontent = self.content + '\n' + questionlist[answer]
            self.page.put(newcontent, comment = tpl['msg'])
        else:
            wikipedia.output(u'ERROR: "pos" should be "top" or "bottom" for template %s. Contact a developer.' % questionlist[answer])
            sys.exit("Exiting")

        wikipedia.output(u'Probably added %s with comment %s' % (questionlist[answer], tpl ['msg']))


    def run(self):
        self.showpageinfo()
        if self.couldbebad():
            print 'Integrity of page doubtful...'
            try:
                self.handlebadpage()
            except wikipedia.NoPage:
                print 'seems already gone'
        print '----- Current time:', datetime.datetime.now()

                
class CleaningBot:
    def __init__(self, site=None):
        if site is None:
            site = wikipedia.getSite()
        self.site = site

    def run(self):
        for (page, date, length, loggedIn, username, comment) in wikipedia.getSite().newpages(100, repeat = True):
            handler = PageHandler(page, date, length, loggedIn, username, comment)
            handler.run()

# Generate the question text
i = 0
questions = '\n'
questionlist = {}
for t in wikipedia.translate(wikipedia.getSite(), templates):
    i+=1
    questions += ( u'%s) %s\n' % (i,t) )
    questionlist[i] = t
question = questions + question

# MAIN
if __name__ == "__main__":
    try:
        for arg in sys.argv[1:]:
            wikipedia.argHandler(arg, 'interwiki')
        bot = CleaningBot()
        bot.run()
    except:
        wikipedia.stopme()
        raise

