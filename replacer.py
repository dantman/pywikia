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

from delinker import wait_callback, output, connect_database

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

class Replacer(object):
	def __init__(self):
		self.config = config.CommonsDelinker
		self.config.update(getattr(config, 'Replacer', ()))
		self.template = re.compile(r'\{\{%s\|([^|]*?)\|([^|]*?)(?:(?:\|reason\=(.*?))?)\}\}' % \
				self.config['template'])
		self.site = wikipedia.getSite()
		
		self.database = connect_database()
		self.cursor = self.database.cursor()
		
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
			
		revisions.sort(key = lambda rev: rev[0])
		replacements = self.template.finditer(text)
		
		for replacement in replacements:
			res = self.examine_revision_history(
				revisions, replacement,
				config.sysopnames['commons']['commons'])
			if res:
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
				return (db_timestamp(timestamp), 
					strip_image(replacement.group(1)),
					strip_image(replacement.group(2)),
					user, replacement.group(3))
					
		output('Warning! Could not find out who did %s' % \
				repr(replacement.group(0)), False)
		return
			
	def start(self):
		while True:
			self.read_replace_log()
			# Replacer should not loop as often as delinker
			time.sleep(self.config['timeout'] * 2)

if __name__ == '__main__':
	import sys, cgitb
	try:
		# FIXME: Add support for single-process replacer.
		r = Replacer()
		r.start()
	except StandardError, e:
		if type(e) not in (SystemExit, KeyboardInterrupt):
			output('A critical error has occured! Aborting!')
			print >>sys.stderr, cgitb.text(sys.exc_info())
	except:
		pass
	wikipedia.stopme()