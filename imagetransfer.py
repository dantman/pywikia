# -*- coding: utf-8 -*-
"""
Script to copy images to Wikimedia Commons, or to another wiki.

Syntax:

    python imagetransfer.py pagename [-interwiki] [-targetLang:xx] -targetFamily:yy]

Arguments:

  -interwiki   Look for images in pages found through interwiki links.

  -tolang:xx   Copy the image to the wiki in language xx

  -tofamily:yy Copy the image to a wiki in the family yy

  -file:zz     Upload many files from textfile: [[Image:xx]]
                                                [[Image:yy]]

If pagename is an image description page, offers to copy the image to the
target site. If it is a normal page, it will offer to copy any of the images
used on that page, or if the -interwiki argument is used, any of the images
used on a page reachable via interwiki links.
"""
#
# (C) Andre Engels, 2004
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'

import re, sys, md5, urllib
import wikipedia, upload, config, pagegenerators

copy_message = {
    'en':u"This image was copied from %s. The original description was:\r\n\r\n%s",
    'de':u"Dieses Bild wurde von %s kopiert. Die dortige Beschreibung lautete:\r\n\r\n%s",
    'lt':u"Šis paveikslėlis buvo įkeltas iš %s. Originalus aprašymas buvo:\r\n\r\n%s",
    'nl':u"Afbeelding gekopieerd vanaf %s. De beschrijving daar was:\r\n\r\n%s",
    'pt':u"Esta imagem foi copiada de %s. A descrição original foi:\r\n\r\n%s",
}

nowCommonsTemplate = {
    'de': u'{{NowCommons|%s}}',
    'fr': u'{{Désormais sur Commons|%s}}',
    'en': u'{{NowCommons|Image:%s}}',
    'lt': u'{{NowCommons|Image:%s}}',
    'nl': u'{{NuCommons|%s}}',
    'pt': u'{{NowCommons|%s}}',
}

nowCommonsMessage = {
    'de': u'Datei ist jetzt auf Wikimedia Commons verfügbar.',
    'en': u'File is now available on Wikimedia Commons.',
    'lt': u'Failas įkeltas į Wikimedia Commons projektą.',
    'pt': u'Arquivo está agora na Wikimedia Commons.',
}

# Translations for license templates.
# Must only be given when they are in fact different.
licenseTemplates = {
    ('wikipedia:de', 'commons:commons'): {
        u'Bild-GFDL':                u'GFDL',
        u'Bild-GFDL-OpenGeoDB':      u'GFDL-OpenGeoDB',
        u'Bild-PD':                  u'PD',
        u'Bild-PD-alt':              u'PD-old',
        u'Bild-PD-Kunst':            u'PD-Art',
        u'Bild-PD-US':               u'PD-USGov',
    },
    ('wikipedia:fr', 'commons:commons'): {
        u'Domaine public':           u'PD'
    },
    ('wikipedia:pt', 'commons:commons'): {
        u'Domínio público':          u'PD',
    },        
}

class ImageTransferBot:
    def __init__(self, generator, targetSite = None, interwiki = False):
        self.generator = generator
        self.interwiki = interwiki
        self.targetSite = targetSite
    
    def transferImage(self, sourceImagePage, debug=False):
        """Gets a wikilink to an image, downloads it and its description,
           and uploads it to another wikipedia.
           Returns the filename which was used to upload the image
           This function is used by imagetransfer.py and by copy_table.py
        """
        sourceSite = sourceImagePage.site()
        if debug: print "--------------------------------------------------"
        if debug: print "Found image: %s"% imageTitle
        # need to strip off "Afbeelding:", "Image:" etc.
        # we only need the substring following the first colon
        filename = sourceImagePage.title().split(":", 1)[1]
        # Spaces might occur, but internally they are represented by underscores.
        # Change the name now, because otherwise we get the wrong MD5 hash.
        filename = filename.replace(' ', '_')
        # Also, the first letter should be capitalized
        # TODO: Don't capitalize on non-capitalizing wikis
        filename = filename[0].upper()+filename[1:]
        if debug: print "Image filename is: %s " % filename
        encodedFilename = filename.encode(sourceSite.encoding())
        md5sum = md5.new(encodedFilename).hexdigest()
        if debug: print "MD5 hash is: %s" % md5sum
        encodedFilename = urllib.quote(encodedFilename)
        # TODO: This probably doesn't work on all wiki families
        url = 'http://%s/upload/%s/%s/%s' % (sourceSite.hostname(), md5sum[0], md5sum[:2], encodedFilename)
        print "URL should be: %s" % url
        # localize the text that should be printed on the image description page
        try:
            description = sourceImagePage.get()
            # try to translate license templates
            if licenseTemplates.has_key((sourceSite.sitename(), self.targetSite.sitename())):
                for old, new in licenseTemplates[(sourceSite.sitename(), self.targetSite.sitename())].iteritems():
                    new = '{{%s}}' % new
                    old = re.compile('{{%s}}' % old)
                    description = wikipedia.replaceExceptNowikiAndComments(description, old, new)
            
            description = wikipedia.translate(self.targetSite, copy_message) % (sourceSite, description)
            # TODO: Only the page's version history is shown, but the file's
            # version history would be more helpful
            description += '\n\n' + sourceImagePage.getVersionHistoryTable()
            # add interwiki link
            if sourceSite.family == self.targetSite.family:
                description += "\r\n\r\n" + sourceImagePage.aslink(forceInterwiki = True)
        except wikipedia.NoPage:
            description=''
            print "Image does not exist or description page is empty."
        except wikipedia.IsRedirectPage:
            description=''
            print "Image description page is redirect."
        else:
            bot = upload.UploadRobot(url = url, description = description, targetSite = self.targetSite, urlEncoding = sourceSite.encoding())
            # try to upload
            targetFilename = bot.run()
            if targetFilename and self.targetSite.family.name == 'commons' and self.targetSite.lang == 'commons':
                # upload to Commons was successful
                reason = wikipedia.translate(sourceSite, nowCommonsMessage)
                # try to delete the original image if we have a sysop account
                if config.sysopnames.has_key(sourceSite.family.name) and config.sysopnames[sourceSite.family.name].has_key(sourceSite.lang):
                    if sourceImagePage.delete(reason):
                        return
                if nowCommonsTemplate.has_key(sourceSite.lang) and config.usernames.has_key(sourceSite.family.name) and config.usernames[sourceSite.family.name].has_key(sourceSite.lang):
                # add the nowCommons template.
                    wikipedia.output(u'Adding nowCommons template to %s' % sourceImagePage.title())
                    sourceImagePage.put(sourceImagePage.get() + '\n\n' + nowCommonsTemplate[sourceSite.lang] % targetFilename, comment = nowCommonsMessage[sourceSite.lang])

    def showImageList(self, imagelist):
        for i in range(len(imagelist)):
            image = imagelist[i]
            print "-"*60
            wikipedia.output(u"%s. Found image: %s"% (i, image.aslink()))
            try:
                # Show the image description page's contents
                wikipedia.output(image.get(throttle=False))
            except wikipedia.NoPage:
                try:
                    # Maybe the image is on the target site already
                    targetTitle = '%s:%s' % (self.targetSite.image_namespace(), image.title().split(':', 1)[1])
                    targetImage = wikipedia.Page(self.targetSite, targetTitle)
                    if targetImage.get(throttle=False):
                        wikipedia.output(u"Image is already on %s." % self.targetSite)
                        wikipedia.output(targetImage.get(throttle=False))
                    else:
                        print "Description empty."
                except wikipedia.NoPage:
                    print "Description empty."
                except wikipedia.IsRedirectPage:
                    print "Description page on Wikimedia Commons is redirect?!"
            except wikipedia.IsRedirectPage:
                print "Description page is redirect?!"

        print "="*60
    
    def run(self):
        for page in self.generator:
            if self.interwiki:
                imagelist = []
                for linkedPage in page.interwiki():
                    imagelist += linkedPage.imagelinks(followRedirects = True)
            elif page.isImage():
                imagelist = [page]
            else:
                imagelist = page.imagelinks(followRedirects = True)

            while len(imagelist)>0:
                self.showImageList(imagelist)
                if len(imagelist) == 1:
                    # no need to query the user, only one possibility
                    todo = 0
                else:
                    wikipedia.output(u"Give the number of the image to transfer.")
                    todo = wikipedia.input(u"To end uploading, press enter:")
                    if not todo:
                        break
                    todo=int(todo)
                if todo in range(len(imagelist)):
                    self.transferImage(imagelist[todo], debug = False)
                    # remove the selected image from the list
                    imagelist = imagelist[:todo] + imagelist[todo + 1:]
                else:
                    print("No such image number.")

def main():
    # if -file is not used, this temporary array is used to read the page title.
    pageTitle = []
    page = None
    gen = None
    interwiki = False
    targetLang = None
    targetFamily = None

    for arg in sys.argv[1:]:
    #for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'imagetransfer')
        if arg:
            if arg == '-interwiki':
                interwiki = True
            elif arg.startswith('-tolang:'):
                targetLang = arg[8:]
            elif arg.startswith('-tofamily:'):
                targetFamily = arg[10:]
            elif arg.startswith('-file'):
                if len(arg) == 5:
                    filename = wikipedia.input(u'Please enter the list\'s filename: ')
                else:
                    filename = arg[6:]
                gen = pagegenerators.TextfilePageGenerator(filename)
            else:
                pageTitle.append(arg)

    if not gen:
        # if the page title is given as a command line argument,
        # connect the title's parts with spaces
        if pageTitle != []:
            pageTitle = ' '.join(pageTitle)
            page = wikipedia.Page(wikipedia.getSite(), pageTitle)
        # if no page title was given as an argument, and none was
        # read from a file, query the user
        if not page:
            pageTitle = wikipedia.input(u'Which page to check:')
            page = wikipedia.Page(wikipedia.getSite(), pageTitle)
            # generator which will yield only a single Page
        gen = iter([page])

    if not targetLang and not targetFamily:
        targetSite = wikipedia.getSite('commons', 'commons')
    else:
        if not targetLang:
            targetLang = wikipedia.getSite().language
        if not targetFamily:
            targetFamily = wikipedia.getSite().family
        targetSite = wikipedia.Site(targetLang, targetFamily)
    bot = ImageTransferBot(gen, interwiki = interwiki, targetSite = targetSite)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
