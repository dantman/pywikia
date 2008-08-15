# -*- coding: utf-8 -*-
"""
Program to (re)categorize images at commons.

The program uses commonshelper for category suggestions. The program consists of three parts.

1. prefetchThread - Fetches all the information
2. userThread - Gets input from the user
3. putThread - modifies the images

You need to install the Python Imaging Library http://www.pythonware.com/products/pil/ to get this program working

The program is far from finished. The framework is there, but still a lot has to be implemented:
1. The prefetch thread
    * Mostly finished.
    * Should add some error handling to cope with a slow toolserver
    * Should check if images with special chars work alright
    * Parameter to dont use commonshelper?
2. The user thread
    * Tkinter layout is awful atm
    * Tkinter have to implement most of the interaction
    * Tkinter category webbrowser link
    * Tkinter something with category auto completion (like the javascript in the search box)
3. The put thread
    * Nothing much to put atm
    * Should remove the Uncategorized template (+ redirects)
    * Should check if something is actually changed (set operations?)
"""
#
#  (C) Multichill 2008
#  (tkinter part loosely based on imagecopy.py)
# Distributed under the terms of the MIT license.
#
#
import os, sys, re, codecs
import urllib, httplib, urllib2
import catlib, thread
import time, threading
import wikipedia, config
import pagegenerators, add_text, Queue, StringIO      

exitProgram = False
#autonomous = False

category_blacklist = [u'Hidden categories']

class prefetchThread (threading.Thread):
    '''
    Class to fetch al the info for the user. This thread gets the imagepage, the commonshelper suggestions and the image.
    The thread puts this item in a queue. When there are no more pages left the thread puts a None object in the queue and exits.
    '''
    def __init__ (self, generator, prefetchToPutQueue):
        '''
        Get the thread ready
        '''
        self.generator = generator
        self.prefetchToPutQueue = prefetchToPutQueue
        self.currentCats = []
        self.commonshelperCats = []
        self.image = None
        self.imagepage = None
        self.pregenerator = pagegenerators.PreloadingGenerator(self.generator)
        threading.Thread.__init__ ( self )
        
    def run(self):
        global exitProgram
        #global autonomous
        for page in self.pregenerator:
            if exitProgram:
                break;            
            if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()) :
                self.imagepage = wikipedia.ImagePage(page.site(), page.title())
                self.imagepage.get()
                wikipedia.output(u'Working on ' + self.imagepage.title());
                self.currentCats = self.getCurrentCats(self.imagepage)
                self.commonshelperCats = self.filterCats(self.currentCats, self.getCommonshelperCats(self.imagepage))
                                    
                #if not autonomous:
                #    self.image = self.getImage(self.imagepage)
                #self.prefetchToUserQueue.put((self.imagepage, self.currentCats, self.commonshelperCats, self.image))

                if len(self.commonshelperCats) > 0:
                    for cat in self.commonshelperCats:
                        wikipedia.output(u' Found new cat: ' + cat);                       
                    self.prefetchToPutQueue.put((self.imagepage, self.commonshelperCats))

        self.prefetchToPutQueue.put(None)
        return
    
    def getCurrentCats(self, imagepage):
        '''
        Get the categories currently on the image
        '''
        result = []
        for cat in imagepage.categories():
            result.append(cat.titleWithoutNamespace())
        return result
    
    def getCommonshelperCats(self, imagepage):
        '''
        Get category suggestions from commonshelper. Parse them and return a list of suggestions.        
        '''
        parameters = urllib.urlencode({'i' : imagepage.titleWithoutNamespace().encode('utf-8'), 'r' : 'on', 'go-clean' : 'Find+Categories', 'cl' : 'li'})
        commonsenseRe = re.compile('^#COMMONSENSE(.*)#USAGE(\s)+\((?P<usage>(\d)+)\)(.*)#KEYWORDS(\s)+\((?P<keywords>(\d)+)\)(.*)#CATEGORIES(\s)+\((?P<catnum>(\d)+)\)\s(?P<cats>(.*))\s#GALLERIES(\s)+\((?P<galnum>(\d)+)\)(.*)#EOF$', re.MULTILINE + re.DOTALL)

        gotInfo = False;

        while(not gotInfo):
            try:
                commonsHelperPage = urllib.urlopen("http://toolserver.org/~daniel/WikiSense/CommonSense.php?%s" % parameters)
                matches = commonsenseRe.search(commonsHelperPage.read().decode('utf-8'))
                gotInfo = True;
            except IOError:
                wikipedia.output(u'Got an IOError, let\'s try again')
            except socket.timeout:
                wikipedia.output(u'Got a timeout, let\'s try again')                

        if matches:
            if(matches.group('catnum') > 0):
                return matches.group('cats').splitlines()
        else:            
            return []
        
    def filterCats(self, currentCats, commonshelperCats):
        '''
        Remove the current categories from the suggestions and remove blacklisted cats.
        '''
        result = []
        toFilter = ""

        for cat in currentCats:
            cat = cat.replace('_',' ')
            toFilter = toFilter + "[[Category:" + cat + "]]\n"
        for cat in commonshelperCats:
            cat = cat.replace('_',' ')
            toFilter = toFilter + "[[Category:" + cat + "]]\n"
        parameters = urllib.urlencode({'source' : toFilter.encode('utf-8'), 'bot' : '1'})
        filterCategoriesPage = urllib.urlopen("http://toolserver.org/~multichill/filtercats.php?%s" % parameters)
        #print filterCategoriesPage.read().decode('utf-8')
        filterCategoriesRe = re.compile('\[\[Category:([^\]]*)\]\]')
        result = filterCategoriesRe.findall(filterCategoriesPage.read().decode('utf-8'))
        #print matches
        '''
            if matches:
                print "Found matches"
                if(matches.group('cats') > 0):
                    print matches.group('cats').splitlines()
                    '''
        '''
                
        #currentCatsSet = set(currentCats)
        for cat in commonshelperCats:
            cat = cat.replace('_',' ')
            if (cat not in currentCatsSet) and (cat not in category_blacklist):
                result.append(cat)
        '''
        return list(set(result))
    
    def getImage(self, imagepage):
        '''
        Get the image from the wiki
        '''
        url = imagepage.fileUrl()
        uo = wikipedia.MyURLopener()
          
        file = uo.open(url)

        if 'text/html' in file.info().getheader('Content-Type'):
            wikipedia.output(u'Couldn\'t download the image: the requested URL was not found on this server.')
            return
        
        image = file.read()             
        file.close()
     
        return image                           

class putThread (threading.Thread):
    '''
    class to do the actual changing of images
    '''
    def __init__ (self, userToPutQueue):        
        self.userToPutQueue = userToPutQueue
        self.item = None
        self.imagepage = None
        self.newcats = []
        self.newtext = u''
        threading.Thread.__init__ ( self )
        
    def run(self):        

        while True:
            self.item = self.userToPutQueue.get()            
            if self.item is None:                
                break
            else:
                (self.imagepage, self.newcats)=self.item
                self.newtext = wikipedia.removeCategoryLinks(self.imagepage.get(), self.imagepage.site())
                self.newtext = self.removeUncat(self.newtext) + u'{{subst:chc}}\n'
                for category in self.newcats:
                    self.newtext = self.newtext + u'[[Category:' + category + u']]\n'
                    
                wikipedia.showDiff(self.imagepage.get(), self.newtext)
                #Should change this for not autonomous operation.
                #self.imagepage.put(self.newtext, u'Image is categorized by a bot using data from [[Commons:Tools#CommonSense|CommonSense]]')
        return
    def removeUncat(self, oldtext = u''):
        result = u''
        result = re.sub(u'\{\{\s*([Uu]ncat(egori[sz]ed( image)?)?|[Nn]ocat|[Nn]eedscategory)[^}]*\}\}', u'', oldtext)        
        result = re.sub(u'<!-- Remove this line once you have added categories -->', u'', result)
        #wikipedia.showDiff(oldtext, result)
        return result      
        
def main(args):
    '''
    Main loop. Get a generator. Set up the 3 threads and the 2 queue's and fire everything up.
    '''
    generator = None;
    
    genFactory = pagegenerators.GeneratorFactory()
    #global autonomous
    site = wikipedia.getSite(u'commons', u'commons')
    wikipedia.setSite(site)
    for arg in wikipedia.handleArgs():
        if arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(site, wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(site, arg[6:])]
        elif arg == '-autonomous':
            autonomous = True
        else:
            generator = genFactory.handleArg(arg)
    if not generator:
        generator = pagegenerators.CategorizedPageGenerator(catlib.Category(site, u'Category:Media needing categories'))
        #raise add_text.NoEnoughData('You have to specify the generator you want to use for the script!')


    prefetchToPutQueue=Queue.Queue()    
    
    # Start the prefetch thread
    prefetchThread(generator, prefetchToPutQueue).start()
 
    # Start the user thread
    # userThread(prefetchToUserQueue, userToPutQueue).start()

    # Start the put thread
    putThread(prefetchToPutQueue).start()

    # Wait for all threads to finish    
    for openthread in threading.enumerate():
        if openthread != threading.currentThread():
            openthread.join()        
    wikipedia.output(u'All threads are done')    

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
