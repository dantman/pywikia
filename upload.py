# -*- coding: utf-8 -*-
"""
Script to upload images to wikipedia.

Arguments:

  -keep         Keep the filename as is
  -noverify     Do not ask for verification of the upload description if one is given

If any other arguments are given, the first is the URL or filename
to upload, and the rest is a proposed description to go with the
upload. If none of these are given, the user is asked for the
file or URL to upload. The bot will then upload the image to the wiki.

The script will ask for the location of an image, if not given as a parameter,
and for a description.
"""
#
# (C) Rob W.W. Hooft, Andre Engels 2003-2004
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'

import os, sys, re
import urllib, httplib
import wikipedia, config

def post_multipart(site, address, fields, files, cookies):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    contentType, body = encode_multipart_formdata(fields, files)
    return site.postData(address, body, contentType = contentType)

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
    lines = []
    for (key, value) in fields:
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)
    for (key, filename, value) in files:
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        lines.append('Content-Type: %s' % get_content_type(filename))
        lines.append('')
        lines.append(value)
    lines.append('--' + boundary + '--')
    lines.append('')
    body = '\r\n'.join(lines)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body

def get_content_type(filename):
    import mimetypes
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


class UploadRobot:
    def __init__(self, url, description = u'', useFilename = None, keepFilename = False, verifyDescription = True, ignoreWarning = False, targetSite = None, urlEncoding = None):
        """
        ignoreWarning - Set this to True if you want to upload even if another
                        file would be overwritten or another mistake would be
                        risked.
                        Attention: This parameter doesn't work yet for unknown reason.
        """
        self.url = url
        self.urlEncoding = urlEncoding
        self.description = description
        self.useFilename = useFilename
        self.keepFilename = keepFilename
        self.verifyDescription = verifyDescription
        self.ignoreWarning = ignoreWarning
        if config.upload_to_commons:
            self.targetSite = targetSite or wikipedia.getSite('commons', 'commons')
        else:
            self.targetSite = targetSite or wikipedia.getSite()
        self.targetSite.forceLogin()

    def urlOK(self):
        '''
        Returns true iff the URL references an online site or an
        existing local file.
        '''
        return self.url != '' and ('://' in self.url or os.path.exists(self.url))

    def upload_image(self, debug=False):
        """Gets the image at URL self.url, and uploads it to the target wiki.
           Returns the filename which was used to upload the image.
           If the upload fails, the user is asked whether to try again or not.
           If the user chooses not to retry, returns null.
        """
        # Get file contents
        if '://' in self.url:
            uo = wikipedia.MyURLopener()
            file = uo.open(self.url,"rb")
        else:
            # Opening local files with MyURLopener would be possible, but we
            # don't do it because it only accepts ASCII characters in the
            # filename.
            file = open(self.url,"rb")
        wikipedia.output(u'Reading file %s' % self.url)
        contents = file.read()
        if contents.find("The requested URL was not found on this server.") != -1:
            print "Couldn't download the image."
            return
        file.close()
        # Isolate the pure name
        filename = self.url
        if '/' in filename:
            filename = filename.split('/')[-1]
        if '\\' in filename:
            filename = filename.split('\\')[-1]
        if self.urlEncoding:
            filename = urllib.unquote(filename)
            filename = filename.decode(self.urlEncoding)
        if self.useFilename:
            filename = self.useFilename
        if not self.keepFilename:
            wikipedia.output(u"The filename on the target wiki will default to: %s" % filename)
            # ask newfn until it's valid
            ok = False
            # FIXME: these 2 belong somewhere else, presumably in family
            forbidden = '/' # to be extended
            allowed_formats = (u'gif', u'jpg', u'jpeg', u'mid', u'midi', u'ogg', u'png', u'svg', u'xcf')
            while not ok:
                ok = True
                newfn = wikipedia.input(u'Enter a better name, or press enter to accept:')
                if newfn == "":
                    newfn = filename
                ext = os.path.splitext(newfn)[1].lower().strip('.')
                for c in forbidden:
                    if c in newfn:
                        print "Invalid character: %s. Please try again" % c
                        ok = False
                if ext not in allowed_formats and ok:
                    choice = wikipedia.inputChoice(u"File format is not one of [%s], but %s. Continue?" % (u' '.join(allowed_formats), ext), ['yes', 'no'], ['y', 'N'], 'N')
                    if choice == 'n':
                        ok = False
            if newfn != '':
                filename = newfn
        # MediaWiki doesn't allow spaces in the file name.
        # Replace them here to avoid an extra confirmation form
        filename = filename.replace(' ', '_')
        # Convert the filename (currently Unicode) to the encoding used on the
        # target wiki
        encodedFilename = filename.encode(self.targetSite.encoding())
        # A proper description for the submission.
        wikipedia.output(u"The suggested description is:")
        wikipedia.output(self.description)
        if self.verifyDescription:
                newDescription = u''
                choice = wikipedia.inputChoice(u'Do you want to change this description?', ['Yes', 'No'], ['y', 'N'], 'n')
                if choice == 'y':
                        import editarticle
                        editor = editarticle.TextEditor()
                        newDescription = editor.edit(self.description)
                # if user saved / didn't press Cancel
                if newDescription:
                        self.description = newDescription
    
        formdata = {}
        formdata["wpUploadDescription"] = self.description
    #     if self.targetSite.version() >= '1.5':
    #         formdata["wpUploadCopyStatus"] = wikipedia.input(u"Copyright status: ")
    #         formdata["wpUploadSource"] = wikipedia.input(u"Source of image: ")
        formdata["wpUploadAffirm"] = "1"
        formdata["wpUpload"] = "upload bestand"
        # This somehow doesn't work.
        if self.ignoreWarning:
            formdata["wpIgnoreWarning"] = "1"
        else:
            formdata["wpIgnoreWarning"] = "0"

        # try to encode the strings to the encoding used by the target site.
        # if that's not possible (e.g. because there are non-Latin-1 characters and
        # the home Wikipedia uses Latin-1), convert all non-ASCII characters to
        # HTML entities.
        for key in formdata:
            assert isinstance(key, basestring), "ERROR: %s is not a string but %s" % (key, type(key))
            try:
                formdata[key] = formdata[key].encode(self.targetSite.encoding())
            except (UnicodeEncodeError, UnicodeDecodeError):
                formdata[key] = wikipedia.UnicodeToAsciiHtml(formdata[key]).encode(self.targetSite.encoding())
    
        # don't upload if we're in debug mode
        if not debug:
            wikipedia.output(u'Uploading file to %s...' % self.targetSite)
            response, returned_html = post_multipart(self.targetSite,
                                  self.targetSite.upload_address(),
                                  formdata.items(),
                                  (('wpUploadFile', encodedFilename, contents),),
                                  cookies = self.targetSite.cookies()
                                  )
            # There are 2 ways MediaWiki can react on success: either it gives
            # a 200 with a success message, or it gives a 302 (redirection).
            # Do we know how the "success!" HTML page should look like?
            # ATTENTION: if you changed your Wikimedia Commons account not to show
            # an English interface, this detection will fail!
            success_msg = self.targetSite.mediawiki_message('successfulupload')
            if success_msg in returned_html or response.status == 302:
                 wikipedia.output(u"Upload successful.")
            # The following is not a good idea, because the server also gives a 200 when
            # something went wrong.
            #if response.status in [200, 302]:
            #    wikipedia.output(u"Upload successful.")
            
            else:
                try:
                    # Try to find the error message within the HTML page.
                    # If we can't find it, we just dump the entire HTML page.
                    returned_html = returned_html[returned_html.index('<!-- start content -->') + 22: returned_html.index('<!-- end content -->')]
                except:
                    pass
                wikipedia.output(u'%s\n\n' % returned_html)
                wikipedia.output(u'%i %s' % (response.status, response.reason))
                answer = wikipedia.inputChoice(u'Upload of %s probably failed. Above you see the HTML page which was returned by MediaWiki. Try again?' % filename, ['Yes', 'No'], ['y', 'N'], 'N')
                if answer in ["y", "Y"]:
                    return upload_image(debug)
                else:
                    return
        return filename

    def run(self):
        while not self.urlOK():
            if not self.url:
                wikipedia.output(u'No input filename given')
            else:
                wikipedia.output(u'Invalid input filename given. Try again.')
            self.url = wikipedia.input(u'File or URL where image is now:')
        return self.upload_image()

def main(args):
    url = u''
    description = []
    keepFilename = False
    verifyDescription = True

    # call wikipedia.py function to process all global wikipedia args
    # returns a list of non-global args, i.e. args for upload.py
    args = wikipedia.handleArgs()

    for arg in args:
        if arg:
            if arg.startswith('-keep'):
                keepFilename = True
            elif arg.startswith('-noverify'):
                verifyDescription = False
            elif url == u'':
                url = arg
            else:
                description.append(arg)
    description = u' '.join(description)
    bot = UploadRobot(url, description, keepFilename, verifyDescription)
    bot.run()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
