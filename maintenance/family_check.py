import sys
sys.path.append('..')

import wikipedia, config
from wikipedia import output

import simplejson

def check_namespaces(site):
	predata = {'action': 'query',
		'meta': 'siteinfo',
		'siprop': 'namespaces',
		'format': 'json'}
	response, json = site.postForm(site.apipath(), predata)
	if '<h1 class="firstHeading">Wiki does not exist</h1>' in json:
		output(u'Warning! %s is defined but does not exist!' % site)
		return
	
	data = simplejson.loads(json)
	result = []
	for namespace in data['query']['namespaces'].itervalues():
		try:
			defined_namespace = site.namespace(namespace['id'])
		except KeyError:
			output(u'Warning! %s has no _default for namespace %s' % \
				(site, namespace['id']))
			defined_namespace = None
		
		if defined_namespace != namespace['*'] and namespace['*']:
			result.append((namespace['id'], namespace['*']))
	return result
			
def check_family(family):
	output(u'Checking namespaces for %s' % family.name)
	result = {}
	for lang in family.langs:
		site = wikipedia.getSite(lang, family)
		output(u'Checking %s' % site)
		namespaces = check_namespaces(site)
		if namespaces: 
			for id, name in namespaces:
				output(u'Namespace %s for %s is %s, %s is defined in family file.' % \
					(id, site, name, site.namespace(id)))
			result[lang] = namespaces
	return result
	
if __name__ == '__main__':
	wikipedia.handleArgs()
	family = wikipedia.Family(wikipedia.default_family)
	result = check_family(family)
	output(u'Writing raw Python dictionary to stdout.')
	print result