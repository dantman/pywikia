#!/usr/bin/python
# -*- coding: utf-8  -*-
'''
Tool to copy a flickr stream to Commons

# Get a set to work on (start with just a username).
# * Make it possible to delimit the set (from/to)
#For each image
#*Check the license
#*Check if it isn't already on Commons
#*Build suggested filename
#**Check for name collision and maybe alter it
#*Pull description from Flinfo
#*Show image and description to user
#**Add a nice hotcat lookalike for the adding of categories
#**Filter the categories
#*Upload the image

Todo:
*Check if the image is already uploaded (SHA hash)
*Check and prevent filename collisions
**Initial suggestion
**User input
*Filter the categories

'''
#
# (C) Multichill, 2009
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: upload_to_commons.py 69 2009-08-23 11:44:26Z multichill $'

import sys, urllib, re,  StringIO
import wikipedia, config, query, imagerecat, upload

import flickrapi
import xml.etree.ElementTree
from Tkinter import *
from PIL import Image, ImageTk

def getPhoto(flickr = None, photo_id = ''):
    '''
    Get the photo info and the photo sizes so we can use these later on
    '''
    photoInfo = flickr.photos_getInfo(photo_id=photo_id)
    #xml.etree.ElementTree.dump(photoInfo)
    photoSizes = flickr.photos_getSizes(photo_id=photo_id)
    #xml.etree.ElementTree.dump(photoSizes)
    return (photoInfo, photoSizes)

def isAllowedLicense(photoInfo = None):
    '''
    Check if the image contains the right license
    '''
    license = photoInfo.find('photo').attrib['license']
    if license == '4' or license == '5':
        #Is cc-by or cc-by-sa
        return True
    else:
        #We don't accept other licenses
        return False

def getTags(photoInfo = None):
    '''
    Get all the tags on a photo
    '''
    result = []
    for tag in photoInfo.find('photo').find('tags').findall('tag'):
        result.append(tag.text.lower())

    return result

def getFlinfoDescription(photo_id = 0):
    '''
    Get the description from http://wikipedia.ramselehof.de/flinfo.php
    '''
    parameters = urllib.urlencode({'id' : photo_id, 'raw' : 'on'})
    
    #print 'Flinfo gaat nu aan de slag'
    rawDescription = urllib.urlopen("http://wikipedia.ramselehof.de/flinfo.php?%s" % parameters).read()
    #print rawDescription.decode('utf-8')
    return rawDescription.decode('utf-8')

def getFilename(photoInfo=None):
    '''
    Build a good filename for the upload based on the username and the title
    '''
    username = photoInfo.find('photo').find('owner').attrib['username']
    title = photoInfo.find('photo').find('title').text
    if title:
        title =  cleanUpTitle(title)
    else:
        title = u''

    return u'Flickr - %s - %s.jpg' % (username, title)

def cleanUpTitle(title):
    title = title.strip()   
        
    title = re.sub("[<{\\[]", "(", title)
    title = re.sub("[>}\\]]", ")", title)
    title = re.sub("[ _]?\\(!\\)", "", title)
    title = re.sub(",:[ _]", ", ", title)
    title = re.sub("[;:][ _]", ", ", title)
    title = re.sub("[\t\n ]+", " ", title)
    title = re.sub("[\r\n ]+", " ", title)
    title = re.sub("[\n]+", "", title)
    title = re.sub("[?!]([.\"]|$)", "\\1", title)
    title = re.sub("[&#%?!]", "^", title)
    title = re.sub("[;]", ",", title)
    title = re.sub("[/+\\\\:]", "-", title)
    title = re.sub("--+", "-", title)
    title = re.sub(",,+", ",", title)
    title = re.sub("[-,^]([.]|$)", "\\1", title)
    title = title.replace(" ", "_")   

    return title

def getPhotoUrl(photoSizes=None):
    '''
    Get the url of the jpg file with the highest resolution
    '''
    url = ''
    # The assumption is that the largest image is last
    for size in photoSizes.find('sizes').findall('size'):
        url = size.attrib['source']
    return url

def buildDescription(flinfoDescription=u'', flickrreview=False, reviewer=u'', override=u''):
    '''
    Build the final description for the image. The description is based on the info from flickrinfo and improved.
    '''
    description = flinfoDescription

    if(override):
        description = description.replace(u'{{cc-by-sa-2.0}}\n', u'')
        description = description.replace(u'{{cc-by-2.0}}\n', u'')
        description = description.replace(u'{{flickrreview}}\n', u'')
        description = description.replace(u'{{copyvio|Flickr, licensed as "All Rights Reserved" which is not a free license --~~~~}}\n', u'')       
        description = description.replace(u'=={{int:license}}==', u'=={{int:license}}==\n' + override)
    elif(flickrreview):
        if(reviewer):
            description = description.replace(u'{{flickrreview}}', u'{{flickrreview|' + reviewer + '|{{subst:CURRENTYEAR}}-{{subst:CURRENTMONTH}}-{{subst:CURRENTDAY2}}}}')
    description = description.replace(u'\r\n', u'\n')
    return description

def getPhotos(flickr=None, user_id=u'', group_id=u'', photoset_id=u'', tags=u''):
    result = []    
    # http://www.flickr.com/services/api/flickr.groups.pools.getPhotos.html
    if(group_id):
        #First get the total number of photo's in the group
        photos = flickr.groups_pools_getPhotos(group_id=group_id, user_id=user_id, tags=tags, per_page='100', page='1')
        pages = photos.find('photos').attrib['pages']

        for i in range(1, int(pages)):
            for photo in flickr.groups_pools_getPhotos(group_id=group_id, user_id=user_id, tags=tags, per_page='100', page=i).find('photos').getchildren():
                yield photo.attrib['id']
            
    # http://www.flickr.com/services/api/flickr.photosets.getPhotos.html
    elif(photoset_id):
        photos = flickr.photosets_getPhotos(photoset_id=photoset_id, per_page='100', page='1')
        pages = photos.find('photos').attrib['pages']

        for i in range(1, int(pages)):
            for photo in flickr.photosets_getPhotos(photoset_id=photoset_id, per_page='100', page=i).find('photos').getchildren():
                yield photo.attrib['id']
    
    # http://www.flickr.com/services/api/flickr.people.getPublicPhotos.html
    elif(user_id):
        photos = flickr.people_getPublicPhotos(user_id=user_id, per_page='100', page='1')
        pages = photos.find('photos').attrib['pages']

        for i in range(1, int(pages)):
            for photo in flickr.people_getPublicPhotos(user_id=user_id, per_page='100', page=i).find('photos').getchildren():
                yield photo.attrib['id']
    return
    

def processPhoto(flickr=None, photo_id=u'', flickrreview=False, reviewer=u'', override=u''):
    if(photo_id):
        print photo_id
        (photoInfo, photoSizes) = getPhoto(flickr=flickr, photo_id=photo_id)
    if (isAllowedLicense(photoInfo=photoInfo) or override):
        # Tags not needed atm
        #tags=getTags(photoInfo=photoInfo)

        flinfoDescription = getFlinfoDescription(photo_id=photo_id)

        filename = getFilename(photoInfo=photoInfo)
        #print filename
        photoUrl = getPhotoUrl(photoSizes=photoSizes)
        #print photoUrl
        photoDescription = buildDescription(flinfoDescription=flinfoDescription, flickrreview=flickrreview, reviewer=reviewer, override=override)
        #wikipedia.output(photoDescription)
        (newPhotoDescription, newFilename, skip)=Tkdialog(photoDescription, photoUrl, filename).run()
        #wikipedia.output(newPhotoDescription)
        #if (wikipedia.Page(title=u'File:'+ filename, site=wikipedia.getSite()).exists()):
        # I should probably check if the hash is the same and if not upload it under a different name
        #wikipedia.output(u'File:' + filename + u' already exists!')
        #else:
            #Do the actual upload
            #Would be nice to check before I upload if the file is already at Commons
            #Not that important for this program, but maybe for derived programs
        if not skip:
            bot = upload.UploadRobot(url=photoUrl, description=newPhotoDescription, useFilename=newFilename, keepFilename=True, verifyDescription=False)
            bot.upload_image(debug=False)
    return 0

class Tkdialog:
    def __init__(self, photoDescription, photoUrl, filename):
        self.root=Tk()
        #"%dx%d%+d%+d" % (width, height, xoffset, yoffset)
        self.root.geometry("1600x1000+10-10")

        self.root.title(filename)
        self.photoDescription = photoDescription
        self.filename = filename 
        self.photoUrl = photoUrl
        self.skip=False
        self.exit=False

        ## Init of the widgets
        # The image
        self.image=self.getImage(self.photoUrl, 800, 600)
        self.imagePanel=Label(self.root, image=self.image)
        
        self.imagePanel.image = self.image
        
        # The filename
        self.filenameLabel=Label(self.root,text=u"Suggested filename")
        self.filenameField=Entry(self.root, width=100)
        self.filenameField.insert(END, filename)
        
        # The description
        self.descriptionLabel=Label(self.root,text=u"Suggested description")
        self.descriptionScrollbar=Scrollbar(self.root, orient=VERTICAL)
        self.descriptionField=Text(self.root)
        self.descriptionField.insert(END, photoDescription)
        self.descriptionField.config(state=NORMAL, height=12, width=100, padx=0, pady=0, wrap=WORD, yscrollcommand=self.descriptionScrollbar.set)
        self.descriptionScrollbar.config(command=self.descriptionField.yview)
        
        # The buttons
        self.okButton=Button(self.root, text="OK", command=self.okFile)
        self.skipButton=Button(self.root, text="Skip", command=self.skipFile)
        
        ## Start grid
        # The image
        self.imagePanel.grid(row=0, column=0, rowspan=11, columnspan=4)
        
        # The filename
        self.filenameLabel.grid(row=11, column=0)
        self.filenameField.grid(row=11, column=1, columnspan=3)

        # The description
        self.descriptionLabel.grid(row=12, column=0)
        self.descriptionField.grid(row=12, column=1, columnspan=3)
        self.descriptionScrollbar.grid(row=12, column=5)

        # The buttons
        self.okButton.grid(row=13, column=1, rowspan=2)
        self.skipButton.grid(row=13, column=2, rowspan=2)
        
    def getImage(self, url, width, height):
        image=urllib.urlopen(url).read()
        output = StringIO.StringIO(image)
        image2 = Image.open(output)
        image2.thumbnail((width, height))
        imageTk = ImageTk.PhotoImage(image2)
        return imageTk
    
    def okFile(self):
        '''
        The user pressed the OK button.
        '''
        self.filename=self.filenameField.get()
        self.photoDescription=self.descriptionField.get(0.0, END)
        self.root.destroy()

    def skipFile(self):
        '''
        The user pressed the Skip button.
        '''
        self.skip=True
        self.root.destroy()

    def run(self):
        '''
        Activate the dialog and return the new name and if the image is skipped.
        '''
        self.root.mainloop()
        return (self.photoDescription, self.filename, self.skip)


def usage():
    wikipedia.output(u"Flickrripper is a tool to transfer flickr photos to Wikimedia Commons")
    wikipedia.output(u"-group_id:<group_id>\n")
    wikipedia.output(u"-photoset_id:<photoset_id>\n")
    wikipedia.output(u"-user_id:<user_id>\n")
    wikipedia.output(u"-tags:<tag>\n")
    return

def main():
    site = wikipedia.getSite(u'commons', u'commons')
    wikipedia.setSite(site)
    #imagerecat.initLists()

    #Get the api key
    if(config.flickr['api_key']):
        flickr = flickrapi.FlickrAPI(config.flickr['api_key'])
    else:
        wikipedia.output('Flickr api key not found! Get yourself an api key')
        wikipedia.output('Any flickr user can get a key at http://www.flickr.com/services/api/keys/apply/')
        return

    group_id = u''
    photoset_id = u''
    user_id = u''
    tags = u''
    totalPhotos = 0
    uploadedPhotos = 0

    # Do we mark the images as reviewed right away?
    if config.flickr['review']:
        flickrreview = config.flickr['review']
    else:    
        flickrreview = False       

    # Set the Flickr reviewer
    if config.flickr['reviewer']:
        reviewer = config.flickr['reviewer']
    elif config.sysopnames['commons']['commons']:
        reviewer = config.sysopnames['commons']['commons']
    elif config.usernames['commons']['commons']:
        reviewer = config.usernames['commons']['commons']
    else:
        reviewer = u''

    override = u''
    
    for arg in wikipedia.handleArgs():
        if arg.startswith('-group_id'):
            if len(arg) == 9:
                group_id = wikipedia.input(u'What is the group_id of the pool?')
            else:
                group_id = arg[10:]
        elif arg.startswith('-photoset_id'):
            if len(arg) == 12:
                photoset_id = wikipedia.input(u'What is the photoset_id)?')
            else:
                photoset_id = arg[13:]
        elif arg.startswith('-user_id'):
            if len(arg) == 8:
                user_id = wikipedia.input(u'What is the user_id of the flickr user?')
            else:
                user_id = arg[9:]
        elif arg.startswith('-tags'):
            if len(arg) == 5:
                tags = wikipedia.input(u'What is the tag you want to filter out (currently only one supported)?')
            else:
                tags = arg[6:]
        elif arg == '-flickrreview':
            flickrreview = True
        elif arg.startswith('-reviewer'):
            if len(arg) == 9:
                reviewer = wikipedia.input(u'Who is the reviewer?')
            else:
                reviewer = arg[10:]      
        elif arg.startswith('-override'):
            if len(arg) == 9:
                override = wikipedia.input(u'What is the override text?')
            else:
                override = arg[10:]

    if user_id or group_id or photoset_id:
        for photo_id in getPhotos(flickr=flickr, user_id=user_id, group_id=group_id, photoset_id=photoset_id, tags=tags):
            uploadedPhotos = uploadedPhotos + processPhoto(flickr=flickr, photo_id=photo_id, flickrreview=flickrreview, reviewer=reviewer, override=override)
            totalPhotos = totalPhotos + 1
    else:
        usage()

    wikipedia.output(u'Finished running')
    wikipedia.output(u'Total photos: ' + str(totalPhotos))
    wikipedia.output(u'Uploaded photos: ' + str(uploadedPhotos))
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
