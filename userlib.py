# -*- coding: utf-8  -*-
"""
Library to work with users, their pages and talk pages.
"""
__version__ = '$Id$'

import re
import wikipedia, query



class AutoblockUser(wikipedia.Error):
    """
    The class AutoblockUserError is an exception that is raised whenever
    an action is requested on a virtual autoblock user that's not available
    for him (i.e. roughly everything except unblock).
    """
class UserActionRefuse(wikipedia.Error): pass

class BlockError(UserActionRefuse): pass

class AlreadyBlocked(BlockError): pass

class UnblockError(UserActionRefuse): pass

class BlockIDError(UnblockError): pass

class AlreadyUnblocked(UnblockError): pass

class User(object):
    """
    A class that represents a Wiki user.
    Has getters for the user's User: an User talk: (sub-)pages,
    as well as methods for blocking and unblocking.
    """

    def __init__(self, site, name):
        """
        Initializer for a User object.

        Parameters:
        site - a wikipedia.Site object
        name - name of the user, without the trailing User:
        """
        if type(site) in [str, unicode]:
            self._site = wikipedia.getSite(site)
        else:
            self._site = site
        self._name = name
        self._blocked = None #None mean not loaded
        self._groups = None #None mean not loaded
        #self._editcount = -1 # -1 mean not loaded
        self._registrationTime = -1
        #if self.site().versionnumber() >= 16:
        #    self._urToken = None
        if name[0] == '#':
            #This user is probably being queried for purpose of lifting an autoblock.
            wikipedia.output("This is an autoblock ID, you can only use to unblock it.")
            
            

    
    def site(self):
        return self._site
    
    def name(self):
        return self._name
    
    def __str__(self):
        return u'%s:%s' % (self.site() , self.name() )
    
    def __repr__(self):
        return self.__str__()
    
    def _load(self):
        getall(self.site(), [self])
        return
    
    def registrationTime(self, force = False):
        if not hasattr(self, '_registrationTime') or force:
            self._load()
        return self._registrationTime
    
    def editCount(self, force = False):
        if not hasattr(self, '_editcount') or force:
            self._load()
        return self._editcount
    
    def isBlocked(self, force = False):
        if not self._blocked or force:
            self._load()
        return self._blocked
    
    def groups(self, force = False):
        if not self._groups or force:
            self._load()
        return self._groups
    
    def getUserPage(self, subpage=''):
        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so has no user pages per se.
            raise AutoblockUser
        if subpage:
            subpage = '/' + subpage
        return wikipedia.Page(self.site(), self.name() + subpage, defaultNamespace=2)

    def getUserTalkPage(self, subpage=''):
        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so has no user talk pages per se.
            raise AutoblockUser
        if subpage:
            subpage = '/' + subpage
        return wikipedia.Page(self.site(), self.name() + subpage, defaultNamespace=3)

    def editedPages(self, limit=500):
        """ Deprecated function that wraps 'contributions'
        for backwards compatibility
        """
        for page in self.contributions(limit):
            yield page[0]

    def sendMail(self, subject = u'', text = u'', ccMe = False):
        if not hasattr(self, '_mailable'):
            self._load()
        if not self._mailable:
            raise UserActionRefuse("This user is not mailable")
        
        if not self.site().isAllowed('sendemail'):
            raise UserActionRefuse("You don't have permission to send mail")
        
        if wikipedia.config.use_api and self.site().versionnumber() >= 14:
            pass # will handle NotImplementedError later
        else:
            return self.sendMailOld(subject, text, ccMe)
        
        params = {
            'action': 'emailuser',
            'target': self.name(),
            'token': self.site().getToken(),
            'subject': subject,
            'text': text,
        }
        if ccMe:
            params['ccme'] = 1
        
        result = query.GetData(params, self.site())
        if 'error' in result:
            code = result['error']['code']
            if code == 'usermaildisabled ':
                wikipedia.output("User mail has been disabled")
            #elif code == '':
            #    
            
        elif 'emailuser' in result:
            if result['emailuser']['result'] == 'Success':
                wikipedia.output(u'Email sent.')
                return True
        
        return False
    
    def sendMailOld(self, subject = u'', text = u'', ccMe = False):
        addr = self.site().put_address('Special:EmailUser')
        predata = {
            "wpSubject" : subject,
            "wpText" : text,
            'wpSend' : "Send",
            'wpCCMe' : '0',
        }
        if ccMe:
            predata['wpCCMe'] = '1'
        
        predata['wpEditToken'] = self.site().getToken()

        response, data = self.site().postForm(address, predata, sysop = False)
        
        if data:
            if 'var wgAction = "success";' in data:
                wikipedia.output(u'Email sent.')
                return True
            else:
                wikipedia.output(u'Email not sent.')
                return False
        else:
            wikipedia.output(u'No data found.')
            return False

    
    def contributions(self, limit = 500, namespace = []):
        """ Yields pages that the user has edited, with an upper bound of ``limit''.
        Pages returned are not guaranteed to be unique
        (straight Special:Contributions parsing, in chunks of 500 items)."""
        # please stay this in comment until the regex is fixed
        #if wikipedia.config.use_api:
        #for pg, oldid, date, comment in self._ContributionsOld(limit):
        #    yield pg, oldid, date, comment
        #return

        params = {
            'action': 'query',
            'list': 'usercontribs',
            'ucuser': self.name(),
            'ucprop': ['ids','title','timestamp','comment'],# 'size','flags'],
            'uclimit': int(limit),
            'ucdir': 'older',
        }
        if limit > wikipedia.config.special_page_limit:
            params['uclimit'] = wikipedia.config.special_page_limit
            if limit > 5000 and self.site().isAllowed('apihighlimits'):
                params['uclimit'] = 5000
        
        if namespace:
            params['ucnamespace'] = namespace
        # An user is likely to contribute on several pages,
        # keeping track of titles
        nbresults = 0
        while True:
            result = query.GetData(params, self.site())
            if 'error' in result:
                wikipedia.output('%s' % result)
                raise wikipedia.Error
            for c in result['query']['usercontribs']:
                yield (wikipedia.Page(self.site(), c['title'], defaultNamespace=c['ns']),
                  c['revid'],
                  wikipedia.parsetime2stamp(c['timestamp']),
                  c['comment']
                )
                nbresults += 1
                if nbresults >= limit:
                    break
            if 'query-continue' in result and nbresults < limit:
                params['ucstart'] = result['query-continue']['usercontribs']['ucstart']
            else:
                break
        return

    def _contributionsOld(self, limit = 250, namespace = []):

        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so has no contribs.
            raise AutoblockUser

        #
        #TODO: fix contribRX regex
        #
        offset = 0
        step = min(limit,500)
        older_str = None
        
        if self.site().versionnumber() <= 11:
            older_str = self.site().mediawiki_message('sp-contributions-older')
        else:
            older_str = self.site().mediawiki_message('pager-older-n')
        
        if older_str.startswith('{{PLURAL:$1'):
            older_str = older_str[13:]
            older_str = older_str[older_str.find('|')+1:]
            older_str = older_str[:-2]
        older_str = older_str.replace('$1',str(step))

        address = self.site().contribs_address(self.name(),limit=step)
        contribRX = re.compile(r'<li[^>]*> *<a href="(?P<url>[^"]*?)" title="[^"]+">(?P<date>[^<]+)</a>.*>%s</a>\) *(<span class="[^"]+">[A-Za-z]</span>)* *<a href="[^"]+" (class="[^"]+" )?title="[^"]+">(?P<title>[^<]+)</a> *(?P<comment>.*?)(?P<top><strong> *\(top\) *</strong>)? *(<span class="mw-rollback-link">\[<a href="[^"]+token=(?P<rollbackToken>[^"]+)%2B%5C".*%s</a>\]</span>)? *</li>' % (self.site().mediawiki_message('diff'),self.site().mediawiki_message('rollback') ) )


        while offset < limit:
            data = self.site().getUrl(address)
            for pg in contribRX.finditer(data):
                url = pg.group('url')
                oldid = url[url.find('&amp;oldid=')+11:]
                date = pg.group('date')
                comment = pg.group('comment')
                #rollbackToken = pg.group('rollbackToken')
                top = None
                if pg.group('top'):
                    top = True

                # top, new, minor, should all go in a flags field
                yield wikipedia.Page(self.site(), pg.group('title')), oldid, date, comment

                offset += 1
                if offset == limit:
                    break
            nextRX = re.search('\(<a href="(?P<address>[^"]+)"[^>]*>' + older_str + '</a>\)',data)
            if nextRX:
                address = nextRX.group('address').replace('&amp;','&')
            else:
                break
    
    def uploadedImages(self, number = 10):
        try:
            if wikipedia.config.use_api and self.site().versionnumber() >= 11:
                apitest = self.site().api_address()
                del apitest
            else:
                raise NotImplementedError #No enable api or version not support
        except NotImplementedError:
            for p,t,c,a in self._uploadedImagesOld(number):
                yield p,t,c,a
            return
        
        params = {
            'action': 'query',
            'list': 'logevents',
            'letype': 'upload',
            'leuser': self.name(),
            'lelimit': int(number),
        }
        count = 0
        while True:
            data = query.GetData(params, self.site())
            for info in data['query']['logevents']:
                count += 1
                yield wikipedia.ImagePage(self.site(), info['title']), info['timestamp'], info['comment'], False
                
                if count >= number:
                    break
            
            if 'query-continue' in data and count < number:
                params['lestart'] = data['query-continue']['logevents']['lestart']
            else:
                break
        
    
    def _uploadedImagesOld(self, number = 10):
        """Yield ImagePages from Special:Log&type=upload"""

        regexp = re.compile('<li[^>]*>(?P<date>.+?)\s+<a href=.*?>(?P<user>.+?)</a> .* uploaded "<a href=".*?"(?P<new> class="new")? title="(Image|File):(?P<image>.+?)"\s*>(?:.*?<span class="comment">(?P<comment>.*?)</span>)?', re.UNICODE)

        path = self.site().log_address(number, mode = 'upload', user = self.name())
        html = self.site().getUrl(path)

        redlink_key = self.site().mediawiki_message('red-link-title')
        redlink_tail_len = None
        if redlink_key.startswith('$1 '):
            redlink_tail_len = len(redlink_key[3:])

        for m in regexp.finditer(html):
            image = m.group('image')
            deleted = False
            if m.group('new'):
                deleted = True
                if redlink_tail_len:
                    image = image[0:0-redlink_tail_len]

            date = m.group('date')
            comment = m.group('comment') or ''

            yield wikipedia.ImagePage(self.site(), image), date, comment, deleted
    
    def block(self, expiry = None, reason = None, anon= True, noCreate = False,
          onAutoblock = False, banMail = False, watchUser = False, allowUsertalk = True,
          reBlock = False):
        """
        Block the user by API.

        Parameters:
        expiry - expiry time of block, may be a period of time (incl. infinite)
                 or the block's expiry time
        reason - reason for block
        anonOnly - is the block affecting only anonymous users?
        noSignup - does the block disable account creation?
        enableAutoblock - is autoblock enabled on the block?
        emailBan - prevent user from sending e-mail?
        watchUser - watch the user's user and talk pages?
        allowUsertalk - allow this user to edit own talk page?

        The default values for block options are set to as most unrestrictive
        """

        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so can't be blocked.
            raise AutoblockUser
        if self.isBlocked() and not reBlock:
            raise AlreadyBlocked()
        
        self.site()._getActionUser('block', sysop=True)
        
        if not expiry:
            expiry = wikipedia.input(u'Please enter the expiry time for the block:')
        if not reason:
            reason = wikipedia.input(u'Please enter a reason for the block:')
        
        try:
            if wikipedia.config.use_api and self.site().versionnumber() >= 12:
                x = self.site().api_address()
                del x
            else:
                raise NotImplementedError
        except NotImplementedError:
            return self._blockOld(expiry, reason, anon, noCreate,
              onAutoblock, banMail, watchUser, allowUsertalk, reBlock)
        
        params = {
            'action': 'block',
            'user': self.name(),
            'token': self.site().getToken(self, sysop = True),
            'reason': reason,
            #'':'',
        }
        if expiry:
            params['expiry'] = expiry
        if anon:
            params['anononly'] = 1
        if noCreate:
            params['nocreate'] = 1
        if onAutoblock:
            params['autoblock'] = 1
        if banMail:
            params['noemail'] = 1
        #if watchUser:
        #    
        if reBlock:
            params['reblock'] = 1
        if allowUsertalk:
            params['allowusertalk'] = 1
        
        data = query.GetData(params, self.site(), sysop=True)
        if 'error' in data: #error occured
            errCode = data['error']['code']
            if errCode == 'alreadyblocked':
                raise AlreadyBlocked()
            elif errCode == 'blockedasrange':
                raise AlreadyBlocked("Range Blocked")
            #elif errCode == 'invalidrange':
            #    pass
            elif errCode == 'invalidexpiry':
                raise BlockError("Invaild expiry")
            elif errCode == 'pastexpiry ':
                raise BlockError("expiry time is the past")
            elif errCode == 'cantblock-email':
                raise BlockError("You don't have permission to ban mail")
            
        elif 'block' in data: #success
                return True
        else:
            wikipedia.output("Unknown Error, result: %s" % data)
            raise BlockError
        raise False

    def _blockOld(self, expiry, reason, anonOnly, noSignup, enableAutoblock, emailBan,
                watchUser, allowUsertalk):
        """
        Block the user by web page.

        """

        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so can't be blocked.
            raise AutoblockUser
        sefl.site()._getActionUser('block', sysop=True)
        
        if expiry is None:
            expiry = input(u'Please enter the expiry time for the block:')
        if reason is None:
            reason = input(u'Please enter a reason for the block:')

        token = self.site().getToken(self, sysop = True)

        wikipedia.output(u"Blocking [[User:%s]]..." % self.name())

        boolStr = ['0','1']
        predata = {
            'wpBlockAddress': self.name(),
            'wpBlockOther': expiry,
            'wpBlockReasonList': reason,
            'wpAnonOnly': boolStr[anonOnly],
            'wpCreateAccount': boolStr[noSignup],
            'wpEnableAutoblock': boolStr[enableAutoblock],
            'wpEmailBan': boolStr[emailBan],
            'wpWatchUser': boolStr[watchUser],
            'wpAllowUsertalk': boolStr[allowUsertalk],
            'wpBlock': 'Block this user',
            'wpEditToken': token
        }

        address = self.site().block_address()
        response, data = self.site().postForm(address, predata, sysop = True)

        if data:
            if self.site().mediawiki_message('ipb_already_blocked').replace('$1', self.name()) in data:
                raise AlreadyBlockedError
            
            raise BlockError
        return True

    def unblock(self, reason=None):
        """
        Unblock the user.

        Parameter:
        reason - reason for block
        """

        if self.name()[0] == '#':
            blockID = self.name()[1:]
        else:
            blockID = self._getBlockID()

        self._unblock(blockID,reason)

    def _getBlockID(self):
        wikipedia.output(u"Getting block id for [[User:%s]]..." % self.name())

        address = self.site().blocksearch_address(self.name())
        data = self.site().getUrl(address)
        bIDre = re.search(r'action=unblock&amp;id=(\d+)', data)
        if not bIDre:
            wikipedia.output(data)
            raise BlockIDError

        return bIDre.group(1)

    def _unblock(self, blockID, reason):
        wikipedia.output(u"Unblocking [[User:%s]]..." % self.name())

        token = self.site().getToken(self, sysop = True)

        predata = {
            'id': blockID,
            'wpUnblockReason': reason,
            'wpBlock': 'Unblock this address',
            'wpEditToken': token,
        }
        address = self.site().unblock_address()

        response, data = self.site().postForm(address, predata, sysop = True)
        if response.code != 302:
            if self.site().mediawiki_message('ipb_cant_unblock').replace('$1',blockID) in data:
                raise AlreadyUnblockedError
            raise UnblockError, data
        return True

def getall(site, users, throttle=True, force=False):
    """Bulk-retrieve users data from site
 
    Arguments: site = Site object
               users = iterable that yields User objects

    """
    users = list(users)  # if pages is an iterator, we need to make it a list
    if len(users) > 1: wikipedia.output(u'Getting %d users data from %s...' % (len(users), site))
    _GetAllUI(site, users, throttle, force).run()

class _GetAllUI(object):
    def __init__(self, site, users, throttle, force):
        self.site = site
        self.users = []
        self.throttle = throttle
        self.force = force
        self.sleeptime = 15
    
        for user in users:
            if not hasattr(user, '_editcount') or force:
                self.users.append(user)
            elif wikipedia.verbose:
                wikipedia.output(u"BUGWARNING: %s already done!" % user.name())
     
    def run(self):
        if self.users:
            while True:
                try:
                    data = self.getData()
                except Exception, e:
                    # Print the traceback of the caught exception
                    print e
                    raise
                else:
                    break
            
            for uj in self.users:
                x = data[uj.name()]
                uj._editcount = x['editcount']
                if 'groups' in x:
                    uj._groups = x['groups']
                else:
                    uj._groups = []
                if x['registration']:
                    uj._registrationTime = wikipedia.parsetime2stamp(x['registration'])
                else:
                    uj._registrationTime = 0
                uj._mailable = ("emailable" in x)
                uj._blocked = ('blockedby' in x)
                #if self._blocked: #Get block ID
        
    def getData(self):
        datas = {}
        params = {
            'action': 'query',
            'list': 'users',
            'usprop': ['blockinfo', 'groups', 'editcount', 'registration', 'emailable', 'gender'],
            'ususers': u'|'.join([n.name() for n in self.users]),
        }
        for n in query.GetData(params, self.site)['query']['users']:
            datas[n['name']] = n
        return datas

if __name__ == '__main__':
    """
    Simple testing code for the [[User:Example]] on the English Wikipedia.
    """
    try:
        Site = wikipedia.getSite()
        exampleUser = User(Site, 'Example')
        wikipedia.output(exampleUser.getUserPage().get())
        wikipedia.output(exampleUser.getUserPage('Lipsum').get())
        wikipedia.output(exampleUser.getUserTalkPage().get())
    finally:
        wikipedia.stopme()
