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
import httplib
import wikipedia

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


for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    else:
        print "Unknown argument: ",arg
        sys.exit(1)
        
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

print "Uploading image to ",wikipedia.langs[wikipedia.mylang]

def main():
    fn = raw_input('File or URL where image is now : ')
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
    newfn = newfn.replace(' ', '_')
    
    # A proper description for the submission
    description = raw_input('Description : ')

    data = post_multipart(wikipedia.langs[wikipedia.mylang],
                          uploadaddr,
                          (('wpUploadDescription', description),
                           ('wpUploadAffirm', '1'),
                           ('wpUpload','upload bestand')),
                          (('wpUploadFile',fn,contents),)
                          )

    return fn

if __name__=="__main__":
    main()
    
