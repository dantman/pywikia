# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Graphical Entertainment Project to share images across the wikia in the project.
Info: http://en.anime.wikia.com/wiki/Project:Bots/ImageMirror
"""

import sys, re, os
import wikipedia, pagegenerators, catlib, config, upload

msg = {
       'en':u'[[w:c:Anime:Project:Bots/ImageMirror|ImageMirrorBot]].',
       }
class MirrorBot:
    def __init__(self):
        self.runOk = False;
        #Setup Familys for Wikia Involved
        self.anime = wikipedia.getSite(code=u'en', fam=u'anime')
        wikipedia.setAction(wikipedia.translate(self.anime, msg))
        self.siteList = []
        self.imageList = []
        #Get Project Wiki Listing
        wikiaIds = []
        page = wikipedia.Page(self.anime, u'Bots/Wiki', None, 4)#4=Project Namespace
        try:
            text = page.get()
            r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
            text = re.sub(r, u'', text)
            r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
            text = re.sub(r, u'', text)
            r = re.compile(u'\n', re.UNICODE | re.DOTALL)
            wikilist = re.split(r, text)
            r = re.compile(u'^#|^\s*$|^\[', re.UNICODE | re.MULTILINE | re.DOTALL)
            for wiki in wikilist:
                if not re.match(r, wiki):
                    wikiaIds.append(wiki)
        except wikipedia.NoPage:
            return False
        
        for wiki in wikiaIds:
            self.siteList.append(wikipedia.getSite(code=u'en', fam=wiki))
        
        #Get Image Info List
        page = wikipedia.Page(self.anime, u'Bots/ImageMirror/Images', None, 4)#4=Project Namespace
        try:
            text = page.get()
            r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
            text = re.sub(r, u'', text)
            r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
            text = re.sub(r, u'', text)
            r = re.compile(u'\n', re.UNICODE | re.DOTALL)
            images = re.split(r, text)
            r = re.compile(u'^#|^\s*$', re.UNICODE | re.MULTILINE | re.DOTALL)
            for image in images:
                if not re.match(r, image):
                    self.imageList.append(image)
        except wikipedia.NoPage:
            return False
        self.runOk = True;

        #Mirror the Images category and all subcategorys to all the wiki.
        ImageCategorys = []
        cat = catlib.Category(self.anime, u'Category:Images')
        ImageCategorys.append(cat)

        catlist = cat.subcategories(True)

        for category in catlist:
            ImageCategorys.append(category)

        for category in ImageCategorys:
            categorySource = u'{{networkMirror|%s|anime|category}}\n%s' % (category.title(),category.get())

            if categorySource != u'':
                for site in self.siteList:
                    siteCategory = catlib.Category(site, category.title())
                    siteSource = u''
                    try:
                        siteSource = siteCategory.get()
                    except wikipedia.NoPage:
                        wikipedia.output(u'Site %s has no %s category, creating it' % (site, category.title()))
                    if siteSource != categorySource:
                        wikipedia.output(u'Site \'%s\' category status: Needs Updating' % site)
                        wikipedia.output(u'Updating category on %s' % site)
                        siteCategory.put(categorySource)
                    else:
                        wikipedia.output(u'Site \'%s\' category status: Ok' % site)
            else:
                wikipedia.output(u'Category %s is blank, skipping category' % category.title())

        #Anime should only be in the list after categorys have been done.
        self.siteList.append(self.anime)
        
    def run(self):
        if self.runOk:
            for image in self.imageList:
                self.doImage(image)
            return True
        else:
            return False
        
    def doImage(self, image):
        r = re.compile(u'\|', re.UNICODE | re.DOTALL)
        data = re.split(r, image)
        imageName = data[0]
        newImageName = data[0]
        r = re.compile(u'^\s*$', re.UNICODE | re.DOTALL)
        if len(data) >= 2 and not re.match(r, data[1]):
            newImageName = data[1]
        sourceWiki = u'anime'
        if len(data) >= 3:
            sourceWiki = data[2]
        exclusionMode = u'normal'
        if len(data) >= 4:
            exclusionMode = data[3]
        exclusionInfo = u''
        if len(data) >= 5:
            exclusionInfo = data[4]
        sourceSite = None
        outputSites = []
        sourceImage = None
        sourcePage = None
        
        wikipedia.output(u'Doing Image %s' % imageName)
        for site in self.siteList:
            if site.family.name == sourceWiki:
                sourceSite = site
            if exclusionMode == u'normal':
                outputSites.append(site)
            elif exclusionMode == u'include':
                r = re.compile(u',', re.UNICODE | re.DOTALL)
                includes = re.split(r, exclusionInfo)
                if site.family.name in includes:
                    outputSites.append(site)
            elif exclusionMode == u'exclude':
                r = re.compile(u',', re.UNICODE | re.DOTALL)
                excludes = re.split(r, exclusionInfo)
                if site.family.name not in includes:
                    outputSites.append(site)
            else:
                wikipedia.output(u'Unknown exclusion mode. Skiping %s.' % imageName)
                return False
        if sourceSite == None:
            wikipedia.output(u'No source site found. Skiping %s.' % imageName)
            return False
        
        try:
            sourceDescriptionPage = wikipedia.Page(sourceSite, imageName, None, 6)#6=Image Namespace
            sourceImagePage = wikipedia.ImagePage(sourceSite, sourceDescriptionPage.title())
        except wikipedia.NoPage:
            wikipedia.output(u'No source page found. Skiping %s.' % imageName)
            return False
        
        sourceURL = sourceImagePage.fileUrl()
        if '://' not in sourceURL:
            sourceURL = u'http://%s%s' % (sourceSite.hostname(), sourceURL)
        
        # Get file contents
        uo = wikipedia.MyURLopener()
        sourceFile = uo.open(sourceURL,"rb")
        wikipedia.output(u'Reading file %s' % sourceURL)
        sourceContents = sourceFile.read()
        if sourceContents.find("The requested URL was not found on this server.") != -1:
            wikipedia.output("Couldn't download the image. Skiping.")
            return False
        sourceFile.close()
        
        #Setup Description Page
        pageDescription = sourceDescriptionPage.get()
        r = re.compile(u'== Summary ==\n?')
        if re.search(r, pageDescription):
            pageDescription = re.sub(r, u'', pageDescription)
        
        mirrorText = u'{{networkMirror|%s|%s}}' % (imageName,sourceSite.family.name)
        comm = re.compile(u'({{commons(\|[^{}]*)?}})', re.IGNORECASE)
        if re.search(comm, pageDescription):
            pageDescription = re.sub(comm, u'\\1\n%s' % mirrorText, pageDescription)
        else:
            pageDescription = u'%s%s' % (mirrorText, pageDescription)
        pageDescription = u'== Summary ==\n%s' % pageDescription
        
        for site in outputSites:
            if sourceSite.family.name != site.family.name or imageName != newImageName:
                doUpload = False
                doDescription = False
                
                try:
                    siteDescriptionPage = wikipedia.Page(site, newImageName, None, 6)#6=Image Namespace
                    siteImagePage = wikipedia.ImagePage(site, siteDescriptionPage.title())
                    
                    siteURL = siteImagePage.fileUrl()
                    if '://' not in siteURL:
                        siteURL = u'http://%s%s' % (site.hostname(), siteURL)
                
                    uo2 = wikipedia.MyURLopener()
                    siteFile = uo2.open(siteURL,"rb")
                    wikipedia.output(u'Reading file %s' % siteURL)
                    siteContents = siteFile.read()
                    if sourceContents.find("The requested URL was not found on this server.") != -1:
                        wikipedia.output("Couldn't download the image at new location.")
                        doUpload = True
                        break
                    siteFile.close()
                    
                    if siteContents != sourceContents:
                        doUpload = True
                    
                    if siteDescriptionPage.get() != pageDescription:
                        doDescription = True
                    
                except wikipedia.NoPage:
                    doUpload = True
                    doDescription = True
                
                if doUpload:
                    bot = upload.UploadRobot(url = sourceURL, useFilename = newImageName, keepFilename = True, verifyDescription = False, description = msg['en'], targetSite = site, urlEncoding = sourceSite.encoding())
                    bot.run()
                if doDescription:
                    siteDescriptionPage.put(pageDescription)
                    
        
if __name__ == "__main__":
    try:
        bot = MirrorBot()
        bot.run()
    finally:
        wikipedia.stopme()
