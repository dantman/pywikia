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

import re,sys
import httplib,md5
import wikipedia

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

# gets a wikilink to an image, downloads it and its description,
# and uploads it to another wikipedia
def treat(imagelink, target):
    print "--------------------------------------------------"
    print "Found image: %s"% (imagelink.aslink())
    # todo: need to strip of "Afbeelding:"
    filename = imagelink.linkname()
    print "Image filename is: %s " % filename
    md5sum = md5.new(filename).hexdigest()
    print "MD5 hash is: %s" % md5sum
    url = "http://" + imagelink.code() + ".wikipedia.org/upload/" + md5sum[0] + "/" + md5sum[:2] + "/" + filename
    print "URL should be: %s" % url
    
    print
    try:
        print imagelink.get()
    except wikipedia.NoPage:
        print "Page not found"


for i in range(len(imagelist)):
    treat (imagelist[i], wikipedia.mylang)

print "=================================================="

print "Bot still in development; use upload.py for uploading."
