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

from Tkinter import *
from PIL import Image, ImageTk
import os, sys, re, codecs
import urllib, httplib, urllib2
import catlib, thread, webbrowser
import time, threading
import wikipedia, config
import pagegenerators, add_text, Queue, StringIO      

exitProgram = 0

class prefetchThread (threading.Thread):
    '''
    Class to fetch al the info for the user. This thread gets the imagepage, the commonshelper suggestions and the image.
    The thread puts this item in a queue. When there are no more pages left the thread puts a None object in the queue and exits.
    '''
    def __init__ (self, generator, prefetchToUserQueue):
        '''
        Get the thread ready
        '''
        self.generator = generator
        self.prefetchToUserQueue = prefetchToUserQueue
        self.currentCats = []
        self.commonshelperCats = []
        self.image = None
        self.imagepage = None
        self.pregenerator = pagegenerators.PreloadingGenerator(self.generator)
        threading.Thread.__init__ ( self )
        
    def run(self):

        global exitProgram        
        for page in self.pregenerator:
            if exitProgram != 0:
                break;            
            if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()) :
                self.imagepage = wikipedia.ImagePage(page.site(), page.title())
                self.imagepage.get()
                self.currentCats = self.getCurrentCats(self.imagepage)
                self.commonshelperCats = self.filterCommonsHelperCats(self.currentCats, self.getCommonshelperCats(self.imagepage))
                self.image = self.getImage(self.imagepage)
                self.prefetchToUserQueue.put((self.imagepage, self.currentCats, self.commonshelperCats, self.image))
        self.prefetchToUserQueue.put(None)
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
        parameters = urllib.urlencode({'i' : imagepage.titleWithoutNamespace(), 'r' : 'on', 'go-clean' : 'Find+Categories'})        
        commonsHelperPage = urllib.urlopen("http://tools.wikimedia.de/~daniel/WikiSense/CommonSense.php?%s" % parameters)        
        
        commonsenseRe = re.compile('^#COMMONSENSE(.*)#USAGE(\s)+\((?P<usage>(\d)+)\)(.*)#KEYWORDS(\s)+\((?P<keywords>(\d)+)\)(.*)#CATEGORIES(\s)+\((?P<catnum>(\d)+)\)\s(?P<cats>(.*))\s#GALLERIES(\s)+\((?P<galnum>(\d)+)\)(.*)#EOF$', re.MULTILINE + re.DOTALL)
        matches = commonsenseRe.search(commonsHelperPage.read())

        if matches:
            if(matches.group('catnum') > 0):
                return matches.group('cats').splitlines()
        else:            
            return []
        
    def filterCommonsHelperCats(self, currentCats, commonshelperCats):
        '''
        Remove the current categories from the suggestions.
        '''
        result = []
        currentCatsSet = set(currentCats)
        for cat in commonshelperCats:
            cat = cat.replace('_',' ')
            if cat not in currentCatsSet:
                result.append(cat)
        return result
    
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
    
class userThread (threading.Thread):    
    def __init__ (self, prefetchToUserQueue, userToPutQueue):
        self.prefetchToUserQueue = prefetchToUserQueue
        self.userToPutQueue = userToPutQueue
        self.item = None
        self.imagepage = None
        self.image = None
        self.currentCats = []
        self.commonshelperCats = []
        self.newCats = []        
        self.skip = 0
        
        threading.Thread.__init__ ( self )
        
    def run(self):
        
        global exitProgram
        while exitProgram == 0:
            self.item = self.prefetchToUserQueue.get()           
            if self.item is None:                                
                break
            else:
                (self.imagepage, self.currentCats, self.commonshelperCats, self.image) = self.item
                (self.skip, exitProgram, self.newCats) = Tkdialog(self.imagepage.titleWithoutNamespace(), self.image, self.imagepage.get(), self.currentCats, self.commonshelperCats, self.imagepage.permalink()).run()                

                if not self.skip:
                    self.userToPutQueue.put((self.imagepage, self.newCats))
        self.userToPutQueue.put(None)
        return

class putThread (threading.Thread):
    '''
    class to do the actual changing of images
    '''
    def __init__ (self, userToPutQueue):        
        self.userToPutQueue = userToPutQueue
        threading.Thread.__init__ ( self )
        
    def run(self):        
        item = None
        imagepage = None
        newtext = u''
        while True:
            item = self.userToPutQueue.get()            
            if item is None:                
                break
            else:
                (imagepage, newtext)=item
                #wikipedia.showDiff(imagepage.get(), newtext)
                #imagepage.put(newtext, u'Recat by bot')
        return

class Tkdialog:
    '''
    The Tk dialog presented to the user. The user can add and remove categories. View the images in a webbrowser, skip the image, apply the changes or exit.
    '''
    def __init__(self, image_title = u'', image = None, pagetext=u'', currentCats = [], commonsHelperCats = [], url= ''):
        self.newCats = currentCats
        self.url = url
        self.skip = 0
        self.exit = 0
        self.root=Tk()
        self.root.title(image_title)
        w = 1600 #image1.width()
        h = 900 #image1.height()
        x = 50
        y = 50
        self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.root.rowconfigure( 0, weight = 1 )
        self.root.columnconfigure( 0, weight = 1 )

        image1 = self.getImage(image, 800, 600)                 
               
        panel1 = Label(self.root, image=image1)
        panel1.grid(row=0, column=2, rowspan=11, columnspan=11)
        panel1.image = image1                

        self.cb = []
        self.cbstate = []
        self.entry = []
        for i in range(0, 10):
            self.cbstate.append(IntVar())
            self.cb.append(Checkbutton (self.root, variable=self.cbstate[i]))
            self.entry.append(Entry (self.root, width=50))            
            self.cb[i].grid(row=i, column=0)
            self.entry[i].grid(row=i, column=1)

        catindex = 0

        for cat in currentCats:
            self.entry[catindex].delete(0, END)            
            self.entry[catindex].insert(0, cat)
            self.entry[catindex].config(background="green")
            self.cb[catindex].select()
            catindex = catindex + 1            
        
        for cat in commonsHelperCats:
            self.entry[catindex].delete(0, END)            
            self.entry[catindex].insert(0, cat)
            self.entry[catindex].config(background="yellow")
            self.cb[catindex].deselect()
            catindex = catindex + 1

        textarea=Text(self.root)
        scrollbar=Scrollbar(self.root, orient=VERTICAL)
        textarea.insert(END, pagetext.encode('utf-8'))
        textarea.config(state=DISABLED, height=12, width=80, padx=0, pady=0, wrap=WORD, yscrollcommand=scrollbar.set)

        scrollbar.config(command=textarea.yview)

        browserButton=Button(self.root, text='View in browser', command=self.openInBrowser)
        skipButton=Button(self.root, text="Skip", command=self.skipFile)
        okButton=Button(self.root, text="OK", command=self.okFile)
        exitButton=Button(self.root, text="EXIT", command=self.exitProgram)      
        
        textarea.grid(row=12, column=4, columnspan=10)
        scrollbar.grid(row=12, column=3)
        
        okButton.grid(row=20, column=0, rowspan=2)
        skipButton.grid(row=20, column=1, rowspan=2)
        browserButton.grid(row=20, column=2, rowspan=2)
        exitButton.grid(row=20, column=3, rowspan=2)
                
    def getImage(self, image, width, height):        
        output = StringIO.StringIO(image)
        image2 = Image.open(output)
        image2.thumbnail((width, height))
        imageTk = ImageTk.PhotoImage(image2)
        return imageTk

    def okFile(self):
        '''
        The user pressed the OK button.
        '''
        #Read what the user has entered
        self.root.destroy()
        
    def skipFile(self):
        '''
        The user pressed the Skip button.
        '''
        self.skip=1
        self.root.destroy()
        
    def openInBrowser(self):
        '''
        The user pressed the View in browser button.
        '''
        webbrowser.open(self.url)

    def exitProgram(self):
        '''
        Exit the program
        '''
        self.skip=1
        self.exit=1
        self.root.destroy()
        
    def run (self):
        self.root.mainloop()
        return (self.skip, self.exit, self.newCats)
    
def main(args):
    '''
    Main loop. Get a generator. Set up the 3 threads and the 2 queue's and fire everything up.
    '''
    generator = None;
    genFactory = pagegenerators.GeneratorFactory()

    site = wikipedia.getSite(u'commons', u'commons')
    wikipedia.setSite(site)
    for arg in wikipedia.handleArgs():
        if arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(site, wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(site, arg[6:])]
        elif arg == '-always':
            always = True
        else:
            generator = genFactory.handleArg(arg)
    if not generator:
        generator = pagegenerators.CategorizedPageGenerator(catlib.Category(site, u'Category:Media needing categories'))
        #raise add_text.NoEnoughData('You have to specify the generator you want to use for the script!')

    prefetchToUserQueue=Queue.Queue()    
    userToPutQueue=Queue.Queue()
    
    # Start the prefetch thread
    prefetchThread(generator, prefetchToUserQueue).start()
 
    # Start the user thread
    userThread(prefetchToUserQueue, userToPutQueue).start()

    # Start the put thread
    putThread(userToPutQueue).start()

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
