import sys
sys.path.append('..')

import wikipedia
from wikipedia import output

import family_check
import re

r_namespace_section = r'(?s)self\.namespaces\[%s]\s*\=\s*\{(.*?)\}'

r_string = '[u]?[r]?[\'"].*?[\'"]'
r_list = '\\[.*?\\]'
r_namespace_def = re.compile(r'[\'"]([a-z_-]*)[\'"]\s*\:\s*((?:%s)|(?:%s))\s*,' % (r_string, r_list))
def update_family(family, changes):
    global namespace_section_text, namespace_defs, new_defs
    
    output(u'Updating family %s' % family)
    family_file = open('../families/%s_family.py' % family.name, 'r')
    old_family_text = family_text = family_file.read()
    family_file.close()
    
    for lang, namespaces in changes.iteritems():
        for namespace_id, namespace_name, predefined_namespace in namespaces:
            output(u'Setting namespace[%s] for %s to %s' % (namespace_id, lang, namespace_name))
            
            namespace_section = re.search(r_namespace_section % namespace_id, family_text)
            if not namespace_section:
                continue
            namespace_section_text = namespace_section.group(1)
            namespace_defs = dict([(match.group(1), match.group(2)) 
                for match in r_namespace_def.finditer(namespace_section_text)])
                
            if not namespace_defs.get(lang, '').startswith('['):
                output(u'Updating namespace[%s] to %s' % (namespace_id, namespace_name))
                    
                namespace_defs[lang] = escape_string(namespace_name.encode('utf-8'))
            else:
                output(u'Namespace[%s] definition is a list; not updating.' % namespace_id)
                    
            new_defs = namespace_defs.items()
            new_defs.sort(key = lambda x: x[0])
            new_text = '\n' + ''.join([12 * ' ' + "'%s': %s,\n" % i for i in new_defs]) + ' ' * 8
            family_text = family_text.replace(namespace_section.group(1), new_text)
            
    if test_data(family_text):
        output(u'Saving to family file')
        family_file = open('../families/%s_family.py' % family.name, 'w')
        family_file.write(family_text)
        family_file.close()
    else:
        output(u'Warning! Syntax error!')
        output(family_text.decode('utf-8'))
        
def escape_string(string):
    return "u'%s'" % string.replace('\\', '\\\\').replace("'", "\\'")
            
def test_data(_test_data):
    try:
        exec _test_data
    except SyntaxError:
        return False
    except:
        return True
    return True
    
if __name__ == '__main__':
    try:
        wikipedia.handleArgs()
        family = wikipedia.Family(wikipedia.default_family)
        result = family_check.check_family(family)
        update_family(family, result)
    finally:
        wikipedia.stopme()