"""
Script to upload images to wikipedia.

Arguments:

  -lang:xx Log in to the given wikipedia language

Any other arguments given are filenames or URLs to get the pictures
from.
  
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
import wikipedia, lib_images

flist = []

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        flist.append(arg)

if not wikipedia.cookies:
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)

if flist==[]:
    fn = raw_input('File or URL where image is now : ')
    lib_images.get_image(fn, wikipedia.mylang,"")
else:
    for fn in flist:
        print('')
        print('Uploading: %s')%fn
        lib_images.get_image(fn, wikipedia.mylang,"")
