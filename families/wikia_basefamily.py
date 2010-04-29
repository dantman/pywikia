# -*- coding: utf-8  -*-
import family

# Base file for Wikia wiki.

class Family(family.Family):

	def __init__(self):
		
		family.Family.__init__(self)
		
		self.wikia = {
			'projectns': None,
			'forums': True,
			'smw': False,
			'video': False,
			'kaltura': False,
			'profile': False,
			'userwiki': False,
		}
		
	def initNamespaces(self):
		if self.wikia['forums'] is True:
			self.wikia['forums'] = 110
		if self.wikia['smw'] is True:
			self.wikia['smw'] = 300
		if self.wikia['video'] is True:
			self.wikia['video'] = 400
		if self.wikia['kaltura'] is True:
			self.wikia['kaltura'] = 320
		if self.wikia['profile'] is True:
			self.wikia['profile'] = 202
		if self.wikia['userwiki'] is True:
			self.wikia['userwiki'] = 200
		
		if self.wikia['projectns']:
			self.namespaces[4] = { '_default':[u'%s' % self.wikia['projectns'], self.namespaces[4]['_default']] }
			self.namespaces[5] = { '_default':[u'%s talk' % self.wikia['projectns'], self.namespaces[5]['_default']] }
		
		if self.wikia['forums']:
			self.namespaces[self.wikia['forums']+0] = { '_default': u'Forum', }
			self.namespaces[self.wikia['forums']+1] = { '_default': u'Forum talk', }
		
		if self.wikia['smw']:
			#self.namespaces[self.wikia['smw']+0] = { '_default': u'Relation', }
			#self.namespaces[self.wikia['smw']+1] = { '_default': u'Relation talk', }
			self.namespaces[self.wikia['smw']+2] = { '_default': u'Property', }
			self.namespaces[self.wikia['smw']+3] = { '_default': u'Property talk', }
			self.namespaces[self.wikia['smw']+4] = { '_default': u'Type', }
			self.namespaces[self.wikia['smw']+5] = { '_default': u'Type talk', }
		
		if self.wikia['video']:
			self.namespaces[self.wikia['video']+0] = { '_default': u'Video', }
			self.namespaces[self.wikia['video']+1] = { '_default': u'Video talk', }
		
		if self.wikia['kaltura']:
			self.namespaces[self.wikia['kaltura']+0] = { '_default': u'Kaltura', }
			self.namespaces[self.wikia['kaltura']+1] = { '_default': u'Kaltura talk', }
		
		if self.wikia['profile']:
			self.namespaces[self.wikia['profile']] = { '_default': u'User profile', }
		
		if self.wikia['userwiki']:
			self.namespaces[self.wikia['userwiki']+0] = { '_default': u'UserWiki', }
			self.namespaces[self.wikia['userwiki']+1] = { '_default': u'UserWiki talk', }
		
	def scriptpath(self, code):
		return ''
		
	def code2encoding(self, code):
		return 'utf-8'
	
	def version(self, code):
		return u'1.15'
	
