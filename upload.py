"""
Script to upload images to wikipedia.

Arguments:

  -lang:xx Log in to the given wikipedia language to upload to

  -keep    Keep the filename as is

  -wiki:xx The page is not a URL or filename, but the name of the
           file on another wikipedia, namely xx:. Do NOT include
           'Image:' or similar as name of the file.

If any other arguments are given, the first is the URL or filename
to upload, and the rest is a proposed description to go with the
upload. If none of these are given, the user is asked for the
file or URL to upload.
  
The script will ask for the location of an image, and for a description.
It will then send the image to wikipedia.
"""
#
# (C) Rob W.W. Hooft, Andre Engels 2003-2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'

import os, sys, re
import wikipedia, lib_images, config

class UploadRobot:
    def __init__(self, filename, description, wiki, keep):
        self.filename = filename
        self.description = description
        self.wiki = wiki
        #print wiki
        self.keep = keep
        
        mysite = wikipedia.getSite()
        if not mysite.loggedin():
            print "You must be logged in to upload images"
            sys.exit(1)
    
    def filenameOK(self):
        '''
        Returns true iff the filename references an online site or to an
        existing local file.
        '''
        return self.filename != '' and ('://' in self.filename or os.path.exists(self.filename))
        
    def run(self):
        if self.wiki:
            mysite = wikipedia.getSite()
            othersite = mysite.getSite(self.wiki)
            while not self.filename:
                wikipedia.output(u'No input filename given.')
                self.filename = wikipedia.input(u'Give filename:')
            full_image_name = "%s:%s" % (othersite.image_namespace(), self.filename)
            pl = wikipedia.PageLink(othersite, full_image_name)
            lib_images.transfer_image(pl)
        else:
            while not self.filenameOK():
                if not self.filename:
                    wikipedia.output(u'No input filename given')
                else:
                    wikipedia.output(u'Invalid input filename given. Try again.')
                self.filename = wikipedia.input(u'File or URL where image is now:')
         
            lib_images.get_image(self.filename, None, self.description, self.keep)

def main(args):
    filename = ''
    description = []
    keep = False
    wiki = ''

    for arg in args:
        if wikipedia.argHandler(arg):
            print arg
            if arg.startswith('-keep'):
                keep = True
            elif arg.startswith('-wiki:'):
                wiki=arg[6:]
            elif filename == '':
                filename = arg
            else:
                description.append(arg)
    description = ' '.join(description)
    bot = UploadRobot(filename, description, wiki, keep)
    bot.run()

try:
    main(sys.argv[1:])
finally:
    wikipedia.stopme()
