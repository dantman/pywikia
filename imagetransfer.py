"""
Script to find images on a subject on another wikipedia and copy them
to one's own Wikipedia. Script is still in development; the image
searching part has been finished, but the uploading has not. Look for
the image through its description page and upload with upload.py.

Arguments:

  -lang:xx Log in to the given wikipedia language
  
The script will ask for the location of an image, and for a description.
It will then send the image to wikipedia.
"""
#
# (C) Andre Engels, 2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'

import re,sys,string
import httplib
import wikipedia, lib_images

inname = []
imagelist = []

for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        inname.append(arg)

inname = '_'.join(inname)

if not wikipedia.special.has_key(wikipedia.mylang):
    print "Please add the translation for the Special: namespace in"
    print "Your home wikipedia to the wikipedia.py module"
    import sys
    sys.exit(1)

if not wikipedia.cookies:
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)
    
uploadaddr='/wiki/%s:Upload'%wikipedia.special[wikipedia.mylang]

inpl = wikipedia.PageLink(wikipedia.mylang, inname)
ilinks = inpl.interwiki()

for page in ilinks:
    lang=page.code()
    for i in page.imagelinks():
        imagelist.append(i)

for i in range(len(imagelist)):
    imagelink = imagelist[i]
    print "--------------------------------------------------"
    print "%s. Found image: %s"% (i,imagelink.aslink())
    try:
        print imagelink.get()
    except wikipedia.NoPage:
        print "Description empty."        

print "=================================================="

while 1:
    print("Give the number of the image to download.")
    todo=raw_input("To end uploading, press enter: ")
    if not todo:
        break
    todo=int(todo)
    if todo in range(len(imagelist)):
        lib_images.transfer_image(imagelist[todo], wikipedia.mylang)
    else:
        print("No such image number.")
