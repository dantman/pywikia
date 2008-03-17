import sys
sys.path.append('..')

import wikipedia, config
from wikipedia import output

import simplejson

def check_namespaces(site):
    if not site.apipath():
        output(u'Warning! %s has no apipath() defined!' % site)
        return
    predata = { 'action': 'query',
                'meta': 'siteinfo',
                'siprop': 'namespaces',
                'format': 'json'}
    try:
        response, json = site.postForm(site.apipath(), predata)
    except wikipedia.ServerError, e:
        output(u'Warning! %s: %s' % (site, e))
        return
    try:
        data = simplejson.loads(json)
    except ValueError:
        output(u'Warning! %s is defined but does not exist!' % site)
        return

    result = []
    for namespace in data['query']['namespaces'].itervalues():
        try:
            defined_namespace = site.namespace(namespace['id'])
        except KeyError:
            output(u'Warning! %s has no _default for namespace %s' % \
                (site, namespace['id']))
            defined_namespace = None

        if defined_namespace != namespace['*'] and namespace['*']:
            result.append((namespace['id'], namespace['*'], defined_namespace))
    return result

def check_family(family):
    output(u'Checking namespaces for %s' % family.name)
    result = {}
    for lang in family.langs:
        if not family.obsolete.has_key(lang):
            site = wikipedia.getSite(lang, family)
            output(u'Checking %s' % site)
            namespaces = check_namespaces(site)
            if namespaces: 
                for id, name, defined_namespace in namespaces:
                    output(u'Namespace %s for %s is %s, %s is defined in family file.' % \
                        (id, site, name, defined_namespace))
                result[lang] = namespaces
    return result

if __name__ == '__main__':
    try:
        wikipedia.handleArgs()
        family = wikipedia.Family(wikipedia.default_family)
        result = check_family(family)
        output(u'Writing raw Python dictionary to stdout.')
        output(u'Format is: (namespace_id, namespace_name, predefined_namespace)')
        print result
    finally:
        wikipedia.stopme()
