# -*- coding: iso8859-1 -*-
"""
Bot for getting multiple images from an external site. It takes a URL as an
argument and finds all images (and other files specified by the extensions
in 'fileformats') that URL is referring to, asking whether to upload them.
If further arguments are given, they are considered to be the text that is
common to the descriptions.
"""

import re, sys, os
import wikipedia, lib_images

def get_imagelinks(url):
    # Given a URL, get all images linked to by the page at that URL.
    # First, we get the location for relative links from the URL.
    relativepath = url.split("/")
    if len(relativepath) == 1:
        relativepath=relativepath[0]
    else:
        relativepath=relativepath[:len(relativepath)-1]
        relativepath="/".join(relativepath)
    links = []
    uo = wikipedia.MyURLopener()
    file = uo.open(url)
    text = file.read()
    file.close()
    text = text.lower()
    R=re.compile("[(HREF)(href)]=[\"'](.*?)[\"']")
    for link in R.findall(text):
        ext = os.path.splitext(link)[1].lower().strip('.')
        if ext in fileformats:
            if re.compile("://").match(text):
                links += [link]
            else:
                links += [relativepath+"/"+link]
    return links

url = ''
fileformats = ('jpg', 'jpeg', 'png', 'gif', 'svg', 'ogg')
basicdesc = []
  
for arg in sys.argv[1:]:
    arg = wikipedia.argHandler(arg)
    if arg:
        if url == '':
            url = arg
        else:
            desc += [arg]

mysite = wikipedia.getSite()

if not mysite.loggedin():
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)

if url == '':
    url = wikipedia.input(u"From what URL should I get the images?")

if basicdesc == []:
    basicdesc = wikipedia.input(
        u"What text should be added at the end of the description of each image from this url?")
else:
    basicdesc = ' '.join(desc)

ilinks = get_imagelinks(url)

for image in ilinks:
    if wikipedia.input(u"Include image %s (y/N)?"%image) in ["y","Y"]:
        desc = wikipedia.input(u"Give the description of this image:")
        desc = desc + "\r\n\n\r" + basicdesc
        lib_images.get_image(image, None, desc)

