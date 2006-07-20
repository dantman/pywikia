# -*- coding: utf-8  -*-
import codecs
import sys, re


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
               'ia':u'Robot: conversion/reparation de HTML',
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
            (u'(\d+|\d+[\.,]\d+)(\$|€|DM|mg|g|kg|l|t|ms|min|µm|mm|cm|dm|m|km|°C|kB|MB|TB|W|kW|MW|PS|Hz|kHz|MHz|GHz)(?=-\w)',           r'\1-\2'),
            (u'(\d+|\d+[\.,]\d+)(\$|€|DM|mg|g|kg|l|t|ms|min|µm|mm|cm|dm|m|km|°C|kB|MB|TB|W|kW|MW|PS|Hz|kHz|MHz|GHz)(?=\W|$)',          r'\1 \2'),
            # Kein Leerzeichen zwischen Tag und Monat
            (u'(\d+)\.(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', r'\1. \2'),
            # Keine führende Null beim Datum
            (u'0(\d+)\. (Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)', r'\1. \2'),
            # Kein Leerzeichen nach Komma
            (u'([a-z],)([a-zA-Z])',                                                                          r'\1 \2'),
            # Leerzeichen und Komma vertauscht
            (u'([a-z]) ,([a-zA-Z])',                                                                          r'\1, \2'),
            #(u'([a-z]\.)([A-Z])',                                                                             r'\1 \2'),
        ]
    },
    'syntax': {
        'regex': True,
        'msg': {
               'de':u'Bot: Korrigiere Wiki-Syntax',
               'en':u'Bot: Fixing wiki syntax',
               'ia':u'Robot: Reparation de syntaxe wiki',
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
        ]
    },
    # for de.wikipedia
    'schwesterprojekte': {
        'regex': True,
        'msg': {
               'de':u'Bot: ersetze Schwesterprojekt-Vorlagen',
              },
        'replacements': [
            (u'{{[Cc]ommons1', u'{{Commons'),
            (u'{{[Cc]ommons2', u'{{Commons'),
            (u'{{[Ww]iktionary1', u'{{Wiktionary'),
            (u'{{[Ww]iktionary2', u'{{Wiktionary'),
            (u'{{[Ww]iktionary1', u'{{Wiktionary'),
            (u'{{[Ww]iktionary2', u'{{Wiktionary'),
            (u'{{[Ww]ikibooks1', u'{{Wikibooks'),
            (u'{{[Ww]ikibooks2', u'{{Wikibooks'),
            (u'{{[Ww]ikiquote1', u'{{Wikiquote'),
            (u'{{[Ww]ikiquote2', u'{{Wikiquote'),
            (u'{{[Ww]ikisource1', u'{{Wikisource'),
            (u'{{[Ww]ikisource2', u'{{Wikisource'),
            (u'{{[Ww]ikinews1', u'{{Wikinews'),
            (u'{{[Ww]ikinews2', u'{{Wikinews'),
        ]
    },
    'flags-de': {
        'regex': True,
        'msg': {
               'de':u'Bot: ersetze Flaggen durch SVG-Versionen',
              },
        'replacements': [
            # coat of arms has wrong color.
            #(u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]afghanistan[_ ]2004.png'   ,                           u'[[Bild:Flag of Afghanistan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]gypt[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Egypt.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]lbania[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Albania.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]lgeria[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Algeria.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]ndorra[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Andorra.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]ngola[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Angola.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]quatorial[_ ]guinea[_ ]flag[_ ](medium|large|300).png',       u'[[Bild:Flag of Equatorial Guinea.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]ntigua[_ ]and[_ ]barbuda[_ ]flag[_ ](medium|large|300).png',  u'[[Bild:Flag of Antigua and Barbuda.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]rgentina[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Argentina.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]rmenia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Armenia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]zerbaijan[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Azerbaijan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Ethiopia.png',                                   u'[[Bild:Flag of Ethiopia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]thiopia[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Ethiopia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]ustralia[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Australia.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]ahamas[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of the Bahamas.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]ahrain[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Bahrain.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]angladesh[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Bangladesh.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]arbados[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Barbados.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]elgium[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Belgium.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Belgium.png',                                    u'[[Bild:Flag of Belgium.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]elize[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Belize.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]enin[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Benin.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]hutan[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Bhutan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]olivia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Bolivia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]osnia[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Bosnia and Herzegovina.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Bosnia[_ ]Herzegowina.png',                      u'[[Bild:Flag of Bosnia and Herzegovina.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]otswana[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Botswana.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]razil[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Brazil.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]rasilien[_ ]flagge[_ ]gross.png',                             u'[[Bild:Flag of Brazil.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]runei[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Brunei.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]ulgaria[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Bulgaria.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]urkina faso[_ ]flag[_ ](medium|large|300).png',               u'[[Bild:Flag of Burkina Faso.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]urundi[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Burundi.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]hile[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Chile.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]hina[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of the People\'s Republic of China.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]China.png',                                      u'[[Bild:Flag of the People\'s Republic of China.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ook[_ ]islands[_ ]flag[_ ](medium|large|300).png',            u'[[Bild:Flag of the Cook Islands.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]osta[_ ]rica[_ ]flag[_ ](medium|large|300).png',              u'[[Bild:Flag of Costa Rica.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Denmark.png',                                    u'[[Bild:Flag of Denmark.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Dd]enmark[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Denmark.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]ermany[_ ]flag[_ ](mittel|medium|large|300).png',             u'[[Bild:Flag of Germany.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Germany.png',                                    u'[[Bild:Flag of Germany.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Dd]ominica[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Dominica.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Dd]ominican[_ ]republic[_ ]flag[_ ](medium|large|300).png'    ,  u'[[Bild:Flag of the Dominican Republic.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Dd]jibouti[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Djibouti.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]cuador[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Ecuador.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]l[_ ]salvador[_ ]flag[_ ](medium|large|300).png',             u'[[Bild:Flag of El Salvador.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Cote[_ ]d\'Ivoire.png',                          u'[[Bild:Flag of Cote d\'Ivoire.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ote[_ ]d\'ivoire[_ ]flag[_ ](medium|large|300).png',          u'[[Bild:Flag of Cote d\'Ivoire.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]ritrea[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Eritrea.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Estonia.png',                                    u'[[Bild:Flag of Estonia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]stonia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Estonia.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]iji[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Fiji.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]inland[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Finland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Finland.png',                                    u'[[Bild:Flag of Finland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]France.png',                                     u'[[Bild:Flag of France.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]rance[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of France.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]abun[_ ]flagge[_ ]gross.png',                                 u'[[Bild:Flag of Gabon.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]ambia[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of The Gambia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Georgien[_ ]neu.png',                                u'[[Bild:Flag of Georgia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]hana[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Ghana.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]reece[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Greece.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Greece.png',                                     u'[[Bild:Flag of Greece.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]renada[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Grenada.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]uatemala[_ ]flagge[_ ]gross.png',                             u'[[Bild:Flag of Guatemala.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]uatemala[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Guatemala.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]uyana[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Guyana.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]uinea[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Guinea.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Gg]uinea[_ ]bissau[_ ]flagge[_ ]gross.png',                      u'[[Bild:Flag of Guinea-Bissau.svg'),
            
            # Haiti ausgelassen: Wappenfrage
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Hh]onduras[_ ]flagge[_ ]gross.png',                              u'[[Bild:Flag of Honduras.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Hh]onduras[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Honduras.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]ndia[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of India.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]ndonesien[_ ]flagge[_ ]gross.png',                            u'[[Bild:Flag of Indonesia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Iraq.png',                                       u'[[Bild:Flag of Iraq.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]raq[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Iraq.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]ndonesia[_ ]flagge[_ ]gross.png',                             u'[[Bild:Flag of Indonesia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]ran[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Iran.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]reland[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Ireland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Ireland.png',                                    u'[[Bild:Flag of Ireland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]celand[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Iceland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]sland[_ ]flag.png',                                           u'[[Bild:Flag of Iceland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]srael[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Israel.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]srael[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Israel.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Israel.png',                                     u'[[Bild:Flag of Israel.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]talien[_ ]flagge[_ ]gross.png',                               u'[[Bild:Flag of Italy.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ii]taly[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Italy.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Italy.png',                                      u'[[Bild:Flag of Italy.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Jj]amaika[_ ]flagge[_ ]gross.png',                               u'[[Bild:Flag of Jamaica.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Jj]amaika[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Jamaica.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Jj]apan[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Japan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Jj]emen[_ ]flagge[_ ]gross.png',                                 u'[[Bild:Flag of Yemen.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Jj]ordanien[_ ]flagge[_ ]gross.png',                             u'[[Bild:Flag of Jordan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Jj]ordan[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Jordan.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ambodia[_ ]flag[_ ](medium|large).png',                       u'[[Bild:Flag of Cambodia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ameroon[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Cameroon.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]anada[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Canada.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]anada[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Canada.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ape[_ ]verde[_ ]flag[_ ](medium|large|300).png',              u'[[Bild:Flag of Cape Verde.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]azakhstan[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Kazakhstan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Kazakhstan.png',                                 u'[[Bild:Flag of Kazakhstan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Qatar.png',                                      u'[[Bild:Flag of Qatar.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Qq]atar[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Qatar.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]enya[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Kenya.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Kyrgyzstan.png',                                 u'[[Bild:Flag of Kyrgyzstan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]iribati[_ ]flagge[_ ]gross.png',                              u'[[Bild:Flag of Kiribati.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]olombia[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Colombia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]omoren[_ ]flagge[_ ]gross.png',                               u'[[Bild:Flag of the Comoros.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ongo[_ ]democratic[_ ]flag[_ ](medium|large|300).png',        u'[[Bild:Flag of the Democratic Republic of the Congo.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]ongo[_ ]republic[_ ]flag[_ ](medium|large|300).png',          u'[[Bild:Flag of the Republic of the Congo.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]roatia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Croatia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Cuba.png',                                       u'[[Bild:Flag of Cuba.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]uba[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Cuba.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]uwait[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Kuwait.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Kk]uwait[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Kuwait.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]aos[_ ]flagge[_ ]gross.png',                                  u'[[Bild:Flag of Laos.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]esotho[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Lesotho.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Lettland.png',                                       u'[[Bild:Flag of Latvia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]ibanon[_ ]flagge[_ ]gross.png',                               u'[[Bild:Flag of Lebanon.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]iberia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Liberia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]ibya[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Libya.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]iechtenstein[_ ]flagge[_ ]gross.png',                         u'[[Bild:Flag of Liechtenstein.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Lithuania.png',                                  u'[[Bild:Flag of Lithuania.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ll]uxembourg[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Luxembourg.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Luxembourg.png',                                 u'[[Bild:Flag of Luxembourg.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Madagascar.png',                                 u'[[Bild:Flag of Madagascar.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]alawi[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Malawi.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]alaysia[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Malaysia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Malediven.png',                                      u'[[Bild:Flag of Maldives.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Mali.png',                                       u'[[Bild:Flag of Mali.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]ali[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Mali.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]alta[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Malta.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]orocco[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Morocco.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]arshall[_ ]islands[_ ]flag[_ ](medium|large|300).png',        u'[[Bild:Flag of the Marshall Islands.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Mauritania.png',                                 u'[[Bild:Flag of Mauritania.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]auritius[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Mauritius.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Macedonia.png',                                  u'[[Bild:Flag of Macedonia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]acedonia[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Macedonia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Mexico.png',                                     u'[[Bild:Flag of Mexico.svg'),
            # coat of arms too undetailed in SVG
            # (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]exico[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Mexico.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]icronesia[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Micronesia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]oldova[_ ]flag[_ ](large|large-02|300).png',                  u'[[Bild:Flag of Moldova.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]onaco[_ ]flag.png',                                           u'[[Bild:Flag of Monaco.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Mongolia.png',                                   u'[[Bild:Flag of Mongolia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]ozambique[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Mozambique.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Mm]yanmar[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Myanmar.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]amibia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Namibia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Nauru.png',                                      u'[[Bild:Flag of Nauru.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]epal[_ ]flagge[_ ]gross.png',                                 u'[[Bild:Flag of Nepal.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]ew[_ ]zealand[_ ]flag[_ ](medium|large|300).png',             u'[[Bild:Flag of New Zealand.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]icaragua[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Nicaragua.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]the[_ ]Netherlands.png',                         u'[[Bild:Flag of the Netherlands.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]etherlands[_ ]flag[_ ](medium|large|300).png',                u'[[Bild:Flag of the Netherlands.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]iger[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Niger.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]igeria[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Nigeria.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]iue[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Niue.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]North[_ ]Korea.png',                             u'[[Bild:Flag of North Korea.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]von[_ ]Norwegen.png',                                u'[[Bild:Flag of Norway.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Norway.png',                                     u'[[Bild:Flag of Norway.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]orway[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Norway.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Aa]ustria[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Austria.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Oo]man[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Oman.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Pakistan.png',                                       u'[[Bild:Flag of Pakistan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Palaus[_ ]mittel.png',                               u'[[Bild:Flag of Palau.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Palestine.png',                                  u'[[Bild:Flag of Palestine.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]anama[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Panama.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]papua[_ ]new[_ ]guinea.png',                     u'[[Bild:Flag of Papua New Guinea.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]araguay[_ ]flagge[_ ]gross.png',                              u'[[Bild:Flag of Paraguay.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]araguay[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Paraguay.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]eru[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Peru.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]hilippines[_ ]flag[_ ](medium|large|300).png',                u'[[Bild:Flag of the Philippines.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]oland[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Poland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Poland.png',                                     u'[[Bild:Flag of Poland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Pp]ortugal[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Portugal.svg'),

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Rr]wanda[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Rwanda.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Rr]omania[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Romania.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Rr]ussia[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Russia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Russia.png',                                     u'[[Bild:Flag of Russia.svg'),
            
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Salomonen[_ ]mittel.png',                            u'[[Bild:Flag of the Solomon Islands.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]ambia[_ ]flagge[_ ]gross.png',                                u'[[Bild:Flag of Zambia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Zz]ambia[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Zambia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Samoas[_ ]mittel.png',                               u'[[Bild:Flag of Samoa.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]an[_ ]marino[_ ]flagge[_ ]gross.png',                         u'[[Bild:Flag of San Marino.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Sao[_ ]Tome[_ ]and[_ ]Principe.png',             u'[[Bild:Flag of Sao Tome and Principe.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]audi[_ ]arabia[_ ]flag[_ ](medium|large|300).png',            u'[[Bild:Flag of Saudi Arabia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]chweden[_ ]flagge.png',                                       u'[[Bild:Flag of Sweden.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]weden[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Sweden.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]witzerland[_ ]flag[_ ](medium|large|300).png',                u'[[Bild:Flag of Switzerland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]enegal[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Senegal.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Serbien-und-Montenegro.png',                         u'[[Bild:Flag of Serbia and Montenegro.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Yugoslavia[_ ]1992.png',                         u'[[Bild:Flag of Serbia and Montenegro.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Yy]ugoslavia[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Serbia and Montenegro.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]eychelles[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of the Seychelles.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]ierra[_ ]leone[_ ]flag[_ ](medium|large|300).png',            u'[[Bild:Flag of Sierra Leone.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Zz]imbabwe[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Zimbabwe.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]ingapore[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Singapore.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Slovakia.png',                                   u'[[Bild:Flag of Slovakia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]lowenien[_ ]flagge[_ ]gross[_ ]korr.png',                     u'[[Bild:Flag of Slovenia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]lovenia[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Slovenia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]von[_ ]Somalia.png',                                 u'[[Bild:Flag of Somalia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]pain[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Spain.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Spain.png',                                      u'[[Bild:Flag of Spain.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]St[_ ]Kitts[_ ]und[_ ]Nevis[_ ]mittel.png',          u'[[Bild:Flag of Saint Kitts and Nevis.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]saint[_ ]lucia[_ ]gross.png',                        u'[[Bild:Flag of Saint Lucia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]t[_ ]vincent[_ ]grenadines[_ ]flag[_ ](medium|large|300).png',u'[[Bild:Flag of Saint Vincent and the Grenadines.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]ri[_ ]lanka[_ ]flag[_ ](medium|large|300).png',               u'[[Bild:Flag of Sri Lanka.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]Südafrika.png',                                      u'[[Bild:Flag of South Africa.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]South[_ ]Africa.png',                            u'[[Bild:Flag of South Africa.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]outh[_ ]africa[_ ]flag[_ ](medium|large|300).png',            u'[[Bild:Flag of South Africa.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]udan[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Sudan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]South[_ ]Korea.png',                             u'[[Bild:Flag of South Korea.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]uriname[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Suriname.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]waziland[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Swaziland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]yria[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Syria.svg'),
            
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]tajikistan.png',                                 u'[[Bild:Flag of Tajikistan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]aiwan[_ ]flag.png',                                           u'[[Bild:Flag of the Republic of China.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]anzania[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Tanzania.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]hailand[_ ]flag[_ ](medium|large|300).png',                   u'[[Bild:Flag of Thailand.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]ast[_ ]timor[_ ]flag[_ ](medium|large|300).png',              u'[[Bild:Flag of East Timor.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]ogo[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Togo.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Togo.png',                                       u'[[Bild:Flag of Togo.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]onga[_ ]flag[_ ](medium|large|300).png',                      u'[[Bild:Flag of Tonga.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]rinidad[_ ]and[_ ]tobago[_ ]flag[_ ](medium|large|300).png',  u'[[Bild:Flag of Trinidad and Tobago.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]had[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of Chad.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]zech[_ ]republic[_ ]flag[_ ](medium|large|300).png',          u'[[Bild:Flag of the Czech Republic.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]unisia[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Tunisia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]uerkei[_ ]flagge[_ ]gross.png',                               u'[[Bild:Flag of Turkey.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]urkey[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Turkey.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Turkey.png',                                     u'[[Bild:Flag of Turkey.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]urkmenistan[_ ]flag[_ ](medium|large|300).png',               u'[[Bild:Flag of Turkmenistan.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Tt]uvalu[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Tuvalu.svg'),
            
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]ganda[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Uganda.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]kraine[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Ukraine.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Ukraine.png',                                    u'[[Bild:Flag of Ukraine.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Hungary.png',                                    u'[[Bild:Flag of Hungary.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Hh]ungary[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Hungary.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]ruguay[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Uruguay.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]s[_ ]flag[_ ](medium|large|300).png',                         u'[[Bild:Flag of the United States.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]the[_ ]United[_ ]States.png',                    u'[[Bild:Flag of the United States.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]zbekistan[_ ]flag[_ ](medium|large|300).png',                 u'[[Bild:Flag of Uzbekistan.svg'),
            
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Vv]anuatu[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Vanuatu.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Vatican[_ ]City.png',                            u'[[Bild:Flag of the Vatican.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Vv]enezuela[_ ]flag[_ ](medium|large|300).png',                  u'[[Bild:Flag of Venezuela.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]ae[_ ]flag[_ ](medium|large|300).png',                        u'[[Bild:Flag of the United Arab Emirates.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]k[_ ]flag[_ ](medium|large|300).png',                         u'[[Bild:Flag of the United Kingdom.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]the[_ ]United[_ ]Kingdom.png',                   u'[[Bild:Flag of the United Kingdom.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Vv]ietnam[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Vietnam.svg'),
            
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]elarus[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Belarus.svg'),
            # Westsahara

            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]entral[_ ]african[_ ]republic[_ ]flag[_ ](medium|large|300).png', u'[[Bild:Flag of the Central African Republic.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Cc]yprus[_ ]flag[_ ](medium|large|300).png',                     u'[[Bild:Flag of Cyprus.svg'),

            # Former nations
            
            #(u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]ast[_ ]Germany[_ ]flag.png',                                 u'[[Bild:       '),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ss]FRY[_ ]flag[_ ](medium|large|300).png',                       u'[[Bild:Flag of SFR Yugoslavia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]SFR[_ ]Yugoslavia.png',                          u'[[Bild:Flag of SFR Yugoslavia.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]der[_ ]Sowjetunion.png',                             u'[[Bild:Flag of the Soviet Union.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]the[_ ]Soviet[_ ]Union.png',                     u'[[Bild:Flag of the Soviet Union.svg'),
            
            # Non-souvereign regions
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Bb]ermuda[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of Bermuda.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]ngland[_ ]Flagge.PNG',                                        u'[[Bild:Flag of England.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]ngland[_ ]flag.png',                                          u'[[Bild:Flag of England.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lagge[_ ]England.png',                                        u'[[Bild:Flag of England.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]ngland[_ ]flag[_ ](medium|large|300).png',                    u'[[Bild:Flag of England.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Hh]ong[_ ]kong[_ ]flag[_ ](medium|large|300).png',               u'[[Bild:Flag of Hong Kong SAR.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Hong[_ ]Kong[_ ]SAR.png',                        u'[[Bild:Flag of Hong Kong SAR.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Nn]orthern[_ ]ireland[_ ]flag[_ ](medium|large|300).png',        u'[[Bild:Flag of Northern Ireland.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]the[_ ]Faroe[_ ]Islands.png',                    u'[[Bild:Flag of the Faroe Islands.svg'),
            # Tibet TibetFlaggeGross.png

            # Organizations
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]Europe.png',                                     u'[[Bild:European flag.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ee]speranto[_ ]flagge.png',                                      u'[[Bild:Flag of Esperanto.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]NATO.jpg',                                       u'[[Bild:Flag of NATO.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Ff]lag[_ ]of[_ ]the[_ ]United[_ ]Nations.png',                   u'[[Bild:Flag of the United Nations.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]nicef[_ ]flag.png',                                           u'[[Bild:Flag of UNICEF.svg'),
            (u'\[\[(?:[Bb]ild|[Ii]mage):[Uu]NESCO[_ ]flag.png',                                           u'[[Bild:Flag of UNESCO.svg'),
            
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
