# -*- coding: utf-8 -*-
"""
Script to copy files from a local Wikimedia wiki to Wikimedia Commons
using CommonsHelper to not leave any information out and CommonSense
to automatically categorise the file. After copying, a NowCommons
template is added to the local wiki's file. It uses a local exclusion
list to skip files with templates not allow on Wikimedia Commons. If no
categories have been found, the file will be tagged on Commons.

This bot uses a graphical interface and may not work from commandline
only environment.

Requests for improvement for CommonsHelper output should be directed to
Magnus Manske at his talk page. Please be very specific in your request
(describe current output and expected output) and note an example file,
so he can test at: [[de:Benutzer Diskussion:Magnus Manske]]. You can
write him in German and English.

Examples

Work on a single image
 python imagecopy.py -page:Image:<imagename>
Work on the 100 newest images:
 python imagecopy.py -newimages:100
Work on all images in a category:<cat>
 python imagecopy.py -cat:<cat>
Work on all images which transclude a template
 python imagecopy.py -transcludes:<template>

See pagegenerators.py for more ways to get a list of images.
By default the bot works on your home wiki (set in user-config)

Known issues/FIXMEs (no critical issues known):
* make it use pagegenerators.py
** Implemented in rewrite
* Some variable names are in Spanish, which makes the code harder to read.
** Almost all variables are now in English
* Depending on sorting within a file category, the "next batch" is sometimes
  not working, leading to an endless loop
** Using pagegenerators now
* Different wikis can have different exclusion lists. A parameter for the
  exclusion list Uploadbot.localskips.txt would probably be nice.
* Bot should probably use API instead of query.php
** Api? Query? Wikipedia.py!
* Should request alternative name if file name already exists on Commons
** Implemented in rewrite
* Exits after last file in category was processed, aborting all pending
  threads.
** Implemented proper threading in rewrite
* Should take user-config.py as input for project and lang variables
** Implemented in rewrite
* Should require a Commons user to be present in user-config.py before
  working
* Should probably have an input field for additional categories
* Should probably have an option to change uploadtext with file
* required i18n options for NowCommons template (f.e. {{subst:ncd}} on
  en.wp. Currently needs customisation to work properly. Bot was tested
  succesfully on nl.wp (12k+ files copied and deleted locally) and en.wp
  (about 100 files copied and SieBot has bot approval for tagging {{ncd}}
  with this bot)
* {{NowCommons|xxx}} requires the namespace prefix Image: on most wikis
  and can be left out on others. This needs to be taken care of when
  implementing i18n
* This bot should probably get a small tutorial at meta with a few
  screenshots.
"""
#
# Based on upload.py by:
# (C) Rob W.W. Hooft, Andre Engels 2003-2007
# (C) Wikipedian, Keichwa, Leogregianin, Rikwade, Misza13 2003-2007
#
# New bot by:
# (C) Kyle/Orgullomoore, Siebrand Mazeland 2007
#
# Another rewrite by:
#  (C) Multichill 2008
# 
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#

from Tkinter import *
import os, sys, re, codecs
import urllib, httplib, urllib2
import catlib, thread, webbrowser
import time, threading
import wikipedia, config
import pagegenerators, add_text
from upload import *
NL=''
                
def pageTextPost(url,postinfo):
    print url
    m=re.search(ur'http://(.*?)(/.*)',url)
    if m==None:
            return
    else:
            domain=m.group(1)
            path=m.group(2)
            
    h = httplib.HTTP(domain)
    h.putrequest('POST', path)
    h.putheader('Host', domain)
    h.putheader('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7')
    h.putheader('Content-Type', 'application/x-www-form-urlencoded')
    h.putheader('Content-Length', str(len(postinfo)))
    h.endheaders()
    h.send(postinfo)
    errcode, errmsg, headers = h.getreply()
    data = h.getfile().read() # Obtener el HTML en bruto/wiki?title=Special:Userlogin&action=submitlogin&type=signup HTTP/1.1

    return data

class imageTransfer (threading.Thread):

    def __init__ ( self, imagePage, newname):
        self.imagePage = imagePage
        self.newname = newname
        threading.Thread.__init__ ( self )
        
    def run(self):
        tosend={'language':str(self.imagePage.site().language()),
                'image':self.imagePage.titleWithoutNamespace().encode('utf-8'),
                'newname':urllib.quote(self.newname.encode('utf-8')),
                'project':str(self.imagePage.site().family.name),
                'commonsense':'1',
                'doit':'Get+text'}
        #for k in tosend.keys():
        #    tosend[k]=tosend[k].encode('utf-8')
        tosend=urllib.urlencode(tosend)
        print tosend
        CH=pageTextPost('http://tools.wikimedia.de/~magnus/commonshelper.php', tosend)
        print 'Got CH desc.'
        wikipedia.output(CH);
        tablock=CH.split('<textarea ')[1].split('>')[0]
        CH=CH.split('<textarea '+tablock+'>')[1].split('</textarea>')[0]
        CH=CH.replace('&times;', '×')
        CH=CH.decode('utf-8')
        ## if not '[[category:' in CH.lower():
        # I want every picture to be tagged with the bottemplate so i can check my contributions later.
        CH=u'\n\n{{BotMoveToCommons|'+ self.imagePage.site().language() + '.' + self.imagePage.site().family.name +'}}'+CH
        #urlEncoding='utf-8'
        bot = UploadRobot(url=self.imagePage.fileUrl(), description=CH, useFilename=self.newname, keepFilename=True, verifyDescription=False, ignoreWarning = True, targetSite = wikipedia.getSite('commons', 'commons'))
        bot.run()
    
        #add {{NowCommons}}, first force to get the page so we dont run into edit conflicts
        imtxt=self.imagePage.get(force=True)
        if self.newname!=self.imagePage.titleWithoutNamespace():
            self.imagePage.put(imtxt+u'\n\n{{NowCommons|'+self.newname.decode('utf-8')+'}}', u'{{NowCommons}}')
            print 'Nowcommons with different name.\n'
        else:
            self.imagePage.put(imtxt+u'\n\n{{NowCommons}}', u'{{NowCommons}}')
            print 'Nowcommons.\n'
        return
        
#-label ok skip view
#textarea
archivo=wikipedia.config.datafilepath("Uploadbot.localskips.txt")
try:
    open(archivo, 'r')
except IOError:
    tocreate=open(archivo, 'w')
    tocreate.write("{{NowCommons")
    tocreate.close()
    
def getautoskip():
    '''
    Get a list of templates to skip.
    '''
    f=codecs.open(archivo, 'r', 'utf-8')
    txt=f.read()
    f.close()
    toreturn=txt.split('{{')[1:]
    return toreturn
    
class Tkdialog:
    def __init__(self, image_title, content, uploader, url, templates, commonsconflict=0):
        self.root=Tk()
        #"%dx%d%+d%+d" % (width, height, xoffset, yoffset)
        #Always appear the same size and in the bottom-left corner
        self.root.geometry("600x200+100-100")
        #self.nP=wikipediaPage
        self.root.title(image_title)
        self.changename=''
        self.skip=0
        self.url=url
        self.uploader="Unkown"
        #uploader.decode('utf-8')
        scrollbar=Scrollbar(self.root, orient=VERTICAL)
        label=Label(self.root,text=u"Enter new name or leave blank.")
        imageinfo=Label(self.root, text='Uploaded by '+uploader+'.')
        textarea=Text(self.root)
        textarea.insert(END, content.encode('utf-8'))
        textarea.config(state=DISABLED, height=8, width=40, padx=0, pady=0, wrap=WORD, yscrollcommand=scrollbar.set)
        scrollbar.config(command=textarea.yview)
        self.entry=Entry(self.root)
        
        self.templatelist=Listbox(self.root, bg="white", height=5)
                
        for template in templates:
            self.templatelist.insert(END, template)
        autoskipButton=Button(self.root, text="Add to AutoSkip", command=self.add2autoskip)
        browserButton=Button(self.root, text='View in browser', command=self.openInBrowser)
        skipButton=Button(self.root, text="Skip", command=self.skipFile)
        okButton=Button(self.root, text="OK", command=self.okFile)
        
        ##Start grid
        label.grid(row=0)
        okButton.grid(row=0, column=1, rowspan=2)
        skipButton.grid(row=0, column=2, rowspan=2)
        browserButton.grid(row=0, column=3, rowspan=2)
        
        self.entry.grid(row=1)

        
        textarea.grid(row=2, column=1, columnspan=3)
        scrollbar.grid(row=2, column=5)
        self.templatelist.grid(row=2, column=0)
        
        autoskipButton.grid(row=3, column=0)
        imageinfo.grid(row=3, column=1, columnspan=4)

        
    def okFile(self):
        '''
        The user pressed the OK button.
        '''
        self.changename=self.entry.get()
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
    def add2autoskip(self):
        '''
        The user pressed the Add to AutoSkip button.
        '''
        templateid=int(self.templatelist.curselection()[0]) 
        template=self.templatelist.get(templateid)
        toadd=codecs.open(archivo, 'a', 'utf-8')
        toadd.write('{{'+template)
        toadd.close()
        self.skipFile()
        
    def getnewname(self):
        '''
        Activate the dialog and return the new name and if the image is skipped.
        '''
        self.root.mainloop()
        return (self.changename, self.skip)

def doiskip(pagetext):
    '''
    Skip this image or not.
    Returns True if the image is on the skip list, otherwise False
    '''
    saltos=getautoskip()
    #print saltos
    for salto in saltos:
        rex=ur'\{\{\s*['+salto[0].upper()+salto[0].lower()+']'+salto[1:]+'(\}\}|\|)'
        #print rex
        if re.search(rex, pagetext):
            return True
    return False

def main(args):
    generator = None;
    #newname = "";
    imagepage = None;
    # Load a lot of default generators
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        if arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(wikipedia.getSite(), wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(wikipedia.getSite(), arg[6:])]
        elif arg == '-always':
            always = True
        else:
            generator = genFactory.handleArg(arg)
    if not generator:
        raise add_text.NoEnoughData('You have to specify the generator you want to use for the script!')

    pregenerator = pagegenerators.PreloadingGenerator(generator)

    for page in pregenerator:        
        if page.exists() and (page.namespace() == 6) and (not page.isRedirectPage()) :
            imagepage = wikipedia.ImagePage(page.site(), page.title())
            
            #First do autoskip.         
            if doiskip(imagepage.get()):
                wikipedia.output("Skipping " + page.title())
                skip = True            
            else:
                # The first upload is last in the list.
                (datetime, username, resolution, size, comment) = imagepage.getFileVersionHistory().pop()               
                while True:

                    # Do the Tkdialog to accept/reject and change te name        
                    (newname, skip)=Tkdialog(imagepage.titleWithoutNamespace(), imagepage.get(), username, imagepage.permalink(), imagepage.templates()).getnewname()
                
                    if skip:
                        wikipedia.output('Skipping this image')
                        break
                   
                    # Did we enter a new name?
                    if len(newname)==0:                
                        #Take the old name
                        newname=imagepage.titleWithoutNamespace()
                           
                    # Check if the image already exists
                    CommonsPage=wikipedia.Page(wikipedia.Site('commons', 'commons'), 'Image:'+newname)
                    
                    if not CommonsPage.exists():
                        break
                    else:
                        wikipedia.output('Image already exists, pick another name or skip this image')
                    # We dont overwrite images, pick another name, go to the start of the loop

            if not skip:
                imageTransfer(imagepage, newname).start()
                     
    wikipedia.output(u'Still ' + str(threading.activeCount()) + u' active threads, lets wait')    
    for openthread in threading.enumerate():
        if openthread != threading.currentThread():
            openthread.join()        
    wikipedia.output(u'All threads are done')    

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
