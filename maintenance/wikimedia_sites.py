# This script checks the language list of each Wikimedia multiple-language site
# against the language lists

import sys, re

sys.path.append('..')
import wikipedia

families = ['wikipedia', 'wiktionary', 'wikiquote', 'wikisource', 'wikibooks', 'wikinews']
familiesDict = {
    'wikipedia':  'wikipedias_wiki.php',
    'wiktionary': 'wiktionaries_wiki.php',
    'wikiquote':  'wikiquotes_wiki.php',
    'wikisource': 'wikisources_wiki.php',
    'wikibooks':  'wikibooks_wiki.php',
    'wikinews':   'wikinews_wiki.php',
}
exceptions = ['www']

for family in families:
    print 'Checking family %s:' % family

    original = wikipedia.Family(family).languages_by_size
    obsolete = wikipedia.Family(family).obsolete

    url = 'http://s23.org/wikistats/%s' % familiesDict[family]
    uo = wikipedia.MyURLopener()
    f = uo.open(url)
    text = f.read()

    if family == 'wikipedia':
        p = re.compile(r'\[\[:([a-z\-]{2,}):\|\1\]\]')
    else:
        p = re.compile(r'\[http://([a-z\-]{2,}).%s.org/wiki/ \1]' % family)

    new = []
    for lang in p.findall(text):
        if lang in obsolete or lang in exceptions:
            # Ignore this language
            continue
        new.append(lang)

    if original == new:
        print 'The lists match!'
    else:
        print "The lists don't match, the new list is:"
        print '        self.languages_by_size = ['
        line = '            '
        index = 0
        for lang in new:
            index += 1
            if index > 1:
                line += u' '
            line += u"'%s'," % lang
            if index == 10:
                print line
                line = '            '
                index = 0
        if index > 0:
            print line
        print '        ]'
