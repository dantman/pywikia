# -*- coding: utf-8  -*-
"""
Library to work with users, their pages and talk pages.
"""
__version__ = '$Id$'

import re, time
import wikipedia, query



class AutoblockUserError(wikipedia.Error):
    """
    The class AutoblockUserError is an exception that is raised whenever
    an action is requested on a virtual autoblock user that's not available
    for him (i.e. roughly everything except unblock).
    """

class BlockError(wikipedia.Error): pass

class AlreadyBlockedError(BlockError): pass

class UnblockError(wikipedia.Error): pass

class BlockIDError(UnblockError): pass

class AlreadyUnblockedError(UnblockError): pass

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
        if type(site) == str:
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
    
    def site(self):
        return self._site
    
    def name(self):
        return self._name
    
    def __str__(self):
        return u'%s:%s' % (self.site() , self.name() )
    
    def __repr__(self):
        return self.__str__()
    
    def _load(self):
        data = batchLoadUI(self.name(), self.site()).values()[0]
        if 'missing' in data or 'invalid' in data:
            raise wikipedia.Error('No such user or invaild username')
        
        self._editcount = data['editcount']
        
        if 'groups' in data:
            self._groups = data['groups']
        else:
            self._groups = []
        
        if data['registration']:
            self._registrationTime = time.strftime("%Y%m%d%H%M%S", time.strptime(data['registration'], "%Y-%m-%dT%H:%M:%SZ") )
        else:
            self._registrationTime = 0
        
        self._blocked = ('blockedby' in data)
    
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
            raise AutoblockUserError
        if subpage:
            subpage = '/' + subpage
        return wikipedia.Page(self.site(), self.name() + subpage, defaultNamespace=2)

    def getUserTalkPage(self, subpage=''):
        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so has no user talk pages per se.
            raise AutoblockUserError
        if subpage:
            subpage = '/' + subpage
        return wikipedia.Page(self.site(), self.name() + subpage, defaultNamespace=3)

    def editedPages(self, limit=500):
        """ Deprecated function that wraps 'contributions'
        for backwards compatibility
        """
        for page in self.contributions(limit):
            yield page[0]

    def contributions(self, limit=500, namespace = []):
        """ Yields pages that the user has edited, with an upper bound of ``limit''.
        Pages returned are not guaranteed to be unique
        (straight Special:Contributions parsing, in chunks of 500 items)."""

        if self.name()[0] == '#':
            #This user is probably being queried for purpose of lifting
            #an autoblock, so has no contribs.
            raise AutoblockUserError

        # please stay this in comment until the regex is fixed
        #if wikipedia.config.use_api:
        for pg, oldid, date, comment in self._apiContributions(limit):
            yield pg, oldid, date, comment
        return
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
    
    def _apiContributions(self, limit =  250, namespace = []):
        params = {
            'action': 'query',
            'list': 'usercontribs',
            'ucuser': self.name(),
            'ucprop': 'ids|title|timestamp|comment',# |size|flags',
            'uclimit': int(limit),
            'ucdir': 'older',
        }
        if limit > wikipedia.config.special_page_limit:
            params['uclimit'] = wikipedia.config.special_page_limit
            if limit > 5000 and self.site().isAllowed('apihighlimits'):
                params['uclimit'] = 5000
        
        if namespace:
            params['ucnamespace'] = query.ListToParam(namespace)
        # An user is likely to contribute on several pages,
        # keeping track of titles
        nbresults = 0
        while True:
            result = query.GetData(params, self.site())
            if 'error' in result:
                wikipedia.output('%s' % result)
                raise wikipedia.Error
            for c in result['query']['usercontribs']:
                yield wikipedia.Page(self.site(), c['title'], defaultNamespace=c['ns']), c['revid'], c['timestamp'], c['comment']
                nbresults += 1
                if nbresults >= params['uclimit']:
                    break
            if 'query-continue' in result and nbresults < params['uclimit']:
                params['ucstart'] = result['query-continue']['usercontribs']['ucstart']
            else:
                break
        return

    def uploadedImages(self, number = 10):
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
    
    def _apiUploadImages(self, number = 10):
        
        params = {
            'action':'query',
            'list':'logevents',
            'letype':'upload',
            'leuser':self.name(),
            'lelimit':int(number),
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
        
    
    def block(self, expiry=None, reason=None, anonOnly=True, noSignup=False,
                enableAutoblock=False, emailBan=False, watchUser=False, allowUsertalk=True):
        """
        Block the user.

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
            raise AutoblockUserError

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
        if response.status != 302:
            if self.site().mediawiki_message('ipb_cant_unblock').replace('$1',blockID) in data:
                raise AlreadyUnblockedError
            raise UnblockError, data
        return True

def batchLoadUI(names = [], site = None):
    #
    # batch load users information by API.
    # result info: http://www.mediawiki.org/wiki/API:Query_-_Lists#users_.2F_us
    #
    if not site:
        site = wikipedia.getSite()
    elif type(site) is str or type(site) is unicode:
        site = wikipedia.getSite(site)
    
    result = {}
    params = {
        'action': 'query',
        'list': 'users',
        'usprop': 'blockinfo|groups|editcount|registration|emailable|gender',
        'ususers': query.ListToParam(names),
    }
    #if site.versionnumber() >= 16:
    #    params['ustoken'] = 'userrights'

    result = dict([(sig['name'].lower(), sig) for sig in query.GetData(params, site)['query']['users'] ])
    
    
    return result

def batchDumpInfo(user):
    totals = batchLoadUI([x.name() for x in user])
    for oj in user:
        data = totals[oj.name().lower()]
        oj._editcount = data['editcount']
        if 'groups' in data:
            oj._groups = data['groups']
        oj._blocked = ('blockedby' in data)

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
