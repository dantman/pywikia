"""
Script to transfer many images from one wiki to another. Your
language (which can be changed with the -lang: argument) is the
language to upload to. The images should be in a file as interwiki
links (that is in the form [[en:Image:myimage.png]]); they do not
need to be all from the same Wiki. This file can be created with
extract_wikilinks.py.

Arguments:

  -lang:xx Log in to the given wikipedia language to upload to

The first other argument is taken to be the name of the file you get
the links from; other arguments are ignored.
"""
#
# (C) Andre Engels 2004
#
# Distribute under the terms of the PSF license.
#

import sys
import wikipedia, lib_images

filename = None
list = []

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if filename:
            print "Ignoring argument %s"%arg
        else:
            filename = arg

if not filename:
    print "No file specified to get the image links from"
    sys.exit(1)

# We want to be able to get our pictures from WikiCommons, so we
# add it to the list of languages.
wikipedia.family._addlang('commons','commons.wikimedia.org')

for image in wikipedia.PageLinksFromFile(filename):
    if image.isImage():
        image.get()
        print "--------------------------------------------------"
        print "Image: %s"% (image.linkname())
        try:
            # show the image description page's contents
            print image.get()
        except wikipedia.NoPage:
            print "Description empty."
        except wikipedia.IsRedirectPage:
            print "Description page is redirect?!"
        answer=wikipedia.input(u"Copy this image (y/N)?")
        if answer[0] in ["y","Y"]:
            lib_images.transfer_image(image)
