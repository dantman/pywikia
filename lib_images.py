# -*- coding: iso8859-1 -*-
"""
Library with functions needed for image treatment
"""

import re,sys
import httplib
import wikipedia, string, md5

uploadaddr='/wiki/%s:Upload'%wikipedia.special[wikipedia.mylang]

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

# Gets the image at URL fn, and uploads it to Wikipedia 'target'.
# Description is the proposed description; if description is empty (''),
# a description is asked.
# Returns the filename which was used to upload the image
def get_image(fn,target,description):
    # Get file contents
    uo = wikipedia.MyURLopener()
    file = uo.open(fn)
    contents = file.read()
    file.close()
    # Isolate the pure name
    if '/' in fn:
        fn = fn.split('/')[-1]
    if '\\' in fn:
        fn = fn.split('\\')[-1]
    print "The filename on wikipedia will default to:",fn
    newfn = raw_input("Better name : ")
    if newfn:
        fn = newfn
    # Wikipedia doesn't allow spaces in the file name.
    # Replace them here to avoid an extra confirmation form
    fn = fn.replace(' ', '_')
    
    # A proper description for the submission

    # What I would have _liked_ to put here:
    # if description=='':
    #     description = raw_input('Description : ')
    # Unfortunately, the result is not ASCII then. I assume
    # but am not sure that the problem is newlines.

    description = raw_input('Description : ')

    data = post_multipart(wikipedia.langs[wikipedia.mylang],
                          uploadaddr,
                          (('wpUploadDescription', description),
                           ('wpUploadAffirm', '1'),
                           ('wpUpload','upload bestand')),
                          (('wpUploadFile',fn,contents),)
                          )

    return fn


# Gets a wikilink to an image, downloads it and its description,
# and uploads it to another wikipedia
# Returns the filename which was used to upload the image
# This function is used by imagetransfer.py and by copy_table.py
def transfer_image(imagelink, target, debug=False):
    if debug: print "--------------------------------------------------"
    if debug: print "Found image: %s"% (imagelink.aslink())
    # need to strip off "Afbeelding:", "Image:" etc.
    # we only need the substring following the first colon
    filename = string.split(imagelink.linkname(), ":", 1)[1]
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
    try:
        description="This image was copied from the " + imagelink.code() + " Wikipedia. The original description was:<br>" + imagelink.get()
    except wikipedia.NoPage:
        description=''
        print "Image does not exist or description page is empty."
    try:
        if debug:
            print imagelink.get()
            return filename
        else:
            return get_image(url,target,description)
    except wikipedia.NoPage:
        print "Page not found"

