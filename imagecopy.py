# -*- coding: utf-8 -*-
"""
Script to copy files from a local Wikimedia wiki to Wikimedia Commons
using CommonsHelper to not leave any information out and CommonSense
to automatically categorise the file. After copying, a NowCommons
template is added to the local wiki's file. It uses a local exclusion
list to skip files with templates not allow on Wikimedia Commons. If no
categories have been found, the file will be tagged on Commons.

This bot uses a graphical interface and may not work from commandline
only environment.

Requests for improvement for CommonsHelper output should be directed to
Magnus Manske at his talk page. Please be very specific in your request
(describe current output and expected output) and note an example file,
so he can test at: [[de:Benutzer Diskussion:Magnus Manske]]. You can
write him in German and English.

Arguments:

  -project      Project to copy from (default: wikipedia)
  -lang         Language to copy from (default: nl)
  -cat          Category to copy to Wikimedia Commons (required)
  -start        Start at index within category (optional)

Known issues/FIXMEs (no critical issues known):
* Some variable names are in Spanish, which makes the code harder to read.
* Depending on sorting within a file category, the "next batch" is sometimes
  not working, leading to an endless loop
* Different wikis can have different exclusion lists. A parameter for the
  exclusion list Uploadbot.localskips.txt would probably be nice.
* Bot should probably use API instead of query.php
* Should request alternative name if file name already exists on Commons
* Exits after last file in category was processed, aborting all pending
  threads.
* Should take user-config.py as input for project and lang variables
* Should require a Commons user to be present in user-config.py before
  working
* Should probably have an input field for additional categories
* Should probably have an option to change uploadtext with file
* required i18n options for NowCommons template (f.e. {{subst:ncd}} on
  en.wp. Currently needs customisation to work properly. Bot was tested
  succesfully on nl.wp (12k+ files copied and deleted locally) and en.wp
  (about 100 files copied and SieBot has bot approval for tagging {{ncd}}
  with this bot)
* {{NowCommons|xxx}} requires the namespace prefix Image: on most wikis
  and can be left out on others. This needs to be taken care of when
  implementing i18n
* This bot should probably get a small tutorial at meta with a few
  screenshots.
"""
#
# Based on upload.py by:
# (C) Rob W.W. Hooft, Andre Engels 2003-2007
# (C) Wikipedian, Keichwa, Leogregianin, Rikwade, Misza13 2003-2007
#
# New bot by:
# (C) Kyle/Orgullomoore, Siebrand Mazeland 2007
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#

from Tkinter import *
import os, sys, re, codecs
import urllib, httplib, urllib2
import catlib, thread, webbrowser
import wikipedia, config
NL=''

def pageText(url):
    request=urllib2.Request(url)
    user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
    print url
    request.add_header("User-Agent", user_agent)
    response=urllib2.urlopen(request)
    text=response.read()
    response.close()
    return text

def post_multipart(host, selector, fields, files, cookies):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    conn = httplib.HTTPConnection(host)
    conn.putrequest('POST', selector)
    conn.putheader('content-type', content_type)
    conn.putheader('content-length', str(len(body)))
    conn.putheader("User-agent", 'RobHooftWikiRobot/1.0')
    if cookies:
        conn.putheader('Cookie',cookies)
    conn.endheaders()
    conn.send(body)
    response = conn.getresponse()
    returned_html = response.read()
    conn.close()
    return response, returned_html

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


class UploadRobot:
    def __init__(self, url, description = u'', keepFilename = False, verifyDescription = False, ignoreWarning = True, targetSite = None, urlEncoding = None, newname=None):
        """
        ignoreWarning - Set this to True if you want to upload even if another
                        file would be overwritten or another mistake would be
                        risked.
                        Attention: This parameter doesn't work yet for unknown reason.
        """
        self.url = url
        self.urlEncoding = urlEncoding
        self.description = description
        self.keepFilename = keepFilename
        self.verifyDescription = verifyDescription
        self.ignoreWarning = ignoreWarning
        self.newname=newname
        if config.upload_to_commons:
            self.targetSite = targetSite or wikipedia.getSite('commons', 'commons')
        else:
            self.targetSite = targetSite or wikipedia.getSite()
        self.targetSite=wikipedia.Site('commons', 'commons')
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
            print "Couldn't download the file."
            return
        file.close()
        # Isolate the pure name
        filename = self.newname
        if '/' in filename:
            filename = filename.split('/')[-1]
        if '\\' in filename:
            filename = filename.split('\\')[-1]
        if self.urlEncoding:
            filename = urllib.unquote(filename)
            filename = filename.decode(self.urlEncoding)
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
    #         formdata["wpUploadSource"] = wikipedia.input(u"Source of file: ")
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
            response, returned_html = post_multipart(self.targetSite.hostname(),
                                  self.targetSite.upload_address(),
                                  formdata.items(),
                                  (('wpUploadFile', encodedFilename, contents),),
                                  cookies = self.targetSite.cookies()
                                  )
            returned_html = returned_html.decode(self.targetSite.encoding())
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
            self.url = wikipedia.input(u'File or URL where file is now:')
        return self.upload_image()

def getcatimgs(catP, cpfrom=''):
    toreturn=[]
    #http://commons.wikimedia.org/w/query.php?what=category&cptitle=GFDL&cplimit=500
    done=0
    while done==0:
        if catP !='':
            path='http://'+catP.site().hostname()+'/w/query.php?what=content|imageinfo|category&cptitle='+catP.urlname()+'&cpfrom='+six[0]+':'+cpfrom+'&cplimit=50&cpnamespace=6&iiurl&format=xml'
        else:
            path='http://'+six[1].hostname()+'/w/query.php?what=content|imageinfo|allpages&apfrom='+cpfrom+'&aplimit=50&apnamespace=6&iiurl&format=xml'
        crudo=pageText(path)
        print 'got'
        if '<category next="' in crudo:
            cpfrom=crudo.split('<category next="')[1].split('"')[0]
        elif '<allpages next="' in crudo:
            cpfrom=crudo.split('<allpages next="')[1].split('"')[0]
        else:
            done=1
        cpfrom=urllib.quote(cpfrom)
        paginas=crudo.split('<page>')
        for pagina in paginas[1:]:
            ns=pagina.split('<ns>')[1].split('</ns>')[0]
            if ns =='6':
                try:
                    imageblock=pagina.split('<image ')[1].split('>')[0]
                    url=imageblock.split('url="')[1].split('"')[0]
                    uploader=imageblock.split('user="')[1].split('"')[0]
                    imtit=pagina.split('<title>')[1].split('</title>')[0]
                    contentblock=pagina.split('<content ')[1].split('>')[0]
                    if contentblock[-1]=='/':
                        content=''
                    else:
                        content=pagina.split('<content '+contentblock+'>')[1].split('</content>')[0]
                    toappend=(url, imtit.decode('utf-8'), content, uploader)
                    yield toappend
                except:
                    continue
def pageTextPost(url,postinfo):
    print url
    m=re.search(ur'http://(.*?)(/.*)',url)
    if m==None:
            return
    else:
            domain=m.group(1)
            path=m.group(2)
            
    h = httplib.HTTP(domain)
    h.putrequest('POST', path)
    h.putheader('Host', domain)
    h.putheader('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7')
    h.putheader('Content-Type', 'application/x-www-form-urlencoded')
    h.putheader('Content-Length', str(len(postinfo)))
    h.endheaders()
    h.send(postinfo)
    errcode, errmsg, headers = h.getreply()
    data = h.getfile().read() # Obtener el HTML en bruto/wiki?title=Special:Userlogin&action=submitlogin&type=signup HTTP/1.1

    return data
def getCH(url, imageP, nn, tenemosuncambio):
    tosend={'language':str(imageP.site()).split(':')[1],
            'image':imageP.title(),
            'newname':'',
            'project':str(imageP.site()).split(':')[0],
            'commonsense':'1',
            'doit':'Get+text'}
    for k in tosend.keys():
        tosend[k]=tosend[k].encode('utf-8')
    tosend=urllib.urlencode(tosend)
    print tosend
    CH=pageTextPost('http://tools.wikimedia.de/~magnus/commonshelper.php', tosend)
    print 'Got CH desc.'
    tablock=CH.split('<textarea ')[1].split('>')[0]
    CH=CH.split('<textarea '+tablock+'>')[1].split('</textarea>')[0]
    CH=CH.replace('&times;', '×')
    CH=CH.decode('utf-8')
    if not '[[category:' in CH.lower():
        CH=u'\n\n{{BotMoveToCommons|'+six[1].hostname().split('.org')[0]+'}}'+CH
    ##add {{NowCommons}}

    bot = UploadRobot(url, CH, keepFilename=True, verifyDescription=False, newname=nn, urlEncoding='utf-8')
    bot.run()
    imtxt=imageP.get()
    if tenemosuncambio==1:
        imageP.put(imtxt+u'\n\n{{NowCommons|'+nn.decode('utf-8')+'}}', u'{{NowCommons}}')
    else:
        imageP.put(imtxt+u'\n\n{{NowCommons}}', u'{{NowCommons}}')
#-etiqueta ok skip view
#texto
archivo=wikipedia.config.datafilepath("Uploadbot.localskips.txt")
try:
    open(archivo, 'r')
except IOError:
    tocreate=open(archivo, 'w')
    tocreate.write("{{NowCommons")
    tocreate.close()
    
def getautoskip():
    f=codecs.open(archivo, 'r', 'utf-8')
    txt=f.read()
    f.close()
    toreturn=txt.split('{{')[1:]
    return toreturn
    
class Tkstuff:
    def __init__(self, nP, contenido, uploader, commonsconflict=0):
        self.root=Tk()
        #"%dx%d%+d%+d" % (width, height, xoffset, yoffset)
        #Always appear the same size and in the bottom-left corner
        self.root.geometry("600x200+100-100")
        self.nP=wikipedia.Page(six[1], 'Image:'+nP)
        self.root.title(self.nP.titleWithoutNamespace())
        self.changename=''
        self.skip=0
        uploader=uploader.decode('utf-8')
        scrollbar=Scrollbar(self.root, orient=VERTICAL)
        etiqueta=Label(self.root,text=u"Enter new name or leave blank.")
        imageinfo=Label(self.root, text='Uploaded by '+uploader+'.')
        texto=Text(self.root)
        texto.insert(END, contenido.decode('utf-8'))
        texto.config(state=DISABLED, height=8, width=40, padx=0, pady=0, wrap=WORD, yscrollcommand=scrollbar.set)
        scrollbar.config(command=texto.yview)
        self.entrada=Entry(self.root)
        
        self.listado=Listbox(self.root, bg="white", height=5)
        
        self.plantillas=[]
        
        for chuleta in contenido.split('{{')[1:]:
            trytosplit=re.split(ur'(?:\}\}|\|)', chuleta)
            if trytosplit !=[]:
                plantilla=trytosplit[0]
                for char in ['}', ']', '{', '[']:
                    if char in plantilla:
                        plantilla=''
                if plantilla.lower()=='information':
                    plantilla=''
                if plantilla !='':
                    self.plantillas.append(plantilla)
        for plantilla in self.plantillas:
            self.listado.insert(END, plantilla)
        addB=Button(self.root, text="Add to AutoSkip", command=self.add2autoskip)
        browser=Button(self.root, text='View in browser', command=self.oib)
        saltar=Button(self.root, text="Skip", command=self.skipF)
        ok=Button(self.root, text="OK", command=self.okF)
        
##Start grid
        etiqueta.grid(row=0)
        ok.grid(row=0, column=1, rowspan=2)
        saltar.grid(row=0, column=2, rowspan=2)
        browser.grid(row=0, column=3, rowspan=2)
        
        self.entrada.grid(row=1)

        
        texto.grid(row=2, column=1, columnspan=3)
        scrollbar.grid(row=2, column=5)
        self.listado.grid(row=2, column=0)
        
        addB.grid(row=3, column=0)
        imageinfo.grid(row=3, column=1, columnspan=4)
    def okF(self):
        self.changename=self.entrada.get()
        self.root.destroy()
    def skipF(self):
        self.skip=1
        self.root.destroy()
    def oib(self):
        webbrowser.open('http://'+six[1].hostname()+'/wiki/'+self.nP.urlname())
    def add2autoskip(self):
        identificador=int(self.listado.curselection()[0])
        template=self.plantillas[identificador]
        toadd=codecs.open(archivo, 'a', 'utf-8')
        toadd.write('{{'+template)
        toadd.close()
        self.skipF()
        
    def getnewname(self):
        self.root.mainloop()
        return (self.changename, self.skip)

def doiskip(pagetext):
    saltos=getautoskip()
    #print saltos
    for salto in saltos:
        rex=ur'\{\{\s*['+salto[0].upper()+salto[0].lower()+']'+salto[1:]+'(\}\}|\|)'
        #print rex
        if re.search(rex, pagetext):
            return True
    return False

six=['These should', 'both be changed']

def main(args):

    lang=u''
    site=u''
    cat = u''
    startingpoint=u''
    verifyDescription=False
    keepFilename = False

    for arg in args:
        if arg.startswith('-start:'):
            startingpoint=arg.split('-start:')[1]
        elif arg.startswith('-cat:'):
            cat=arg.split('-cat:')[1]
        elif arg.startswith('-lang:'):
            lang=arg.split('-lang:')[1]
        elif arg.startswith('-site:'):
            site=arg.split('-site:')[1]
        else:
            print 'Argument: '+str([arg])+' is not valid'
    print 'ourcat: '+cat
    if (len(site)>1, len(lang)>1)==(True, True):
        try:
            sitio=wikipedia.Site(lang, site)
            six[1]=sitio
        except:
            print str((site, lang))+' didnt work out. Defaulting to nl.wikipedia.'
            six[1]=wikipedia.Site('nl', 'wikipedia')
    else:
        six[1]=wikipedia.Site('nl', 'wikipedia')
    print "Working from "+str(six[1])
    seis=pageText('http://'+six[1].hostname()+'/w/query.php?what=namespaces&format=xml').split('<ns id="6">')[1].split('</ns>')[0]
    seis=urllib.quote(seis)
    six[0]=seis
    print six
    if cat != u'':
        categ=wikipedia.Page(six[1], 'Category:'+cat.decode('utf-8'))
        #Wikipedia:Verplaats naar Wikimedia Commons
        categorizadas=getcatimgs(categ, startingpoint)

    elif startingpoint != u'':
        categorizadas=getcatimgs('', startingpoint)


    for categorizada in categorizadas:
        #print categorizada
        url=categorizada[0]
        tenemosuncambio=0
        nn=url.split('/')[-1]
        if doiskip(categorizada[2]):
            print "Autoskipping " + nn
            continue
        #changename=wikipedia.input(u'The name on Commons will be '+nn+', ok? Enter a better name or press ENTER to proceed: ')
        changename=Tkstuff(nn, categorizada[2], categorizada[3]).getnewname()
        print ('changename', changename)
        if len(changename[0])!=0:
            nn=changename[0].encode('utf-8')
            tenemosuncambio=1
        elif changename[1]==1:
            print 'skipping this file'
            continue
        imageP=wikipedia.Page(six[1], categorizada[1])
        CP=wikipedia.Page(wikipedia.Site('commons', 'commons'), 'Image:'+nn.decode('utf-8'))
        if CP.exists():
            nn=Tkstuff(nn[0], categorizada[2], categorizada[3], commonsconflict=1).getnewname()
        if nn[1]==1:
            print 'skipping this file'
            continue
        
        thread.start_new_thread(getCH, (url, imageP, nn, tenemosuncambio))

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        wikipedia.stopme()
