# -*- coding: utf-8 -*-
"""
Script to upload images to wikipedia.

Arguments:

  -keep    Keep the filename as is

If any other arguments are given, the first is the URL or filename
to upload, and the rest is a proposed description to go with the
upload. If none of these are given, the user is asked for the
file or URL to upload. The bot will then upload the image to the wiki.

The script will ask for the location of an image, if not given as a parameter,
and for a description.
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
    def __init__(self, filename, description, keep):
        self.filename = filename
        self.description = description
        self.keep = keep
        
        mysite = wikipedia.getSite()
        mysite.forceLogin()

    def filenameOK(self):
        '''
        Returns true iff the filename references an online site or to an
        existing local file.
        '''
        return self.filename != '' and ('://' in self.filename or os.path.exists(self.filename))

    def run(self):
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

    for arg in args:
        if wikipedia.argHandler(arg, 'upload'):
            if arg.startswith('-keep'):
                keep = True
            elif filename == '':
                filename = arg
            else:
                description.append(arg)
    description = ' '.join(description)
    bot = UploadRobot(filename, description, keep)
    bot.run()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
