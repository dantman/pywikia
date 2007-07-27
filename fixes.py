# -*- coding: utf-8  -*-
""" File containing all standard fixes """
__version__ = '$Id$'
fixes = {
    # These replacements will convert HTML to wiki syntax where possible, and
    # make remaining tags XHTML compliant.
    'HTML': {
        'regex': True,
        # We don't want to mess up pages which discuss HTML tags, so we skip
        # all pages which contain nowiki tags.
        'exceptions':  ['<nowiki>'],
        'msg': {
               'en':u'Robot: converting/fixing HTML',
               'de':u'Bot: konvertiere/korrigiere HTML',
               'fr':u'Robot: convertit/fixe HTML',
               'he':u'רובוט: ממיר/מתקן HTML',
               'ia':u'Robot: conversion/reparation de HTML',
               'lt':u'robotas: konvertuojamas/taisomas HTML',
               'nl':u'Bot: conversie/reparatie HTML',
               'pl':u'Robot konwertuje/naprawia HTML',
               'pt':u'Bot: Corrigindo HTML',
               'sr':u'Бот: Поправка HTML-а'
              },
        'replacements': [
            # Everything case-insensitive (?i)
            # Keep in mind that MediaWiki automatically converts <br> to <br />
            # when rendering pages, so you might comment the next two lines out
            # to save some time/edits.
            #r'(?i)<br>':                      r'<br />',
            # linebreak with attributes
            #r'(?i)<br ([^>/]+?)>':            r'<br \1 />',
            (r'(?i)<b>(.*?)</b>',              r"'''\1'''"),
            (r'(?i)<strong>(.*?)</strong>',    r"'''\1'''"),
            (r'(?i)<i>(.*?)</i>',              r"''\1''"),
            (r'(?i)<em>(.*?)</em>',            r"''\1''"),
            # horizontal line without attributes in a single line
            (r'(?i)([\r\n])<hr[ /]*>([\r\n])', r'\1----\2'),
            # horizontal line without attributes with more text in the same line
            (r'(?i) +<hr[ /]*> +',             r'\r\n----\r\n'),
            # horizontal line with attributes; can't be done with wiki syntax
            # so we only make it XHTML compliant
            (r'(?i)<hr ([^>/]+?)>',            r'<hr \1 />'),
            # a header where only spaces are in the same line
            (r'(?i)([\r\n]) *<h1> *([^<]+?) *</h1> *([\r\n])',  r"\1= \2 =\3"),
            (r'(?i)([\r\n]) *<h2> *([^<]+?) *</h2> *([\r\n])',  r"\1== \2 ==\3"),
            (r'(?i)([\r\n]) *<h3> *([^<]+?) *</h3> *([\r\n])',  r"\1=== \2 ===\3"),
            (r'(?i)([\r\n]) *<h4> *([^<]+?) *</h4> *([\r\n])',  r"\1==== \2 ====\3"),
            (r'(?i)([\r\n]) *<h5> *([^<]+?) *</h5> *([\r\n])',  r"\1===== \2 =====\3"),
            (r'(?i)([\r\n]) *<h6> *([^<]+?) *</h6> *([\r\n])',  r"\1====== \2 ======\3"),
            # TODO: maybe we can make the bot replace <p> tags with \r\n's.
        ]
    },
    # Grammar fixes for German language
    'grammar-de': {
        'regex': True,
        'exceptions':  ['sic!'],
        'msg': {
               'de':u'Bot: korrigiere Grammatik',
              },
        'replacements': [
            #(u'([Ss]owohl) ([^,\.]+?), als auch',                                                            r'\1 \2 als auch'),
            #(u'([Ww]eder) ([^,\.]+?), noch', r'\1 \2 noch'),
            # 
            # Vorsicht bei Substantiven, z. B. 3-Jähriger!
            (u'(\d+)(minütig|stündig|tägig|wöchig|jährig|minütlich|stündlich|täglich|wöchentlich|jährlich|fach|mal|malig|köpfig|teilig|gliedrig|geteilt|elementig|dimensional|bändig|eckig|farbig|stimmig)', r'\1-\2'),
            # zusammengesetztes Wort, Bindestrich wird durchgeschleift
            (u'(?<!\w)(\d+|\d+[\.,]\d+)(\$|€|DM|£|¥|mg|g|kg|ml|cl|l|t|ms|min|µm|mm|cm|dm|m|km|°C|kB|MB|TB|W|kW|MW|PS|Nm|eV|J|kcal|mA|mV|kV|Ω|Hz|kHz|MHz|GHz|mol|Pa|Bq|Sv|mSv)([²³]?-[\w\[])',           r'\1-\2\3'),
            # Größenangabe ohne Leerzeichen vor Einheit
            # weggelassen wegen vieler falsch Positiver: s, A, V, C, S, %
            (u'(?<!\w)(\d+|\d+[\.,]\d+)(\$|€|DM|£|¥|mg|g|kg|ml|cl|l|t|ms|min|µm|mm|cm|dm|m|km|°C|kB|MB|TB|W|kW|MW|PS|Nm|eV|J|kcal|mA|mV|kV|Ω|Hz|kHz|MHz|GHz|mol|Pa|Bq|Sv|mSv)(?=\W|²|³|$)',          r'\1 \2'),
            # Kein Leerzeichen zwischen Tag und Monat
            (u'(\d+)\.(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', r'\1. \2'),
            # Keine führende Null beim Datum
            #(u'0(\d+)\. (Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', r'\1. \2'),
            # Kein Leerzeichen nach Komma
            (u'([a-z](\]\])?,)((\[\[)?[a-zA-Z])',                                                                          r'\1 \3'),
            # Leerzeichen und Komma vertauscht
            (u'([a-z](\]\])?) ,((\[\[)?[a-zA-Z])',                                                                          r'\1, \3'),
            #(u'([a-z]\.)([A-Z])',                                                                             r'\1 \2'),
        ]
    },
    # Do NOT run this automatically!
    # Recommendation: First run syntax2 automatically, afterwards
    # run syntax manually, carefully checking that you're not breaking
    # anything.
    'syntax': {
        'regex': True,
        'msg': {
               'de':u'Bot: Korrigiere Wiki-Syntax',
               'en':u'Bot: Fixing wiki syntax',
               'fr':u'Bot: Corrige wiki-syntaxe',
               'he':u'בוט: מתקן תחביר ויקי',
               'ia':u'Robot: Reparation de syntaxe wiki',
               'lt':u'robotas: Taisoma wiki sintaksė',
               'nl':u'Bot: reparatie wikisyntaxis',
               'pl':u'Robot poprawia wiki-składnię',
               'pt':u'Bot: Corrigindo sintaxe wiki',
               'sr':u'Бот: Поправка вики синтаксе',
              },
        'replacements': [
            # external link in double brackets
            (r'\[\[(?P<url>http://[^\]]+?)\]\]',   r'[\g<url>]'),
            # external link starting with double bracket
            (r'\[\[(?P<url>http://.+?)\]',   r'[\g<url>]'),
            # external link ending with double bracket.
            # do not change weblinks that contain wiki links inside
            # inside the description
            (r'\[(?P<url>http://[^\[\]]+?)\]\](?!\])',   r'[\g<url>]'),
            # external link and description separated by a dash.
            # ATTENTION: while this is a mistake in most cases, there are some
            # valid URLs that contain dashes!
            (r'\[(?P<url>http://[^\|\]\s]+?) *\| *(?P<label>[^\|\]]+?)\]', r'[\g<url> \g<label>]'),
            # wiki link closed by single bracket.
            # ATTENTION: There are some false positives, for example
            # Brainfuck code examples or MS-DOS parameter instructions.
            # There are also sometimes better ways to fix it than
            # just putting an additional ] after the link.
            # wiki link opened by single bracket.
            # ATTENTION: same as above.
            (r'\[\[([^\[\]]+?)\](?!\])',  r'[[\1]]'),
            (r'(?<!\[)\[([^\[\]]+?)\]\](?!\])',  r'[[\1]]'),
            # template closed by single bracket
            # ATTENTION: There are some false positives, especially in
            # mathematical context or program code.
            (r'{{([^{}]+?)}(?!})',       r'{{\1}}'),
        ],
        'exceptions': [
            r'http://.*?object=tx\|',               # regular dash in URL
            r'http://.*?allmusic\.com',             # regular dash in URL
            r'http://.*?allmovie\.com',             # regular dash in URL
            r'http://physics.nist.gov/',            # regular dash in URL
            r'http://www.forum-seniorenarbeit.de/', # regular dash in URL
            r'&object=med',                         # regular dash in URL
            r'\[CDATA\['                            # lots of brackets
        ]
    },
    # The same as syntax, but restricted to replacements that should
    # be safe to run automatically.
    'syntax-safe': {
        'regex': True,
        'msg': {
               'de':u'Bot: Korrigiere Wiki-Syntax',
               'en':u'Bot: Fixing wiki syntax',
               'fr':u'Bot: Corrige wiki-syntaxe',
               'he':u'בוט: מתקן תחביר ויקי',
               'ia':u'Robot: Reparation de syntaxe wiki',
               'lt':u'robotas: Taisoma wiki sintaksė',
               'pl':u'Robot poprawia wiki-składnię',
               'pt':u'Bot: Corrigindo sintaxe wiki',
               'sr':u'Бот: Поправка вики синтаксе',
              },
        'replacements': [
            # external link in double brackets
            (r'\[\[(?P<url>http://[^\]]+?)\]\]',   r'[\g<url>]'),
            # external link starting with double bracket
            (r'\[\[(?P<url>http://.+?)\]',   r'[\g<url>]'),
            # external link with forgotten closing bracket
            (r'\[(?P<url>http://[^\]\s]+)\r\n',   r'[\g<url>]\r\n'),
             # external link and description separated by a dash, with
             # whitespace in front of the dash, so that it is clear that
             # the dash is not a legitimate part of the URL.
            (r'\[(?P<url>http://[^\|\]\r\n]+?) +\| *(?P<label>[^\|\]]+?)\]', r'[\g<url> \g<label>]'),
            # dash in external link, where the correct end of the URL can
            # be detected from the file extension. It is very unlikely that
            # this will cause mistakes.
            (r'\[(?P<url>http://[^\|\] ]+?(\.pdf|\.html|\.htm|\.php|\.asp|\.aspx)) *\| *(?P<label>[^\|\]]+?)\]', r'[\g<url> \g<label>]'),
        ],
    },
    'case-de': { # German upper / lower case issues
        'regex': True,
        'msg': {
               'de':u'Bot: Korrigiere Groß-/Kleinschreibung',
              },
        'replacements': [
            (r'\batlantische(r|n|) Ozean', r'Atlantische\1 Ozean'),
            (r'\bdeutsche(r|n|) Bundestag\b', r'Deutsche\1 Bundestag'),
            (r'\bdeutschen Bundestags\b', r'Deutschen Bundestags'), # Aufpassen, z. B. 'deutsche Bundestagswahl'
            (r'\bdeutsche(r|n|) Reich\b', r'Deutsche\1 Reich'),
            (r'\bdeutschen Reichs\b', r'Deutschen Reichs'), # Aufpassen, z. B. 'deutsche Reichsgrenzen'
            (r'\bdritte(n|) Welt(?!krieg)', r'Dritte\1 Welt'),
            (r'\bdreißigjährige(r|n|) Krieg', r'Dreißigjährige\1 Krieg'),
            (r'\beuropäische(n|) Gemeinschaft', r'Europäische\1 Gemeinschaft'),
            (r'\beuropäische(n|) Kommission', r'Europäische\1 Kommission'),
            (r'\beuropäische(n|) Parlament', r'Europäische\1 Parlament'),
            (r'\beuropäische(n|) Union', r'Europäische\1 Union'),
            (r'\berste(r|n|) Weltkrieg', r'Erste\1 Weltkrieg'),
            (r'\bkalter(r|n|) Krieg', r'Kalte\1 Krieg'),
            (r'\bpazifische(r|n|) Ozean', r'Pazifische\1 Ozean'),
            (r'Tag der deutschen Einheit', r'Tag der Deutschen Einheit'),
            (r'\bzweite(r|n|) Weltkrieg', r'Zweite\1 Weltkrieg'),
        ],
        'exceptions':  ['sic!'],
    },
    'vonbis': {
        'regex': True,
        'msg': {
            'de':u'Bot: Ersetze Binde-/Gedankenstrich durch "bis"',
        },
        'replacements': [
            # Bindestrich, Gedankenstrich, Geviertstrich
            (u'(von \d{3,4}) *(-|&ndash;|–|&mdash;|—) *(\d{3,4})', r'\1 bis \3'),
        ],
    },
    # some disambiguation stuff for de:
    # python replace.py -fix:music -subcat:Album
    'music': {
        'regex': False,
        'msg': {
            'de':u'Bot: korrigiere Links auf Begriffsklärungen',
        },
        'replacements': [
            (u'[[CD]]', u'[[Audio-CD|CD]]'),
            (u'[[LP]]', u'[[Langspielplatte|LP]]'),
            (u'[[EP]]', u'[[Extended Play|EP]]'),
            (u'[[MC]]', u'[[Musikkassette|MC]]'),
            (u'[[Single]]', u'[[Single (Musik)|Single]]'),
        ]
    },
    # format of dates of birth and death, for de:
    # python replace.py -fix:datum -ref:Vorlage:Personendaten
    'datum': {
        'regex': True,
        'msg': {
            'de': u'Bot: Korrigiere Datumsformat',
        },
        'replacements': [
            # space after birth sign w/ year
            #(u'\(\*(\d{3,4})', u'(* \\1'),
            ## space after death sign w/ year
            #(u'†(\d{3,4})', u'† \\1'),
            #(u'&dagger;(\d{3,4})', u'† \\1'),
            ## space after birth sign w/ linked date
            #(u'\(\*\[\[(\d)', u'(* [[\\1'),
            ## space after death sign w/ linked date
            #(u'†\[\[(\d)', u'† [[\\1'),
            #(u'&dagger;\[\[(\d)', u'† [[\\1'),
            (u'\[\[(\d+\. (?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)) (\d{1,4})\]\]', u'[[\\1]] [[\\2]]'),
        ],
        'exceptions': [
            u'[[20. Juli 1944]]',
            u'[[17. Juni 1953]]',
            u'[[11. September 2001]]',
        ]
        
    },
}
