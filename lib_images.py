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
    "af":"Laai suksesvol",
    "als":"Successful upload",
    "ar":"%D8%AA%D8%AD%D9%85%D9%8A%D9%84 %D8%A7%D9%84%D9%85%D9%84%D9%81 %D8%A8%D9%86%D8%AC%D8%A7%D8%AD",
    "ca":"L'arxiu s'ha carregat amb %C3%A8xit",
    "co":"Successful upload",
    "cs":"Nacten%C3%AD_%C3%BAspe%C5%A1ne_provedeno%21",
    "cy":"Uwchlwyth llwyddiannus",
    "da":"Opl%E6gning er gennemf%F8rt med success",
    "de":"Erfolgreich hochgeladen",
    "en":"Succesful upload",
    "eo":"uto sukcesis!",
    "es":"Subida exitosa",
    "et":"%C3%9Cleslaadimine %C3%B5nnestus",
    "eu":"Succesful upload",
    "fi":"Tallennus onnistui",
    "fy":"Oanbieden slagge",
    "gl":"Successful upload",
    "he":"%D7%94%D7%A2%D7%9C%D7%90%D7%AA %D7%94%D7%A7%D7%95%D7%91%D7%A5 %D7%94%D7%A6%D7%9C%D7%99%D7%97%D7%94",
    "hr":"Successful upload",
    "hu":"Sikeresen felk",
    "ia":"Carga complete",
    "id":"Berjaya dimuaturun",
    "is":"Successful upload",
    "it":"Caricamento completato",
    "ja":"%E3%82%A2%E3%83%83%E3%83%97%E3%83%AD%E3%83%BC%E3%83%89%E6%88%90%E5%8A%9F",
    "ko":"%EC%98%AC%EB%A6%AC%EA%B8%B0 %EC%84%B1%EA%B3%B5",
    "ku":"Successful upload",
    "la":"Oneratum perfectum",
    "lt":"Successful upload",
    "lv":"Successful upload",
    "ms":"Berjaya dimuaturun",
    "nds":"Successful upload",
    "nl":"De upload was succesvol",
    "no":"Opplastingen er gjennomf%C3%B8rt",
    "oc":"Copie r%C3%A9ussie",
    "pl":"Przes%C5%82anie pliku powiod%C5%82o si%C4%99",
    "pt":"Carregamento efetuado com sucesso",
    "ro":"Fi%C5%9Fierul a fost trimis",
    "ru":"%D0%AF%D0%BF%D0%BE%D0%BD%D1%81%D0%BA%D0%BE%D0%B5_%D0%BC%D0%BE%D1%80%D0%B5",
    "simple":"Succesful upload",
    "sl":"Nalaganje uspe%C5%A1no",
    "sv":"Uppladdningen lyckades",
    "uk":"%D0%97%D0%B0%D0%B2%D0%B0%D0%BD%D1%82%D0%B0%D0%B6%D0%B5%D0%BD%D0%BD%D1%8F_%D1%83%D1%81%D0%BF%D1%96%D1%88%D0%BD%D0%BE_%D0%B7%D0%B0%D0%B2%D0%B5%D1%80%D1%88%D0%B5%D0%BD%D0%BE",
    "wa":"L%27_eberwetaedje_a_st%C3%AE_comif%C3%A5",
    "zh":"%E4%B8%8A%E8%BD%BD%E6%88%90%E5%8A%9F"
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
# source_wiki is the language code for the Wikipedia the image is loaded from.
# if source_wiki is None, it indicates that the image is uploaded directly
# from the user's harddisk (via upload.py).
# Returns the filename which was used to upload the image
# If the upload fails, the user is asked whether to try again or not.
# If the user chooses not to retry, returns null.
def get_image(original_url, source_wiki, original_description, keep=False, debug=False):
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
    if source_wiki != None:
        fn = unicode(fn, wikipedia.code2encoding(source_wiki))
    if not keep:
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
        description = wikipedia.input('Give a description for the image:')
    else:
        print ("The suggested description is:")
        print
        print wikipedia.output(description)
        print
        print ("Enter return to use this description, enter a text to add something")
        print ("at the end, or enter = followed by a text to replace the description.")
        newtext = wikipedia.input('Enter return, text or =text : ')
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
    description = wikipedia.unicode2html(description, wikipedia.code2encoding(wikipedia.mylang))
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
    msg_lang = wikipedia.chooselang(wikipedia.mylang,copy_message)
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

