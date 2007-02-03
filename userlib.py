# -*- coding: utf-8  -*-
"""
Library to work with users, their pages and talk pages.
"""

import wikipedia
import re, httplib

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

class User:
  """
  A class that represents a Wiki user.
  Has getters for the user's User: an User talk: (sub-)pages,
  as well as methods for blocking and unblocking (in future).
  """

  #TODO list:
  #- block and unblock methods
  #- browse contributions, maybe?

  def __init__(self, site, name):
    """
    Initializer for a User object.

    Parameters:
    site - a wikipedia.Site object
    name - name of the user, without the trailing User:
    """

    self.site = site
    self.name = name

  def getUserPage(self, subpage=''):
    if self.name[0] == '#':
      #This user is probably being queried for purpose of lifting
      #an autoblock, so has no user pages per se.
      raise AutoblockUserError
    fullpagename = self.site.namespace(2) + ':' + self.name
    if subpage:
      fullpagename += '/' + subpage
    return wikipedia.Page(self.site,fullpagename)

  def getUserTalkPage(self, subpage=''):
    if self.name[0] == '#':
      #This user is probably being queried for purpose of lifting
      #an autoblock, so has no user talk pages per se.
      raise AutoblockUserError
    fullpagename = self.site.namespace(3) + ':' + self.name
    if subpage:
      fullpagename += '/' + subpage
    return wikipedia.Page(self.site,fullpagename)

  def block(self, expiry=None, reason=None, AnonOnly=True, NoSignup=False, EnableAutoblock=False):
    """
    Block the user.

    Parameters:
    expiry - expiry time of block, may be a period of time (incl. infinite)
             or the block's expiry time
    reason - reason for block
    AnonOnly - is the block affecting only anonymous users?
    NoSignup - does the block disable account creation?
    EnableAutoblock - is autoblock enabled on the block?

    The default values for block options are set to as most unrestrictive
    """

    if self.name[0] == '#':
      #This user is probably being queried for purpose of lifting
      #an autoblock, so can't be blocked.
      raise AutoblockUserError

    if expiry == None:
      expiry = input(u'Please enter the expiry time for the block:')
    if reason == None:
      reason = input(u'Please enter a reason for the block:')

    token = self.site.getToken(self, sysop = True)

    wikipedia.output(u"Blocking [[User:%s]]..." % self.name)

    boolStr = ['0','1']
    predata = [
        ('wpBlockAddress', self.name),
        ('wpBlockExpiry', 'other'),
        ('wpBlockOther', expiry),
        ('wpBlockReason', reason),
        ('wpAnonOnly', boolStr[AnonOnly]),
        ('wpCreateAccount', boolStr[NoSignup]),
        ('wpEnableAutoblock', boolStr[EnableAutoblock]),
        ('wpBlock', 'Block this user'),
        ('wpEditToken', token)
        ]

    data = wikipedia.urlencode(tuple(predata))
    address = self.site.block_address()

    conn = httplib.HTTPConnection(self.site.hostname())
    conn.putrequest("POST", address)
    conn.putheader('Content-Length', str(len(data)))
    conn.putheader("Content-type", "application/x-www-form-urlencoded")
    conn.putheader("User-agent", wikipedia.useragent)
    conn.putheader('Cookie', self.site.cookies())
    conn.endheaders()
    conn.send(data)

    response = conn.getresponse()
    data = response.read()
    conn.close()

    if response.status != 302:
      if re.search('is already blocked',data):
        raise AlreadyBlockedError
      raise BlockError
    return True

  def unblock(self, reason=None):
    """
    Unblock the user.

    Parameter:
    reason - reason for block
    """

    if self.name[0] == '#':
      blockID = self.name[1:]
    else:
      blockID = self._getBlockID()

    self._unblock(blockID,reason)

  def _getBlockID(self):
    wikipedia.output(u"Getting block id for [[User:%s]]..." % self.name)

    token = self.site.getToken(self, sysop = True)
    address = self.site.blocksearch_address(self.name)

    conn = httplib.HTTPConnection(self.site.hostname())
    conn.putrequest("GET", address)
    conn.putheader("User-agent", wikipedia.useragent)
    conn.putheader('Cookie', self.site.cookies())
    conn.endheaders()
    conn.send('')

    response = conn.getresponse()
    data = response.read()
    conn.close()

    bIDre = re.search(r'action=unblock&amp;id=(\d+)',data)
    if not bIDre:
      print data
      raise BlockIDError

    return bIDre.group(1)

  def _unblock(self, blockID, reason):
    wikipedia.output(u"Unblocking [[User:%s]]..." % self.name)

    token = self.site.getToken(self, sysop = True)

    predata = [
        ('id', blockID),
        ('wpUnblockReason', reason),
        ('wpBlock', 'Unblock this address'),
        ('wpEditToken', token)
        ]

    data = wikipedia.urlencode(tuple(predata))
    address = self.site.unblock_address()

    conn = httplib.HTTPConnection(self.site.hostname())
    conn.putrequest("POST", address)
    conn.putheader('Content-Length', str(len(data)))
    conn.putheader("Content-type", "application/x-www-form-urlencoded")
    conn.putheader("User-agent", wikipedia.useragent)
    conn.putheader('Cookie', self.site.cookies())
    conn.endheaders()
    conn.send(data)

    response = conn.getresponse()
    data = response.read()
    conn.close()

    if response.status != 302:
      print data
      if re.search('Block ID \d+ not found',data):
        raise AlreadyUnblockedError
      raise UnblockError
    return True


if __name__ == '__main__':
  """
  Simple testing code for the [[User:Example]] on the English Wikipedia.
  """
  try:
    Site = wikipedia.getSite()
    exampleUser = User(Site,'Example')
    print exampleUser.getUserPage().get()
    print exampleUser.getUserPage('Lipsum').get()
    print exampleUser.getUserTalkPage().get()
  finally:
    wikipedia.stopme()
