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

-file:XYZ      Reads article names from a file. XYZ is the name of the 
               file from which the list is taken. If XYZ is not given, the
               user is asked for a filename.
               Page titles should be saved one per line, without [[brackets]].
               The -pos parameter won't work if -file is used.                              

Article_Name:  Name of the article where a table should be inserted

"""
#
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia,re,sys,string

# Translation database. Non-ASCII characters must be encoded in hexadecimal
# unicode and prefixed with a small u,
# e.g. u"[[Dom\xE4ne (Biologie)|Dom\xE4ne]]"

# For each table type, there can be three lists:
#  * "translations" - direct replacements. Work in either direction.
#  * "regexes" - regular expression replacements. These are more powerful tthan
#     direct replacements, but only work in one direction.
#  * "includes" - items from another table type are included.

types = {
    # translations for images (inside other tables)
    "images": {
         "translations": [
             { "en":"[[image:",     "de":"[[bild:",                "nl":"[[afbeelding:", "fr":"[[image:",      },
             { "en":"[[Image:",     "de":"[[Bild:",                "nl":"[[Afbeelding:", "fr":"[[Image:",      },
             { "en":"larger image", "de":u"Bild vergr\xF6\xDFern", "nl":"groter",        "fr":u"En d\xE9tail"  },
             # usually used as link description for articles about flags, coats of arms etc.
             { "en":"Details",      "de":u"Details",               "nl":"details",       "fr":u"D\xE9tails"    },
         ],
    },
    # translations for taxoboxes (for biology articles)
    "taxo": {
        "translations": [
            # Background colors for table headers, with or without quotation marks (taxoboxes on de: all have quotation marks)
            { "en":"bgcolor=pink",                         "de":"bgcolor=\"#ffc0c0\"",                       "nl":"bgcolor=#EEEEEE",                                "fr":"bgcolor=pink"                               },
            { "en":"bgcolor=\"pink\"",                     "de":"bgcolor=\"#ffc0c0\"",                       "nl":"bgcolor=\"#EEEEEE\"",                            "fr":"bgcolor=\"pink\""                           },
            # second table header (below the image)
            { "en":"[[Scientific classification]]",        "de":"[[Systematik (Biologie)|Systematik]]",      "nl":"[[Taxonomie|Wetenschappelijke  classificatie]]", "fr":u"Classification [[syst\xE9matique]]"        },
            # main taxobox content
            { "en":"[[Domain (biology)|Domain]]:",         "de":u"''[[Dom\xE4ne (Biologie)|Dom\xE4ne]]:''",  "nl":"[[Domain (biologie)|Domain]]:",                  "fr":"??? (domain)"                               },
            { "en":"[[Kingdom (biology)|Kingdom]]:",       "de":"''[[Reich (Biologie)|Reich]]:''",           "nl":"[[Rijk (biologie)|Rijk]]:",                      "fr":u"[[R\xE8gne (biologie)|R\xE8gne]]:",        },
            { "en":"[[Phylum (biology)|Phylum]]:",         "de":"''[[Stamm (Biologie)|Stamm]]:''",           "nl":"[[Stam (biologie)|Stam]]:",                      "fr":"[[Embranchement]]:",                        },
            { "en":"[[Subphylum]]:",                       "de":"''[[Unterstamm]]:''",                       "nl":"[[Substam (biologie)|Substam]]:",                "fr":"[[Sous-embranchement]]:",                   },
            { "en":"[[Superclass (biology)|Superclass]]:", "de":u"''[[Klasse (Biologie)|\xDCberklasse]]:''", "nl":"[[Superklasse (biologie)|Superklasse]]:",        "fr":"[[Super-classe (biologie)|Super-classe]]:", },
            { "en":"[[Class (biology)|Class]]:",           "de":"''[[Klasse (Biologie)|Klasse]]:''",         "nl":"[[Klasse (biologie)|Klasse]]:",                  "fr":"[[Classe (biologie)|Classe]]:",             },
            { "en":"[[Subclass]]:",                        "de":"''[[Klasse (Biologie)|Unterklasse]]:''",    "nl":"[[Onderklasse]]:",                               "fr":"[[Sous-classe (biologie)|Sous-classe]]:",   },
            { "en":"[[Order (biology)|Order]]:",           "de":"''[[Ordnung (Biologie)|Ordnung]]:''",       "nl":"[[Orde (biologie)|Orde]]:",                      "fr":"[[Ordre (biologie)|Ordre]]:"                },
            { "en":"[[Suborder]]:",                        "de":"''[[Ordnung (Biologie)|Unterordnung]]:''",  "nl":"[[Infraorde (biologie)|Infraorde]]:",            "fr":"[[Sous-ordre (biologie)|Sous-ordre]]:",     },
            { "en":"[[Family (biology)|Family]]:",         "de":"''[[Familie (Biologie)|Familie]]:''",       "nl":"[[Familie (biologie)|Familie]]:",                "fr":"[[Famille (biologie)|Famille]]:",           },
            { "en":"[[Subfamily (biology)|Subfamily]]:",   "de":"''[[Familie (Biologie)|Unterfamilie]]:''",  "nl":"[[Onderfamilie]]:",                              "fr":"[[Sous-famille (biologie)|Sous-famille]]:", },
            { "en":"[[Tribe (biology)|Tribe]]:",           "de":"''[[Tribus (Biologie)|Tribus]]:''",         "nl":"[[Tak (biologie)|Tak]]:",                        "fr":"??? (Tribus)"                               },
            { "en":"[[Genus]]:",                           "de":"''[[Gattung (Biologie)|Gattung]]:''",       "nl":"[[Geslacht (biologie)|Geslacht]]:",              "fr":"[[Genre]]:"                                 },
            { "en":"[[Subgenus]]:",                        "de":"''[[Gattung (Biologie)|Untergattung]]:''",  "nl":"[[Ondergeslacht]]:",                             "fr":"??? (Sous-genre)"                           },
            { "en":"[[Species]]:",                         "de":"''[[Art (Biologie)|Art]]:''",               "nl":"[[Soort]]:",                                     "fr":u"[[Esp\xE8ce]]:"                            },
            # table headers for subdivisions of the current group
            { "en":"[[Order (biology)|Orders]]",           "de":"[[Ordnung (Biologie)|Ordnungen]]",          "nl":"[[Orde (biologie)|Orden]]",                      "fr":"[[Ordre (biologie)|Ordres]]"                },
            { "en":"[[Suborder]]s",                        "de":"[[Ordnung (Biologie)|Unterordnungen]]",     "nl":"[[Infraorde (biologie)|Infraorden]]:",           "fr":"[[Sous-ordre (biologie)|Sous-ordres]]",     },
            { "en":"[[Genus|Genera]]",                     "de":"[[Gattung (Biologie)|Gattungen]]",          "nl":"[[Geslacht (biologie)|Geslachten]]",             "fr":"[[Genre (biologie)|Genre]]"                 },
            { "en":"[[Species]]",                          "de":"[[Art (Biologie)|Arten]]",                  "nl":"[[Soort]]en",                                    "fr":u"??? (Esp\xE8ces)"                          },
            { "en":"[[Species]] (incomplete)",             "de":"[[Art (Biologie)|Arten (Auswahl)]]",        "nl":"[[Soort]]en (incompleet)",                       "fr":u"??? (Esp\xE8ces (s\xE9lection))"           },
            # table headers for nl: style taxoboxes (current group is listed in a special section at the bottom)
            { "en":"[[Order (biology)|Order]]",            "de":"[[Ordnung (Biologie)|Ordnung]]",            "nl":"[[Orde (biologie)|Orde]]",                       "fr":"[[Ordre (biologie)|Ordre]]"                 },
            { "en":"[[Family (biology)|Family]]",          "de":"[[Familie (Biologie)|Familie]]",            "nl":"[[Familie (biologie)|Familie]]",                 "fr":"[[Famille (biologie)|Famille]]",            },
            { "en":"[[Genus]]",                            "de":"[[Gattung (Biologie)|Gattung]]",            "nl":"[[Geslacht (biologie)|Geslacht]]",               "fr":"[[Genre]]"                                  },
            { "en":"[[Species]]",                          "de":"[[Art (Biologie)|Art]]",                    "nl":"[[Soort]]",                                      "fr":u"[[Esp\xE8ce]]"                             },
        ],
        "includes": ["images"],
    },

    # not sure if this requires an extra list
#    "plant": {
#        0: { "en":"bgcolor=lightgreen",               "de":"bgcolor=lightgreen",                     }, 
#        1: { "en":"[[Division (biology)|Division]]",  "de":"''[[Abteilung (Biologie)|Abteilung]]''", },
#        "include": ["taxo"],
#        },

    # regular expressions for number formats
    "numbers": {
        "regexes": {
            "fr": {
                # fr uses &nbsp; or space to separate thousands, de uses dots
                "(?P<pre>\d+)\&nbsp;(?P<block>\d\d\d)": {"de":"\g<pre>.\g<block>", },
                "(?P<pre>\d+) (?P<block>\d\d\d)": {"de":"\g<pre>.\g<block>", },
            },
            "de": {
                # de uses dots to separate thousands, en uses commas
                # de uses commas to indicate floating point numbers, en uses dots
                # no solution for this at the moment
            },
        },
    },
   
    # units of measurement etc.
    # only for internal use
    "units": {
        "translations": [
            { "en":"[[Square kilometre|km&sup2;]]",  "de":"[[Quadratkilometer|km&sup2;]]",   },
            { "en":u"[[Square kilometre|km\xB2]]",   "de":u"[[Quadratkilometer|km\xB2]]",    },
            # million
            { "en":"mill.",                          "de":"Mio.",                            },
            { "en":"as of ",                         "de":"Stand: ",                         },
            { "en":"years",                          "de":"Jahre",                           },
        ]
    },
    
    # general geographical terms etc.
    # only for internal use
    "geography": {
        "translations": [
            { "en":"[[Area]]:",                            "de":u"[[Fl\xE4che]]:",                "nl":"[[Oppervlakte]]:",         "fr":"[[Superficie]]:",  },
            { "en":"[[Population]]:",                      "de":"[[Einwohner]]:",                 "nl":"inwoners",                   },
            { "en":"[[Population density]]:",              "de":u"[[Bev\xF6lkerungsdichte]]:",    "nl":"[[Bevolkingsdichtheid]]:",   },
            { "en":"inh./km&sup2;",                        "de":"Einw./km&sup2;",                                                  "fr":"hab/km&sup2;", },
            { "en":u"inh./km\xB2",                         "de":u"Einw./km\xB2",                                                   "fr":u"hab/km\xB2",  },
            { "en":"inhabitants/km&sup2;",                 "de":"Einwohner/km&sup2;",               },
            { "en":u"inhabitants/km\xB2",                  "de":u"Einwohner/km\xB2",                },
            { "en":"inhabitants per km&sup2;",             "de":"Einwohner pro km&sup2;"           },
            { "en":u"inhabitants per km\xB2",              "de":u"Einwohner pro km\xB2"            },
            { "en":"inh.",                                 "de":"Einw.",                                                            "fr":"hab.", },
            { "en":"m above sea level",                    "de":u"m \xFC. [[Normalnull|NN]]",      },
            # longitude, latitude
            { "en":"' north",                              "de":u"' n\xF6rdl. Breite",             },
            { "en":"' north",                              "de":"' n. Br.",                        },
            { "en":"' east",                               "de":u"' \xF6stl. L\xE4nge",            },
            { "en":"' east",                               "de":u"' \xF6. L.",                     },
            { "en":"Map",                                  "de":"Karte",                                   },
            { "en":"Coat of Arms",                         "de":"Wappen",                                                            "fr":"Blason"      },
        ],
        "includes": ["units"],
    },
            
    "city": {
        "translations": [
            { "en":"Base data",                            "de":"Basisdaten"                               },
            { "en":"[[Location]]:",                        "de":"[[Geografische Lage]]:",                  },
            { "en":"[[Altitude]]:",                        "de":u"[[H\xF6he]]:",                           },
            { "en":"Highest point:",                       "de":u"H\xF6chster Punkt:",                     },
            { "en":"Lowest point:",                        "de":u"Niedrigster Punkt:",                     },
            { "en":"[[Postal code]]:",                     "de":"[[Postleitzahl]]:",                       },
            { "en":"[[Postal code]]s:",                    "de":"[[Postleitzahl]]en:",                     },
            { "en":"[[Area code]]:",                       "de":"[[Telefonvorwahl|Vorwahl]]:",             },
            { "en":"[[License plate]]:",                   "de":"[[KFZ-Kennzeichen]]:"                     },
            { "en":"[[License plate]]:",                   "de":"[[Kfz-Kennzeichen]]:"                     },
            { "en":"City structure:",                      "de":"Gliederung des Stadtgebiets:"             },
            { "en":"Municipality's address:",              "de":"Adresse der Stadtverwaltung:"             },
            { "en":"Website:",                             "de":"Website:",                                },
            { "en":"E-Mail adress:",                       "de":"[[E-Mail]]-Adresse:",                       "nl":"E-mail adres",               },
            { "en":"E-Mail adress:",                       "de":"E-Mail-Adresse:",                           "nl":"E-mail adres",               },
            # table header
            { "en":"Politics",                             "de":"Politik",                                 },
            # female mayor
            { "en":"[[Mayor]]:",                           "de":u"[[B\xFCrgermeister]]in:",                },
            { "en":"[[Mayor]]:",                           "de":u"[[B\xFCrgermeisterin]]:",                },
            # male mayor
            { "en":"[[Mayor]]:",                           "de":u"[[B\xFCrgermeister]]:",                  },
            { "en":"Governing [[Political party|party]]:", "de":"Regierende [[Politische Partei|Partei]]", },
            { "en":"Debts:",                               "de":"Schulden:",                               },
            { "en":"[[Unemployment]]:",                    "de":"[[Arbeitslosenquote]]:",                  },
            { "en":"Age distribution:",                    "de":"Altersstruktur:",                         },
        ],
        "includes": ["images", "geography"],
    },
    
    # translations for cities in Germany
    "city-de": {
        "translations": [
            { "en":"[Bundesland]]:",           "de":"[Bundesland]]:",                       "nl":"[[Deelstaat (Duitsland)|Deelstaat]]",     },
            { "en":"[[Regierungsbezirk]]:",    "de":"[[Regierungsbezirk]]:",                "nl":"[[Regierungsbezirk]]:",                   },
            { "en":"[District]]:",             "de":"[Landkreis|Kreis]]:",                  "nl":"[[District]]",                            },
            { "en":"[District]]:",             "de":"[Landkreis]]:",                        "nl":"[[District]]",                            },
            { "en":"district-free town",       "de":"[[kreisfreie Stadt]]",                 "nl":"[[Stadsdistrict]]",                       },
            { "en":"District-free town",       "de":"[[Kreisfreie Stadt]]",                 "nl":"[[stadsdistrict]]",                       },
            { "en":"[[Municipality key]]:",    "de":"[[Amtliche Gemeindekennzahl]]:", },
            { "en":"[[Municipality key]]:",    "de":u"[[Amtlicher Gemeindeschl\xFCssel]]:", },
            { "en":"urban district",           "de":"[[Stadtbezirk]]e",                     },
            # female first mayor, no exact translation in en:
            { "en":"[[Mayor]]:",               "de":u"[[Oberb\xFCrgermeisterin]]:",         },
            { "en":"[[Mayor]]:",               "de":u"[[Oberb\xFCrgermeister]]in:",         },
            # male first mayor, no exact translation in en:
            { "en":"[[Mayor]]:",               "de":u"[[Oberb\xFCrgermeister]]:",           },
            # "bis" is used between postal codes
            { "en":" to ",                     "de":" bis ",                                },
            # Image alt text
            { "en":"Map of Germany, ",         "de":"Deutschlandkarte, ",                   },
            { "en":" marked",                  "de":" markiert",                            },
        ],
        "includes": ["city"],
    },
    
    # French départements
    "dep": {
        "translations": [
            # some entries on fr: lack colons, others have spaces before the colons.
            { "de":"Basisdaten",                                   "fr":"Informations",                              },
            { "de":"[[Region (Frankreich)|Region]]:",              "fr":u"[[R\xE9gions fran\xE7aises|R\xE9gion]] :", },
            { "de":"[[Region (Frankreich)|Region]]:",              "fr":u"[[R\xE9gions fran\xE7aises|R\xE9gion]]:",  },
            { "de":u"[[Pr\xE4fektur (Frankreich)|Pr\xE4fektur]]:", "fr":u"[[Pr\xE9fecture]] :",                      },
            { "de":u"[[Pr\xE4fektur (Frankreich)|Pr\xE4fektur]]:", "fr":u"[[Pr\xE9fecture]]:",                       },
            { "de":u"[[Unterpr\xE4fektur]]en:",                    "fr":u"[[Sous-pr\xE9fecture]]s :",                },
            { "de":u"[[Unterpr\xE4fektur]]en:",                    "fr":u"[[Sous-pr\xE9fecture]]s:",                 },
            { "de":u"[[Unterpr\xE4fektur]]:",                      "fr":u"[[Sous-pr\xE9fecture]] :",                },
            { "de":u"[[Unterpr\xE4fektur]]:",                      "fr":u"[[Sous-pr\xE9fecture]]:",                 },
            { "de":"insgesamt",                                    "fr":"Totale",                                    },
            # the next three items are already in the list "geography", but someone forgot the colons on fr:
            { "de":u"[[Einwohner]]:",                              "fr":u"[[Population]]",  },
            { "de":u"[[Bev\xF6lkerungsdichte|Dichte]]:",           "fr":u"[[Densit\xE9 de population|Densit\xE9]]",  },
            { "de":u"[[Fl\xE4che]]:",                              "fr":"[[Superficie]]",                            },
            # another workaround for a forgotten colon
            { "de":"''</small>:",                                  "fr":"''</small>",                           },
            { "de":"[[Arrondissement]]s:",                         "fr":"[[Arrondissement]]s",                       },
            { "de":"[[Kanton (Frankreich)|Kantone]]:",             "fr":u"[[Cantons fran\xE7ais|Cantons]]",          },
            { "de":"[[Kommune (Frankreich)|Kommunen]]:",           "fr":"[[Communes de France|Communes]]",           },
            { "de":u"Pr\xE4sident des<br>[[Allgemeiner Rat|Allgemeinen Rates]]:",
                                                                   "fr":u"[[Pr\xE9sident du Conseil g\xE9n\xE9ral|Pr\xE9sident du Conseil<br> g\xE9n\xE9ral]]", },
            # image alt text
            { "de":"Lage von ",                                    "fr":"Localisation de la ",                       },
            { "de":"Lage von ",                                    "fr":"Localisation des ",                       },
            { "de":"Lage von ",                                    "fr":"Localisation de ",                       },
            { "de":" in Frankreich",                               "fr":" en France",                                },
            # table header for image
            { "de":"Geografische Lage",                            "fr":"Localisation",                              },
        ],
        "regexes":
            { "fr": {
                "\[\[[aA]rrondissements (des |du |de la |de l\'|d\'|de )":  {"de":u"[[Arrondissemens im D\xE9partement ", },
                "\[\[[cC]ommunes (des |du |de la |de l\'|d\'|de )":         {"de":u"[[Kommunen im D\xE9partement ",       },
                "\[\[[cC]antons (des |du |de la|de l\'|d\'|de )":           {"de":u"[[Kantone im D\xE9partement ",        },
                "Blason (des |du |de la |de l\'|d\'|de )":                 {"de":"Wappen von ",                          },
            },  
        },
        "includes": ["numbers", "images", "geography"],
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

# prints text on the screen only if in -debug mode
def print_debug(text):
    if debug:
        print text
    
# if the -file argument is used, page titles are dumped in this array.
# otherwise it will only contain one page.
page_list = []
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
    elif arg.startswith('-file'):
        if len(arg) == 5:
            file = raw_input('Please enter the list\'s filename: ')
        else:
            file = arg[6:]
        # open file and read page titles out of it
        f=open(file)
        for line in f.readlines():
            if line != '\n':           
                page_list.append(line)
        f.close()
    else:
        page_list.append(arg)

def treat(to_pl):
    try:
        to_text = to_pl.get()
        interwikis = to_pl.interwiki()
    except wikipedia.IsRedirectPage:
        print "Can't work on redirect page."
        return
    except wikipedia.NoPage:
        print "Page not found."
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
    print_debug("\n" + table)
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
        print_debug("First start tag found at " + str(first_start_tag.start()))
        pos = first_start_tag.end()
        # number of start tags minus numer of end tags
        table_level = 1
        remaining_text = text
    # until an end tag has been found for each start tag:
    while table_level != 0:
        # continue search after the last found tag
        remaining_text = text[pos:]
        next_start_tag = re.search(startR, remaining_text, pos)
        next_end_tag = re.search(endR, remaining_text, pos)
        if not next_end_tag:
            print_debug("Error: missing end tag")
            pass
        # if another cascaded table is opened before the current one is closed    
        elif next_start_tag and next_start_tag.start() < next_end_tag.start():
            print_debug( "Next start tag found at " + str(pos + next_start_tag.start()))
            pos += next_start_tag.end()
            table_level += 1
            print_debug("Table level is " + str(table_level))
        else:
            print_debug( "Next end tag found at " + str(pos + next_end_tag.start()))
            pos += next_end_tag.end()
            table_level -= 1
            print_debug("Table level is " + str(table_level))
    print_debug("Table starts at " + str(first_start_tag.start()) + " and ends at " + str(pos) +"\n")
    print_debug(text[first_start_tag.start():pos])
    return text[first_start_tag.start():pos]

def translate(text, type):
    if type == "":
        return text
    else:
        print_debug("\n Translating type " + type + "\n")
        # check if the translation database knows this type of table
        if not types.has_key(type):
            print "Unknown table type: " + type
            return
        if types.get(type).has_key("translations"):
            print_debug("direct translations for type " + type + "\n")
            for item in types.get(type).get("translations"):
                # check if the translation database includes the source language
                if not item.has_key(from_lang):
                    print_debug(from_lang + " translation for item not found in translation table, skipping item")
                    continue
                # if it's necessary to replace a substring
                if string.find(text, item.get(from_lang)) > -1:
                     # check if the translation database includes the target language
                     if not item.has_key(wikipedia.mylang):
                         print "Can't translate \"" + item.get(from_lang) + "\". Please make sure that there is a translation in copy_table.py."
                     else:
                         print_debug(item.get(from_lang) + " => " + item.get(wikipedia.mylang))
                         # translate a substring
                         text = string.replace(text, item.get(from_lang), item.get(wikipedia.mylang))
        if types.get(type).has_key("regexes"):
            # work on regular expressions
            print_debug("\n Working on regular expressions for type " + type + "\n")
            regexes = types.get(type).get("regexes")
            if regexes.has_key(from_lang):
                for item in regexes.get(from_lang):
                    if regexes.get(from_lang).get(item).has_key(wikipedia.mylang):
                        replacement = regexes.get(from_lang).get(item).get(wikipedia.mylang)
                        print_debug(item + " => " + replacement)
                        regex = re.compile(item)
                        text = re.sub(regex, replacement, text)
        # recursively use translation lists which are included in the current list
        if types.get(type).has_key("includes"):
            for inc in types.get(type).get("includes"):
                text = translate(text, inc)
        return text
        
for current_page_name in page_list:
    thispl = wikipedia.PageLink(wikipedia.mylang, current_page_name)
    treat(thispl)