#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This module provides a way for users of the Wikimedia toolserver to check the 
use of images from Commons on other Wikimedia wikis. It supports both running
checkusage against the database and against the live wikis. It is very 
efficient as it only creates one HTTP connection and one MySQL connection 
during its life time. It is not suitable for multithreading!
 
The CheckUsage class' constructor accept as parameters the maximum number of
wikis that should be checked, an option to use it only live and the parameters
to connect to the MySQL database. The top wikis in size will be checked. The 
class provides multiple methods:
 
get_usage(image)
This method will return a generator object that generates the usage of the 
image, returned as the following tuple: (page_namespace, page_title,
full_title). page_namespace is the numeric namespace, page_title the page title
without namespace, full_title the page title including localized namespace.
 
get_usage_db(dbname, image), get_usage_live(domain, image)
Those methods allow querying a specific wiki, respectively against the database
and against the live wiki. They accept respectively the database name and the
domain name. The return a generator which generates the same results as 
get_usage().
 
get_usage_multi(images)
Calls get_usage for each image and returns a dictionary with usages.
 
get_replag(dbname)
Returns the time in seconds since the latest known edit of dbname.
"""
#
# (C) Bryan Tong Minh, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#
 
import httplib, urlparse
from urllib import urlencode
import simplejson
 
try:
	import MySQLdb
except ImportError:
	pass
__ver__ = '0.4c'
 
def strip_ns(title):
	title = title.replace(' ', '_')
	if title.find(':') != -1:
		return title[title.find(':') + 1:]
	return title
def strip_image(title):
	if title.startswith('Image:'):
		return strip_ns(title)
	return title
 
class HTTP(object):
	def __init__(self, host):
		self._conn = httplib.HTTPConnection(host)
		#self._conn.set_debuglevel(100)
		self._conn.connect()
 
	def __request(self, method, path, headers, data):		
		if not headers: headers = {}
		if not data: data = ''
		headers['Connection'] = 'Keep-Alive'
		headers['User-Agent'] = 'MwClient/' + __ver__
 
		self._conn.request(method, path, data, headers)
 
		try:
			res = self._conn.getresponse()
		except httplib.BadStatusLine:
			self._conn.close()
			self._conn.connect()
			self._conn.request(method, path, data, headers)
			res = self._conn.getresponse()
 
		if res.status >= 500:
			self._conn.request(method, path, data, headers)
			res = self._conn.getresponse()
 
		if res.status != 200:
			raise RuntimeError, (res.status, res)
 
		return res
 
	def query_api(self, api, host, **kwargs):
		data = urlencode([(k, v.encode('utf-8')) for k, v in kwargs.iteritems()])
		if api == 'query':
			query_string = '/w/query.php?format=json&' + data
			method = 'GET'
			data = ''
		elif api == 'api':
			query_string = '/w/api.php?format=json'
			method = 'POST'
		else:
			raise ValueError('Unknown api %s' % repr(api))
 
		res = self.__request(method, query_string,
			{'Host': host, 'Content-Type': 'application/x-www-form-urlencoded'}, data)
		data = simplejson.load(res)
		res.close()
		return data
 
class CheckUsage(object):
	LIVE = ['enwiki_p']
	IGNORE = []
	COMMONS = 'commons.wikimedia.org'
 
	def __init__(self, limit = 100, sql_host = 'localhost', sql_user = '', sql_pass = '', no_db = False):
		self.conn = HTTP('wikimedia.org')
		if no_db: return
 
		# A bug in MySQLdb 1.2.1_p will force you to set
		# all your connections to use_unicode = False.
		# Please upgrade to MySQLdb 1.2.2 or higher.
		self.database = MySQLdb.connect(use_unicode = False,
			user = sql_user, passwd = sql_pass, 
			host = sql_host)
		self.cursor = self.database.cursor()
 
		self.fetch_live = []
		self.fetch_database = []
 
		self.cursor.execute('SELECT dbname, domain FROM toolserver.wiki ORDER BY size DESC LIMIT %s', (limit, ))
		for dbname, domain in self.cursor.fetchall():
			if dbname in self.IGNORE: continue
			if dbname in self.LIVE:
				self.fetch_live.append(domain)
			else:
				self.fetch_database.append(dbname)
		self.cursor.execute('SELECT dbname, domain FROM toolserver.wiki')
		self.databases = dict(self.cursor)
 
		self.cursor.execute('SELECT dbname, ns_id, ns_name FROM toolserver.namespace')
		self.namespaces = dict((((i[0], i[1]), i[2].decode('utf-8')) for i in self.cursor))
 
	def get_usage(self, image):
		for database in self.fetch_database:
			for link in self.get_usage_db(database, image):
				yield self.databases[database], link
		for domain in self.fetch_live:
			for link in self.get_usage_live(domain, image):
				yield domain, link
 
	def get_usage_db(self, database, image):
		image = strip_image(image)
		query = """SELECT page_namespace, page_title FROM %s.page, %s.imagelinks
	LEFT JOIN %s.image ON (il_to = img_name) WHERE img_name IS NULL AND
	page_id = il_from AND il_to = %%s"""
		self.cursor.execute(query % (database, database, database), 
			(image.encode('utf-8', 'ignore'), ))
		for item in self.cursor:
			stripped_title = item[1].decode('utf-8', 'ignore')
			if item[0] != 0:
				title = self.namespaces[(database, item[0])] + u':' + stripped_title
			else:
				title = stripped_title
			yield item[0], stripped_title, title
 
	def get_usage_live(self, domain, image):
		image = strip_image(image)
		res = self.conn.query_api('api', domain, action = 'query', list = 'imageusage', 
			prop = 'info', iulimit = '500', titles = 'Image:' + image)
		if '-1' in res['query']['pages'] or domain == self.COMMONS:
			for usage in res['query'].get('imageusage', ()):
				title = usage['title'].replace(' ', '_')
				namespace = usage['ns']
				if namespace != 0:
					stripped_title = strip_ns(title)
				else:
					stripped_title = title
				yield namespace, stripped_title, title
 
	def get_usage_multi(self, images):
		res = {}
		for image in images:
			res[image] = self.get_usage(image)
		return res
 
	def get_replag(self, db):
		query = """SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp)
	FROM %s.recentchanges ORDER BY rc_timestamp DESC LIMIT 1"""
		if self.cursor.execute(query) != 1: raise RuntimeError
		return self.cursor.fetchone()[0]