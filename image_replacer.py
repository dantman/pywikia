#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Please refer to delinker.txt for full documentation.
"""
#
# 
# (C) Bryan Tong Minh, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
import config, wikipedia
import re, time
import threadpool

from delinker import wait_callback, output, connect_database
from checkusage import family

def mw_timestamp(ts):
	return '%s%s%s%s-%s%s-%s%sT%s%s:%s%s:%s%sZ' % tuple(ts)
DB_TS = re.compile('[^0-9]')
def db_timestamp(ts):
	return DB_TS.sub('', ts)
IMG_NS = re.compile(r'(?i)^\s*Image\:')
def strip_image(img):
	img = IMG_NS.sub('', img)
	img = img.replace(' ', '_')
	img = img[0].upper() + img[1:]
	return img.strip()

def site_prefix(site):
	if site.lang == site.family.name:
		return site.lang
	if (site.lang, site.family.name) == ('-', 'wikisource'):
		return 'oldwikisource'
	return '%s:%s' % (site.family.name, site.lang)

class Replacer(object):
	def __init__(self):
		self.config = config.CommonsDelinker
		self.config.update(getattr(config, 'Replacer', ()))
		self.template = re.compile(r'\{\{%s\|([^|]*?)\|([^|]*?)(?:(?:\|reason\=(.*?))?)\}\}' % \
				self.config['replace_template'])
		self.disallowed_replacements = [(re.compile(i[0]), re.compile(i[1])) 
			for i in self.config.get('disallowed_replacements', ())]
				
		self.site = wikipedia.getSite()
		
		self.database = connect_database()
		self.cursor = self.database.cursor()
		
		self.first_revision = 0
		if self.config.get('replacer_report_replacements', False):
			self.reporters = threadpool.ThreadPool(Reporter)
			self.reporters.add_thread(self.site, self.config)
			self.reporters.start()
			
		
	def read_replace_log(self):
		# FIXME: Make sqlite3 compatible
		insert = """INSERT INTO %s (timestamp, old_image, new_image, 
			status, user, comment) VALUES (%%s, %%s, %%s,
			'pending', %%s, %%s)""" % self.config['replacer_table']
		
		page = wikipedia.Page(self.site, self.config['command_page'])
		
		# Get last revision date
		if self.cursor.execute("""SELECT timestamp FROM %s 
				ORDER BY timestamp DESC LIMIT 1""" % \
				self.config['replacer_table']):
			since = mw_timestamp(self.cursor.fetchone()[0])
		else:
			since = None
			
		try:
			revisions = page.fullVersionHistory(max = 500, since = since)
			# Fetch the page any way, to prevent editconflicts
			old_text = text = page.get()
		except StandardError, e:
			# Network error, not critical
			output(u'Warning! Unable to read replacement log.', False)
			output('%s: %s' % (e.__class__.__name__, str(e)), False)
			return time.sleep(self.config['timeout'])
		
		if text.lower().find('{{stop}}') != -1:
			output(u'Found {{stop}} on command page. Not replacing anything.')
			return time.sleep(self.config['timeout'])
		
		revisions.sort(key = lambda rev: rev[0])
		replacements = self.template.finditer(text)
		
		if self.config.get('clean_list', False):
			username = config.sysopnames[self.site.family.name][self.site.lang]
		else:
			username = None
		
		for replacement in replacements:
			res = self.examine_revision_history(
				revisions, replacement, username)
			if res and self.allowed_replacement(replacement) and \
					replacement.group(1) != replacement.group(2):
				self.cursor.execute(insert, res)
				text = text.replace(replacement.group(0), '')
				output('Replacing %s by %s: %s' % replacement.groups())
		self.database.commit()
		
		if text != old_text and self.config.get('clean_list', False):
			page.put(text.strip(), comment = 'Removing images being processed')
		
	def examine_revision_history(self, revisions, replacement, username):
		if replacement.group(0) in revisions[0][2]:
			return (db_timestamp(revisions[0][0]),
				strip_image(replacement.group(1)),
				strip_image(replacement.group(2)),
				'<Unknown>', replacement.group(3))
				
		for timestamp, user, text in revisions[1:]:
			if replacement.group(0) in text and user != username:
				db_time = db_timestamp(timestamp)
				if db_time < self.first_revision or not self.first_revision:
					self.first_revision = int(db_time)
				return (db_time, strip_image(replacement.group(1)),
					strip_image(replacement.group(2)),
					user, replacement.group(3))
					
		output('Warning! Could not find out who did %s' % \
				repr(replacement.group(0)), False)
		return
		
	def read_finished_replacements(self):
		self.cursor.execute('START TRANSACTION WITH CONSISTENT SNAPSHOT')
		self.cursor.execute("""SELECT old_image, new_image, user, comment FROM
			%s WHERE status = 'done' AND timestamp >= %i""" % \
			(self.config['replacer_table'], self.first_revision))
		finished_images = list(self.cursor)
		self.cursor.execute("""UPDATE %s SET status = 'reported' 
			WHERE status = 'done' AND timestamp >= %i""" % \
			(self.config['replacer_table'], self.first_revision))
		self.cursor.commit()
		
		for old_image, new_image, user, comment in finished_images:
			self.cursor.execute("""SELECT wiki, namespace, page_title 
				FROM %s WHERE img = %%s AND status <> 'ok'""" % 
				self.config['log_table'], (old_image, ))
			not_ok = [(wiki, namespace, page_title.decode('utf-8', 'ignore'))
				for wiki, namespace, page_title in self.cursor]
			
			self.reporters.append((old_image.decode('utf-8', 'ignore'),
				new_image.decode('utf-8', 'ignore'), 
				user.decode('utf-8', 'ignore'), 
				comment.decode('utf-8', 'ignore'), not_ok))
		
			
	def start(self):
		while True:
			self.read_replace_log()
			if self.config.get('replacer_report_replacements', False):
				self.read_finished_replacements()
			
			# Replacer should not loop as often as delinker
			time.sleep(self.config['timeout'] * 2)
			
	def allowed_replacement(self, replacement):
		for source, target in self.disallowed_replacements:
			if source.search(replacement.group(1)) and \
					target.search(replacement.group(2)):
				return False
		return True

class Reporter(threadpool.Thread):
	def __init__(self, pool, site, config):
		self.site = site
		self.config = config
		
		threadpool.Thread.__init__(self, pool)
	def do(self, (old_image, new_image, user, comment, not_ok)):
		not_ok_items = []
		for wiki, namespace, page_title in not_ok:
			site = family(wiki)
			if unicode(site) == unicode(self.site):
				title = u'%s:%s' % (site.namespace(namespace), page_title)
			else:
				title = u'%s:%s:%s' % (site_prefix(site),
					site.namespace(namespace), page_title)
			not_ok_items.append(title)
		
		template = u'{{%s|new_image=%s|user=%s|comment=%s|not_ok=%s}}' % \
			(self.config['replacer_report_template'],
			new_image, user, comment, 
			self.config.get('replacer_report_seperator', u', ').join(not_ok))
		page = wikipedia.Page(self.site, u'Image:' + old_image)
		text = page.get()
		
		try:
			page.put(u'%s\n%s' % (template, text), 
				comment = u'This image has been replaced by ' + new_image)
		except PageNotSaved, e:
			output(u'Warning! Unable to report replacement to %s.' % old_image, False)
			output('%s: %s' % (e.__class__.__name__, str(e)), False)
		else:
			output(u'Reporting replacement of %s by %s.' % \
				(old_image, new_image))
			

if __name__ == '__main__':
	import sys, cgitb
	output(u'Running ' + __version__)

	try:
		# FIXME: Add support for single-process replacer.
		r = Replacer()
		output(u'This bot runs from: ' + str(r.site))
		r.start()
	except Exception, e:
		if type(e) not in (SystemExit, KeyboardInterrupt):
			output('A critical error has occured! Aborting!')
			print >>sys.stderr, cgitb.text(sys.exc_info())
	wikipedia.stopme()