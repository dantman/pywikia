# -*- coding: iso8859-1 -*-
"""
Library with functions needed for image treatment
"""

import wikipedia, string, md5

# Gets a wikilink to an image, downloads it and its description,
# and uploads it to another wikipedia
# This function is used by imagetransfer.py and by copy_table.py
def transfer_image(imagelink, target, debug=False):
    if debug: print "--------------------------------------------------"
    if debug: print "Found image: %s"% (imagelink.aslink())
    # need to strip off "Afbeelding:", "Image:" etc.
    # we only need the substring following the first colon
    filename = string.split(imagelink.linkname(), ":", 1)[1]
    if debug: print "Image filename is: %s " % filename
    md5sum = md5.new(filename).hexdigest()
    if debug: print "MD5 hash is: %s" % md5sum
    url = "http://" + imagelink.code() + ".wikipedia.org/upload/" + md5sum[0] + "/" + md5sum[:2] + "/" + filename
    if debug: print "URL should be: %s" % url
    
    print
    try:
        if debug: print imagelink.get()
    except wikipedia.NoPage:
        print "Page not found"