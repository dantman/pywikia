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

    languages_by_size = wikipedia.Family(family).languages_by_size
    obsolete = wikipedia.Family(family).obsolete

    url = 'http://s23.org/wikistats/%s' % familiesDict[family]
    uo = wikipedia.MyURLopener()
    f = uo.open(url)
    text = f.read()

    if family == 'wikipedia':
        p = re.compile(r'\[\[:([a-z\-]{2,}):\|\1\]\]')
    else:
        p = re.compile(r'\[http://([a-z\-]{2,}).%s.org/wiki/ \1]' % family)

    index = 0
    for lang in p.findall(text):
        if lang in obsolete or lang in exceptions:
            # Ignore this language
            continue
        if index >= len(languages_by_size):
            print 'Unmatched languages: site - %s, family file ended' % lang
            break
        if lang == languages_by_size[index]:
            # Matched languages
            index += 1
        else:
            # Unmatched languages
            print 'Unmatched languages: site - %s, family file - %s' % (lang, languages_by_size[index])
            if lang in languages_by_size and index < languages_by_size.index(lang):
                # Try to increment the index until it reaches the current language
                index += 1
                while index < len(languages_by_size) and languages_by_size[index] != lang and lang in languages_by_size and index < languages_by_size.index(lang):
                    print 'Unmatched languages: site - %s, family file - %s' % (lang, languages_by_size[index])
                    index += 1
                # Now increment the index again for the next iteration
                index += 1
    if index < len(languages_by_size):
        # Special-case exception
        if family != 'wikinews' or languages_by_size[index] != 'ta':
            print 'Unmatched languages: site ended, family file - %s' % languages_by_size[index]
