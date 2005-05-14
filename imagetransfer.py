"""
Script to find images on a subject on another wikipedia and copy them
to WikiCommons.

Arguments:

  -lang:xx Log in to the given wikipedia language
  
  -from:xx Only follow interwiki links to language xx. Argument can be used
           multiple times to indicate that only some specific languages should
           be followed. If this argument isn't used, all interwiki links will
           be followed.
  
The script will ask for a page title and eventually copy images from the
equivalent pages on other wikipedias.
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

def main(args):
    # if the -file argument is used, page titles are dumped in this array.
    # otherwise it will only contain one page.
    page_list = []
    # if -file is not used, this temporary array is used to read the page title.
    page_title = []
    imagelist = []
    source_wikis = []

    for arg in args:
    #for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg.startswith('-from:'):
                source_wikis.append(arg[6:])
            elif arg.startswith('-file'):
                if len(arg) == 5:
                    # todo: check for console encoding to allow special characters
                    # in filenames, as done below with pagename
                    file = wikipedia.input(u'Please enter the list\'s filename: ')
                else:
                    file = arg[6:]
                # open file and read page titles out of it
                f=open(file)
                for line in f.readlines():
                    if line != '\n':           
                        page_list.append(line)
                f.close()
            else:
                page_title.append(arg)

    # if the page title is given as a command line argument,
    # connect the title's parts with spaces
    if page_title != []:
        page_title = ' '.join(page_title)
        page_list.append(page_title)

    # Use mysite when getting pages, but commons when uploading pages.
    mysite = wikipedia.getSite()
    wikipedia.argHandler('-lang:commons')

    # if no page title was given as an argument, and none was
    # read from a file, query the user
    if page_list == []:
        pagename = wikipedia.input(u'Which page to check: ')
        pagename = wikipedia.url2unicode(pagename, mysite)
        pagename = pagename.encode(wikipedia.myencoding())
        page_list.append(pagename)

    if not wikipedia.getSite().loggedin():
        print "You must be logged in on WikiCommons."
        import sys
        sys.exit(1)
    
    for page_list_item in page_list:
        inpl = wikipedia.Page(mysite, page_list_item)
        ilinks = inpl.interwiki()
    
        for page in ilinks:
            if page.site() in source_wikis or source_wikis==[]:
                site=page.site()
                try:
                    for i in page.imagelinks():
                        imagelist.append(i)
                except wikipedia.NoPage:
                    pass
                except wikipedia.IsRedirectPage,arg:
                    page2=wikipedia.Page(page.site(),arg.args[0])
                    try:
                        for i in page2.imagelinks():
                            imagelist.append(i)
                    except wikipedia.NoPage:
                        pass
                    except wikipedia.IsRedirectPage:
                        pass
    
        for i in range(len(imagelist)):
            imagelink = imagelist[i]
            print "-"*60
            wikipedia.output(u"%s. Found image: %s"% (i,imagelink.aslink()))
            try:
                # show the image description page's contents
                wikipedia.output(imagelink.get(throttle=False))
            except wikipedia.NoPage:
                try:
                    # Maybe the image is on WikiCommons?
                    commonslink = imagelink.linkname()
                    commonslink = [wikipedia.getSite().image_namespace()] + commonslink.split(':')[1:]
                    commonslink = ':'.join(commonslink)
                    commonslink = wikipedia.Page(wikipedia.getSite(),commonslink)
                    if commonslink.get(throttle=False):
                        print "Image is already on WikiCommons."
                        wikipedia.output(commonslink.get(throttle=False))
                    else:
                        print "Description empty."
                except wikipedia.NoPage:
                    print "Description empty."
                except wikipedia.IsRedirectPage:
                    print "Description page on WikiCommons is redirect?!"
            except wikipedia.IsRedirectPage:
                print "Description page is redirect?!"
    
        print "="*60
    
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

try:
    main(sys.argv[1:])
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()
