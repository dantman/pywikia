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

fn = ''
desc = []
keep = False
wiki = ''

for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if arg.startswith('-keep'):
            keep = True
        elif arg.startswith('-wiki:'):
            wiki=arg[6:]
        elif fn=='':
            fn = arg
        else:
            desc.append(arg)

if not wikipedia.cookies:
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)

desc=' '.join(desc)

if wiki:
    while not fn:
        wikipedia.output(u'No input filename given')
        fn = wikipedia.input(u'Give filename:')
    full_image_name = "%s:%s"%(wikipedia.family.image_namespace(wiki),fn)
    pl = wikipedia.PageLink(wiki,full_image_name)
    lib_images.transfer_image(pl)
else:
    ok = (fn!='') and ( ('://') in fn or os.path.exists(fn))
    while not ok:
        if not fn:
            wikipedia.output(u'No input filename given')
        else:
            wikipedia.output(u'Invalid input filename given. Try again.')
        fn = wikipedia.input(u'File or URL where image is now:')
        ok = (fn!='') and ( ('://') in fn or os.path.exists(fn))
     
    lib_images.get_image(fn, None, desc, keep)

