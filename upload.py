"""
Script to upload images to wikipedia.

Arguments:

  -lang:xx Log in to the given wikipedia language to upload to

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

import re,sys
import wikipedia, lib_images, config

fn = ''
desc = []

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif fn=='':
        fn = arg
    else:
        desc.append(arg)

if not wikipedia.cookies:
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)

desc=' '.join(desc)

if fn=='':
    fn = raw_input('File or URL where image is now : ')

#convert arguments from encoding used by user's console
#to unicode
desc = unicode(desc, config.console_encoding)
fn = unicode(fn, config.console_encoding)

lib_images.get_image(fn, wikipedia.mylang, desc)
