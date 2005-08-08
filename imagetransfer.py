"""
Script to copy images to Wikimedia Commons, or to another wiki.

Syntax:

    python imagetransfer.py pagename [-interwiki] [-targetLang:xx] -targetFamily:yy]

Arguments:

  -interwiki   Look for images in pages found through interwiki links.

  -tolang:xx   Copy the image to the wiki in language xx

  -tofamily:yy Copy the image to a wiki in the family yy

If pagename is an image description page, offers to copy the image to the
target site. If it is a normal page, it will offer to copy any of the images
used on that page, or if the -interwiki argument is used, any of the images
used on a page reachable via interwiki links.
"""
#
# (C) Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'

import re, sys, string
import httplib
import wikipedia, lib_images

class ImageTransferBot:
    def __init__(self, generator, targetSite = None, interwiki = False):
        self.generator = generator
        self.interwiki = interwiki
        self.targetSite = targetSite
        self.targetSite.forceLogin()

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

            while len(imagelist)>0:
                wikipedia.output(u"Give the number of the image to transfer.")
                todo = wikipedia.input(u"To end uploading, press enter:")
                if not todo:
                    break
                todo=int(todo)
                if todo in range(len(imagelist)):
                    lib_images.transfer_image(imagelist[todo], self.targetSite, debug = True)
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
                gen = pagegenerators.TextfileGenerator(filename)
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
            pageTitle = wikipedia.input(u'Which page to check: ')
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
