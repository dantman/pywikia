"""
Script to upload images to wikipedia.

Arguments:

  -lang:xx Log in to the given wikipedia language
  
The script will ask for the location of an image, and for a description.
It will then send the image to wikipedia.
"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'

import re,sys
import wikipedia, lib_images


for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        print "Unknown argument: ",arg
        sys.exit(1)
        
if not wikipedia.cookies:
    print "You must be logged in to upload images"
    import sys
    sys.exit(1)
    
uploadaddr='/wiki/%s:Upload'%wikipedia.special[wikipedia.mylang]

print "Uploading image to ",wikipedia.langs[wikipedia.mylang]

def main():
    fn = raw_input('File or URL where image is now : ')
    lib_images.get_image(fn, wikipedia.mylang,"")

if __name__=="__main__":
    main()
    
