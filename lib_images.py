# -*- coding: iso8859-1 -*-
"""
Library with functions needed for image treatment
"""

import re, sys, string, md5
import httplib
import wikipedia, config

copy_message = {
    "en":"This image was copied from the %s Wikipedia. The original description was:\r\n\r\n%s",
    "de":"Dieses Bild wurde von der %s-Wikipedia kopiert. Die dortige Beschreibung lautete:\r\n\r\n%s",
    "nl":"Afbeelding gekopieerd vanaf Wikipedia-%s. De beschrijving daar was:\r\n\r\n%s",
}


# a string which appears on the HTML page which says that the upload was successful,
# and which doesn't appear on a page which says that the upload failed.
success_message = {
    "de":"Erfolgreich hochgeladen",
}

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.putheader("User-agent", "RobHooftWikiRobot/1.0")
    h.putheader('Host', host)
    h.putheader('Cookie',wikipedia.cookies)
    h.endheaders()
    print "Uploading file..."
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    import mimetypes
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

# Gets the image at URL original_url, and uploads it to the home Wikipedia.
# original_description is the proposed description; if description is
# empty (''), asks for a description.
# Returns the filename which was used to upload the image
# If the upload fails, the user is asked whether to try again or not.
# If the user chooses not to retry, returns null.
def get_image(original_url, source_wiki, original_description, debug=False):
    # work with a copy of argument variables so we can reuse the
    # original ones if the upload fails
    fn = original_url
    description = original_description
    # Get file contents
    uo = wikipedia.MyURLopener()
    file = uo.open(fn)
    contents = file.read()
    if contents.find("The requested URL was not found on this server.") != -1:
        print "Couldn't download the image."
        return
    file.close()
    # Isolate the pure name
    if '/' in fn:
        fn = fn.split('/')[-1]
    if '\\' in fn:
        fn = fn.split('\\')[-1]
    # convert ISO 8859-1 to Unicode, or parse UTF-8 
    # fn = unicode(fn, wikipedia.code2encoding(source_wiki))
    print "The filename on wikipedia will default to:",fn
    newfn = raw_input("Better name : ")
    if newfn:
        fn = unicode(newfn, config.console_encoding)
    try:
        fn = fn.encode(wikipedia.code2encoding(wikipedia.mylang))
    except UnicodeDecodeError:
        print "This filename can't be displayed in " + wikipedia.code2encoding(wikipedia.mylang)
        sys.exit(1)
    # Wikipedia doesn't allow spaces in the file name.
    # Replace them here to avoid an extra confirmation form
    fn = fn.replace(' ', '_')
    
    # A proper description for the submission.
    if description=='':
        print ('Give a description for the image:')
        description = raw_input('')
        description = unicode(description, config.console_encoding)
    else:
        print ("The suggested description is:")
        print
        print wikipedia.UnicodeToAsciiHtml(description)
        print
        print ("Enter return to use this description, enter a text to add something")
        print ("at the end, or enter = followed by a text to replace the description.")
        newtext = raw_input('Enter return, text or =text : ')
        newtext = unicode(newtext, config.console_encoding)
        if newtext=='':
            pass
        elif newtext[0]=='=':
            description=newtext[1:]
        else:
            description=description+' '+newtext

    # try to encode the description to the encoding used by the home Wikipedia.
    # if that's not possible (e.g. because there are non-Latin-1 characters and
    # the home Wikipedia uses Latin-1), convert all non-ASCII characters to
    # HTML entities.
    try:
        description = description.encode(wikipedia.code2encoding(wikipedia.mylang))
    except UnicodeEncodeError:
        description = wikipedia.UnicodeToAsciiHtml(description).encode(wikipedia.code2encoding(wikipedia.mylang))
    # don't upload if we're in debug mode
    if not debug:
        returned_html = post_multipart(wikipedia.family.hostname(wikipedia.mylang),
                              wikipedia.family.upload_address(wikipedia.mylang),
                              (('wpUploadDescription', description),
                               ('wpUploadAffirm', '1'),
                               ('wpIgnoreWarning', '1'),
                               ('wpUpload','upload bestand')),
                              (('wpUploadFile',fn,contents),)
                              )
        # do we know how the "success!" HTML page should look like?
        if not success_message.has_key(wikipedia.mylang):
            print "Please edit lib_images.py and add a string to success_message for your language."
            print "Otherwise it will be impossible to find out if the upload was successful."
        else:
            # did the upload succeed?
            if returned_html.find(success_message[wikipedia.mylang]) != -1:
                 print "Upload successful."
            else:
                 # dump the HTML page
                 print returned_html + "\n\n"
                 answer = raw_input("Upload of " + fn + " failed. Above you see the HTML page which was returned by MediaWiki. Try again? [y|N]")
                 if answer in ["y", "Y"]:
                     return get_image(original_url, source_wiki, original_description, debug)
                 else:
                     return
    return fn


# Gets a wikilink to an image, downloads it and its description,
# and uploads it to another wikipedia
# Returns the filename which was used to upload the image
# This function is used by imagetransfer.py and by copy_table.py
def transfer_image(imagelink, debug=False):
    # convert HTML entities to encoding of the source wiki
    image_linkname = wikipedia.html2unicode(imagelink.linkname(), imagelink.code())
    image_linkname = image_linkname.encode('utf-8')
    if debug: print "--------------------------------------------------"
    if debug: print "Found image: %s"% image_linkname
    # need to strip off "Afbeelding:", "Image:" etc.
    # we only need the substring following the first colon
    filename = string.split(image_linkname, ":", 1)[1]
    if debug: print "Image filename is: %s " % filename
    # Spaces might occur, but internally they are represented by underscores.
    # Change the name now, because otherwise we get the wrong MD5 hash.
    # Also, the first letter should be capitalized
    filename = filename.replace(' ', '_')
    filename = filename[0].upper()+filename[1:]
    md5sum = md5.new(filename).hexdigest()
    if debug: print "MD5 hash is: %s" % md5sum
    url = "http://" + imagelink.code() + ".wikipedia.org/upload/" + md5sum[0] + "/" + md5sum[:2] + "/" + filename
    if debug: print "URL should be: %s" % url
    # localize the text that should be printed on the image description page
    if copy_message.has_key(wikipedia.mylang):
        msg_lang = wikipedia.mylang
    elif wikipedia.mylang == "fy":
        msg_lang = "nl"
    else:
        msg_lang = "en"
    try:
        description = copy_message[msg_lang] % (imagelink.code(), imagelink.get())
        # add interwiki link
        description += "\r\n\r\n" + imagelink.aslink()
    except wikipedia.NoPage:
        description=''
        print "Image does not exist or description page is empty."
    except wikipedia.IsRedirectPage:
        description=''
        print "Image description page is redirect."
    try:
        return get_image(url, imagelink.code(), description, debug)    
    except wikipedia.NoPage:
        print "Page not found"
        return filename

