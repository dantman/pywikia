# -*- coding: utf-8 -*-
"""
Script to copy a table from one Wikipedia to another one, translating it
on-the-fly. 

Syntax:
  copy_table.py -type:abcd -from:xy Article_Name

Command line options:

-from:xy       Copy the table from the Wikipedia article in language xy
               Article must have interwiki link to xy

-debug         Show debug info, and don't send the results to the server
              
-type:abcd     Translates the table, using translations given below.
               When the -type argument is not used, the bot will simply
               copy the table as-is.

Article_Name:  Name of the article where the table should be inserted

"""
#
# (C) Daniel Herding, 2004
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia,re,sys,string

# Translation database. Non-ASCII characters must be encoded in hexadecimal
# unicode and prefixed with a small u,
# e.g. u"[[Dom\xE4ne (Biologie)|Dom\xE4ne]]"
# Order is not important, but try to order the items anyway so that others 
# can change them more easily.
types = {
    # translations for images (inside other tables)
    "image": {
         "include": [],
         0: { "en":"[[image:",     "de":"[[bild:",                "nl":"[[afbeelding:", },
         1: { "en":"[[Image:",     "de":"[[Bild:",                "nl":"[[Afbeelding:", },
         2: { "en":"larger image", "de":u"Bild vergr\xF6\xDFern", "nl":"groter",        },
    },
    # translations for taxoboxes (for biology articles)
    "taxo": {
         "include": ["image"],
         0: { "en":"bgcolor=pink",                      "de":"bgcolor=\"#ffc0c0\"",                      "nl":"bgcolor=#EEEEEE",                                },
         1: { "en":"[[Scientific classification]]",     "de":"[[Systematik (Biologie)|Systematik]]",     "nl":"[[Taxonomie|Wetenschappelijke  classificatie]]", },
         2: { "en":"[[Domain (biology)|Domain]]",       "de":u"''[[Dom\xE4ne (Biologie)|Dom\xE4ne]]:''", "nl":"[[Domain (biologie)|Domain]]",                   },
         3: { "en":"[[Kingdom (biology)|Kingdom]]",     "de":"''[[Reich (Biologie)|Reich]]:''",          "nl":"[[Rijk (biologie)|Rijk]]",                       },
         4: { "en":"[[Phylum (biology)|Phylum]]",       "de":"''[[Stamm (Biologie)|Stamm]]:''",          "nl":"[[Stam (biologie)|Stam]]",                       },
         5: { "en":"[[Subphylum]]",                     "de":"''[[Unterstamm]]:''",                      "nl":"[[Substam (biologie)|Substam]]",                 },
         6: { "en":"[[Class (biology)|Class]]",         "de":"''[[Klasse (Biologie)|Klasse]]:''",        "nl":"[[Klasse (biologie)|Klasse]]",                   },
         7: { "en":"[[Subclass]]",                      "de":"''[[Klasse (Biologie)|Unterklasse]]:''",   "nl":"[[Onderklasse]]",                                },
         8: { "en":"[[Order (biology)|Order]]",         "de":"''[[Ordnung (Biologie)|Ordnung]]:''",      "nl":"[[Orde (biologie)|Orde]]",                       },
         9: { "en":"[[Suborder]]",                      "de":"''[[Ordnung (Biologie)|Unterordnung]]:''", "nl":"[[Infraorde (biologie)|Infraorde]]",             },
        10: { "en":"[[Family (biology)|Family]]",       "de":"''[[Familie (Biologie)|Familie]]:''",      "nl":"[[Familie (biologie)|Familie]]",                 },
        11: { "en":"[[Subfamily (biology)|Subfamily]]", "de":"''[[Familie (Biologie)|Unterfamilie]]:''", "nl":"[[Onderfamilie]]",                               },
        12: { "en":"[[Tribe (biology)|Tribe]]",         "de":"''[[Tribus (Biologie)|Tribus]]:''",        "nl":"[[Tak (biologie)|Tak]]",                         },
        13: { "en":"[[Genus]]",                         "de":"''[[Gattung (Biologie)|Gattung]]:''",      "nl":"[[Geslacht (biologie)|Geslacht]]",               },
        14: { "en":"[[Subgenus]]",                      "de":"''[[Gattung (Biologie)|Untergattung]]:''", "nl":"[[Ondergeslacht]]",                              },
        15: { "en":"[[Species]]",                       "de":"''[[Art (Biologie)|Art]]:''",              "nl":"[[Soort]]",                                      },
        16: { "en":"[[Genus|Genera]]",                  "de":"[[Gattung (Biologie)|Gattungen]]",         "nl":"[[Geslacht (biologie)|Geslacht]]",               },
        },
    "plant": {
        "include": ["taxo"],
        0: { "en":"bgcolor=lightgreen",               "de":"bgcolor=lightgreen",                     }, 
        1: { "en":"[[Division (biology)|Division]]",  "de":"''[[Abteilung (Biologie)|Abteilung]]''", },
        },
    }
        

if not wikipedia.special.has_key(wikipedia.mylang):
    print "Please add the translation for the Special: namespace in"
    print "Your home wikipedia to the wikipedia.py module"
    import sys
    sys.exit(1)

# Summary message
msg={
    "en":"robot: copying table from ",
    "de":"Bot: Kopiere Tabelle von ",
    }

# get edit summary message
if msg.has_key(wikipedia.mylang):
    msglang = wikipedia.mylang
else:
    msglang = "en"
    
page_name = ""
from_lang = ""
type = ""
debug = False

# read command line parameters
for arg in sys.argv[1:]:
    if wikipedia.argHandler(arg):
        pass
    elif arg.startswith("-from"):
        from_lang = arg[6:]
    elif arg.startswith("-type:"):
        type = arg[6:]
    elif arg == "-debug":
        debug = True
    else:
        page_name = arg

thispl = wikipedia.PageLink(wikipedia.mylang, page_name)

def treat(to_pl):
    try:
        to_text = to_pl.get()
        interwikis = to_pl.interwiki()
    except wikipedia.IsRedirectPage:
        print "Can't work on redirect page."
        return
    from_pl = ""
    for interwiki in interwikis:
        if interwiki.code() == from_lang:
            from_pl = interwiki
    if from_pl == "":
        print "Interwiki link to " + from_lang + " not found."
        return
    from_text = from_pl.get()
    wikipedia.setAction(msg[msglang] + from_lang + ":" + from_pl.linkname())
    # search start of table
    table = get_table(from_text)
    if not table:
        print "No table found in %s." % from_lang + ":" + from_pl.linkname()
        return
    table = translate(table, type)
    if not table:
        print "Could not translate table."
        return
    # add table to top of the article, seperated by a blank lines
    to_text = table + "\n\n" + to_text
    if not debug:
        print "Changing page %s" % (to_pl)
        to_pl.put(to_text)

# Regular expression that will match both <table and {|
startR = re.compile(r"<table|\{\|")
# Regular expression that will match both </table> and |}
endR = re.compile(r"</table>|\|\}")

# Finds the first table inside a text, including cascaded inner tables.
def get_table(text):
    pos = 0
    # find first start tag
    first_start_tag = re.search(startR, text)
    if not first_start_tag:
        return
    else:
        if debug: print "First start tag found at " + str(first_start_tag.start())
        pos = first_start_tag.end()
        table_level = 1
        remaining_text = text
    while table_level != 0:
        remaining_text = text[pos:]
        next_start_tag = re.search(startR, remaining_text, pos)
        next_end_tag = re.search(endR, remaining_text, pos)
        if not next_end_tag:
            if debug: print "Error: missing end tag"
            pass
        if next_start_tag and next_start_tag.start() < next_end_tag.start():
            if debug: print "Next start tag found at " + str(pos + next_start_tag.start())
            pos += next_start_tag.end()
            table_level += 1
            if debug: print "Table level is " + str(table_level)
        else:
            if debug: print "Next end tag found at " + str(pos + next_end_tag.start())
            pos += next_end_tag.end()
            table_level -= 1
            if debug: print "Table level is " + str(table_level)
    if debug: print "Table starts at " + str(first_start_tag.start()) + " and ends at " + str(pos)
    if debug: print text[first_start_tag.start():pos]
    return text[first_start_tag.start():pos]

def translate(text, type):
    if type == "":
        return text
    else:
        if debug: print "Trying to translate type " + type
        # check if the translation database knows this type of table
        if not types.has_key(type):
            print "Unknown table type: " + type
            pass
        else:
            translation = types.get(type)
        for i in range(len(translation)-1):
            # check if the translation database includes the two needed languages
            if not (translation.has_key(i) and translation.get(i).has_key(from_lang) and translation.get(i).has_key(wikipedia.mylang)):
                print "Can't translate. Please make sure that there are entries for " + from_lang + " and " + wikipedia.mylang + " for type " + type + " in copy_table.py."
                return
            if debug: print str(i) + ": " + translation.get(i).get(from_lang) + " => " + translation.get(i).get(wikipedia.mylang)
            text = string.replace(text, translation.get(i).get(from_lang), translation.get(i).get(wikipedia.mylang))
        for inc in translation.get("include"):
            print type
            text = translate(text, inc)
        print text
        return text
        
treat(thispl)