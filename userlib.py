# -*- coding: utf-8  -*-
"""
Library to work with users, their pages and talk pages.
"""

import wikipedia

class AutoblockUserError(wikipedia.Error):
  """
  The class AutoblockUserError is an exception that is raised whenever
  an action is requested on a virtual autoblock user that's not available
  for him (i.e. roughly everything except unblock).
  """

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

  def getUserPage(self,subpage=''):
    if self.name[0] == '#':
      #This user is probably being queried for purpose of lifting
      #an autoblock, so has no user pages per se.
      raise AutoblockUserError
    fullpagename = self.site.namespace(2) + ':' + self.name
    if subpage:
      fullpagename += '/' + subpage
    return wikipedia.Page(self.site,fullpagename)

  def getUserTalkPage(self,subpage=''):
    if self.name[0] == '#':
      #This user is probably being queried for purpose of lifting
      #an autoblock, so has no user talk pages per se.
      raise AutoblockUserError
    fullpagename = self.site.namespace(3) + ':' + self.name
    if subpage:
      fullpagename += '/' + subpage
    return wikipedia.Page(self.site,fullpagename)

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
