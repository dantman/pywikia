# -*- coding: utf-8  -*-

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
               'he':u'רובוט: ממיר/מתקן HTML',
               'ia':u'Robot: conversion/reparation de HTML',
               'lt':u'robotas: konvertuojamas/taisomas HTML',
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
            (u'(\d+)(minütig|stündig|tägig|wöchig|jährig|minütlich|stündlich|täglich|wöchentlich|jährlich|fach|mal|malig|köpfig|teilig|gliedrig|geteilt|elementig|dimensional|bändig|eckig|farbig|stimmig)', r'\1-\2'),
            # zusammengesetztes Wort, Bindestrich wird durchgeschleift
            (u'(\d+|\d+[\.,]\d+)(\$|€|DM|£|¥|mg|g|kg|ml|cl|l|t|ms|min|µm|mm|cm|dm|m|km|°C|kB|MB|TB|W|kW|MW|PS|Nm|eV|J|kcal|mA|mV|kV|Ω|Hz|kHz|MHz|GHz|mol|Pa|Bq|Sv|mSv)([²³]?-[\w\[])',           r'\1-\2\3'),
            (u'(\d+|\d+[\.,]\d+)(\$|€|DM|£|¥|mg|g|kg|ml|cl|l|t|ms|min|µm|mm|cm|dm|m|km|°C|kB|MB|TB|W|kW|MW|PS|Nm|eV|J|kcal|mA|mV|kV|Ω|Hz|kHz|MHz|GHz|mol|Pa|Bq|Sv|mSv)(?=\W|²|³|$)',          r'\1 \2'),
            # weggelassen wegen vieler falsch Positiver: s, A, V, C, S, %
            # Kein Leerzeichen zwischen Tag und Monat
            (u'(\d+)\.(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', r'\1. \2'),
            # Keine führende Null beim Datum
            (u'0(\d+)\. (Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', r'\1. \2'),
            # Kein Leerzeichen nach Komma
            (u'([a-z](\]\])?,)((\[\[)?[a-zA-Z])',                                                                          r'\1 \3'),
            # Leerzeichen und Komma vertauscht
            (u'([a-z](\]\])?) ,((\[\[)?[a-zA-Z])',                                                                          r'\1, \3'),
            #(u'([a-z]\.)([A-Z])',                                                                             r'\1 \2'),
        ]
    },
    'syntax': {
        'regex': True,
        'msg': {
               'de':u'Bot: Korrigiere Wiki-Syntax',
               'en':u'Bot: Fixing wiki syntax',
               'he':u'בוט: מתקן תחביר ויקי',
               'ia':u'Robot: Reparation de syntaxe wiki',
               'lt':u'robotas: Taisoma wiki sintaksė',
               'pt':u'Bot: Corrigindo sintax wiki',
               'sr':u'Бот: Поправка вики синтаксе',
              },
        'replacements': [
            (r'\[\[(http://.+?)\]\]',   r'[\1]'),        # external link in double brackets
            (r'\[\[(http://.+?)\]',   r'[\1]'),          # external starting with double bracket
            (r'\[(http://[^\|\] ]+?)\s*\|\s*([^\|\]]+?)\]', r'[\1 \2]'), # external link and description separated by a dash.
            # Attention: while this is a mistake in most cases, there are some valid URLs that contain dashes.
            (r'\[\[([^\[\]]+?)\](?!\])',  r'[[\1]]'),    # wiki link closed by single bracket
            (r'{{([^}]+?)}(?!})',       r'{{\1}}'),      # template closed by single bracket
        ],
        'exceptions': [
            r'http://.*?object=tx\|', # regular dash in URL
        ]
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
            (r'\bdritte(n|) Welt', r'Dritte\1 Welt'),
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
    # python replace.py -fix:music -ref:Vorlage:Musikalbum
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
    # Add tag Wiktionary Interproject
    # By de:Benutzer:Melancholie - http://de.wikipedia.org/w/index.php?title=Benutzer:MelancholieBot/Skripte&oldid=10856865
    # python replace.py -fix:interproject -ref:Template:Wiktionary
    'interproject':{
        'regex': True,
        'exceptions': ['\{\{(W|w)iktionary'],
        'msg': {
            'de':u'InterProjekt: +wikt',
            'pt':u'Interprojetos: +wikcionário',
            },
        'replacements': [
            (r'(?i)([\r\n]+?)\*?:?;? *?(Siehe ?:|\'\'Siehe\'\' ?:|\'\'Siehe ?: ?\'\'|\'\'\'Siehe\'\'\' ?:|\'\'\'Siehe ?: ?\'\'\'|Siehe auch ?:|\'\'Siehe auch\'\' ?:|\'\'Siehe auch ?: ?\'\'|\'\'\'Siehe auch\'\'\' ?:|\'\'\'Siehe auch ?: ?\'\'\')(.*?)([\r\n]+?)(=+? *?Literatur|=+? *?Weblinks|\[\[Kat)',  r"\1== Siehe auch ==\r\n\3\4\5"),
            (r'(?i)([\r\n]+?) *?=+? *?Siehe *?auch *?=+?([^\r\n=]*?)([\r\n]+?) *?([A-ZÄÖÜa-zäöü\[]+?)',  r"\1== Siehe auch ==\2\3* \4"),
            (r'(ommons|ikibooks|ikiquote|iktionary)1\|(.*?)\|\2\}',  r"\11|\2}"),
            (r'(ommons|ikibooks|ikiquote|iktionary)1\|(.*?)\|([^\2]+?)\}',  r"\12|\2|\3}"),
            (r'(?i)([\r\n]+?)\**?:*?;*? *?\{\{(Commons|Wikibooks|Wikiquote|Wikinews|Wikipedia|Wikisource|Wikispecies|Wiktionary)',  r"\1{{\2"),
            (r'(?i)([\r\n]+?)\{\{(Commons|Wikibooks|Wikiquote|Wikinews|Wikipedia|Wikisource|Wikispecies|Wiktionary)([^\{\}]+?)\}\}([^\r\n\{\}]+?)\{\{',  r"\1{{\2\3}}\4\r\n{{"),
            (r'(?i)([\r\n]+?)\{\{(Commons|Wikibooks|Wikipedia|Wikiquote|Wikinews|Wikisource|Wiktionary)(.*?)\}\}(.*?)([\r\n]+?)',  r"\1{{\2\3}}\4\r\n{{Wiktionary1|{{subst:PAGENAME}}}}"),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1<--entfWikt-->\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->\6<--entfWikt-->\7{{Wiktionary1|{{subst:PAGENAME}}}}'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1<--entfWikt-->\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->\6{{Wiktionary1|{{subst:PAGENAME}}}}'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1<--entfWikt-->\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5{{Wiktionary1|{{subst:PAGENAME}}}}'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1<--entfWikt-->\2<--entfWikt-->\3<--entfWikt-->\4{{Wiktionary1|{{subst:PAGENAME}}}}'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1<--entfWikt-->\2<--entfWikt-->\3{{Wiktionary1|{{subst:PAGENAME}}}}'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1<--entfWikt-->\2{{Wiktionary1|{{subst:PAGENAME}}}}'),
            (r'([\r\n])([^:\r\n]+?)([\r\n])\[\[([a-z]{2,3}):',  r"\1\2\r\n\n{{Wiktionary1|{{subst:PAGENAME}}}}\r\n\n[[\4:"),
            (r'([\r\n]{3,9})\[\[([a-z]{2,3}):',  r"\r\n\n{{Wiktionary1|{{subst:PAGENAME}}}}\r\n\n[[\2:"),
            (r'^((?:.*?\r\n+?)+?)(.*?)$',  r"\1\2\r\n\n{{Wiktionary1|{{subst:PAGENAME}}}}"),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->\6<--entfWikt-->\7<--entfWikt-->\8<--entfWikt-->\9<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->\6<--entfWikt-->\7<--entfWikt-->\8<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->\6<--entfWikt-->\7<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->\6<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->\5<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->\4<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->\3<--entfWikt-->'),
            (u'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([^ï¿½]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}',  r'\1{{Wiktionary1|{{subst:PAGENAME}}}}\2<--entfWikt-->'),
            (r'(?i)([\r\n]{1,2}) *?<--entfWikt--> *?',  r""),
            (r'(?i) *?<--entfWikt--> *?',  r""),
            (r'(?i)([\r\n]+?)\{\{Wiktionary1\|\{\{subst:PAGENAME\}\}\}\}([\r\n]+?)\[\[([a-z]{2,3}):',  r"\r\n\n\n{{Wiktionary1|{{subst:PAGENAME}}}}\2[[\3:"),
            (r'(?i)\{\{Wiktionary(.*?)([\r\n]+?)\{\{Wiktionary',  r"{{Wiktionary\1\r\n{{Wiktionary"),
        ]
    },
}
