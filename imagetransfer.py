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

if not wikipedia.cookies:
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)
    
if inname=='':
    inname=raw_input("For which page are images to be found: ")

inpl = wikipedia.PageLink(wikipedia.mylang, inname)
ilinks = inpl.interwiki()

for page in ilinks:
    lang=page.code()
    try:
        for i in page.imagelinks():
            imagelist.append(i)
    except wikipedia.NoPage:
        pass
    except wikipedia.IsRedirectPage,arg:
        page2=wikipedia.PageLink(page.code(),arg.args[0])
        try:
            for i in page2.imagelinks():
                imagelist.append(i)
        except wikipedia.NoPage:
            pass
        except wikipedia.IsRedirectPage:
            pass

for i in range(len(imagelist)):
    imagelink = imagelist[i]
    print "--------------------------------------------------"
    print "%s. Found image: %s"% (i,imagelink.aslink())
    try:
        print wikipedia.UnicodeToAsciiHtml(imagelink.get())
    except wikipedia.NoPage:
        print "Description empty."
    except wikipedia.IsRedirectPage:
        print "Description page is redirect?!"

print "=================================================="

while len(imagelist)>0:
    print("Give the number of the image to upload.")
    todo=raw_input("To end uploading, press enter: ")
    if not todo:
        break
    todo=int(todo)
    if todo in range(len(imagelist)):
        lib_images.transfer_image(imagelist[todo])
    else:
        print("No such image number.")
