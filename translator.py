# -*- coding: iso8859-1 -*-

# Translation database. Non-ASCII characters must be encoded in hexadecimal
# unicode and prefixed with a small u,
# e.g. u"[[Dom\xE4ne (Biologie)|Dom\xE4ne]]"

# For each table type, there can be three lists:
#  * "translations" - direct replacements. Work in either direction.
#  * "regexes" - regular expression replacements. These are more powerful tthan
#     direct replacements, but only work in one direction.
#  * "includes" - items from another table type are included.

#
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
#
#

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
            { "en":"[[Family (biology)|Families]]",          "de":"[[Familie (Biologie)|Familien]]",         "nl":"[[Familie (biologie)|Families]]",                "fr":"[[Famille (biologie)|Familles]]",           },
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
    
    "months": {
        "translations": [
				    { "sl":"januar",    "it":"gennaio",   "en":"January",   "de":"Januar",    "fr":"janvier",   "nl":"januari", },
				    { "sl":"februar",   "it":"febbraio",  "en":"February",  "de":"Februar",   "fr":"fevrier",   "nl":"februari", },
				    { "sl":"marec",     "it":"marzo",     "en":"March",     "de":"M&auml;rz", "fr":"mars",      "nl":"maart", },
				    { "sl":"april",     "it":"aprile",    "en":"April",     "de":"April",     "fr":"avril",     "nl":"april", },
				    { "sl":"maj",       "it":"maggio",    "en":"May",       "de":"Mai",       "fr":"mai",       "nl":"mei", },
				    { "sl":"junij",     "it":"giugno",    "en":"June",      "de":"Juni",      "fr":"juin",      "nl":"juni", },
				    { "sl":"julij",     "it":"luglio",    "en":"July",      "de":"Juli",      "fr":"juillet",   "nl":"juli", },
				    { "sl":"avgust",    "it":"agosto",    "en":"August",    "de":"August",    "fr":"aout",      "nl":"augustus", },
				    { "sl":"september", "it":"settembre", "en":"September", "de":"September", "fr":"septembre", "nl":"september", },
				    { "sl":"oktober",   "it":"ottobre",   "en":"October",   "de":"Oktober",   "fr":"octobre",   "nl":"oktober", },
				    { "sl":"november",  "it":"novembre",  "en":"November",  "de":"November",  "fr":"novembre",  "nl":"november", },
				    { "sl":"december",  "it":"dicembre",  "en":"December",  "de":"Dezember",  "fr":"decembre",  "nl":"december", },
        ]
    },
    
   
    # units of measurement etc.
    # only for internal use
    "units": {
        "translations": [
            { "en":"[[Square kilometre|km&sup2;]]",  "de":"[[Quadratkilometer|km&sup2;]]",  "nl":"[[Vierkante kilometer|km&sup2;]]", },
            { "en":u"[[Square kilometre|km\xB2]]",   "de":u"[[Quadratkilometer|km\xB2]]",   "de":u"[[Vierkante kilometer|km\xB2]]",     },
            # million
            { "en":"mill.",                          "de":"Mio.",                            },
            { "en":"as of ",                         "de":"Stand: ",                         },
            { "en":"years",                          "de":"Jahre",                           "nl":"Jaar"},
        ]
    },
    
    # general geographical terms etc.
    # only for internal use
    "geography": {
        "translations": [
            { "en":"[[Area]]:",                            "de":u"[[Fl\xE4che]]:",                "nl":"Oppervlakte:",         "fr":"[[Superficie]]:",  },
            { "en":"[[Population]]:",                      "de":"[[Einwohner]]:",                 "nl":"Inwoneraantal:",                },
            { "en":"[[Population density]]:",              "de":u"[[Bev\xF6lkerungsdichte]]:",    "nl":"[[Bevolkingsdichtheid]]:",   },
            { "en":"inh./km&sup2;",                        "de":"Einw./km&sup2;",                 "nl":"inw./km&sup2;",           "fr":"hab/km&sup2;", },
            { "en":u"inh./km\xB2",                         "de":u"Einw./km\xB2",                  "nl":u"inw./km\xB2",                                  "fr":u"hab/km\xB2",  },
            { "en":"inhabitants/km&sup2;",                 "de":"Einwohner/km&sup2;",             "nl":"inwoners / km&sup2;",                },
            { "en":u"inhabitants/km\xB2",                  "de":u"Einwohner/km\xB2",              "nl":u"inwoners / km\xB2",               },
            { "en":"inhabitants per km&sup2;",             "de":"Einwohner pro km&sup2;",         "nl":"inwoners per km&sup2;",               }, 
            { "en":u"inhabitants per km\xB2",              "de":u"Einwohner pro km\xB2",           "nl":u"inwoners per km\xB2",                    },
            { "en":"inh.",                                 "de":"Einw.",                          "nl":"inw.",                      "fr":"hab.", },
            { "en":"above [[sea level]]",                  "de":u"\xFC. [[Normalnull|NN]]",       "nl":"boven [[Normaal Amsterdams Peil|NAP]]",                           },
            # longitude, latitude
            { "en":"' north",                              "de":u"' n\xF6rdl. Breite",            "nl":"' NB" },
            { "en":"' north",                              "de":"' n. Br.",                       "nl":"' NB" },
            { "en":"' east",                               "de":u"' \xF6stl. L\xE4nge",           "nl":"' OL" },
            { "en":"' east",                               "de":u"' \xF6. L.",                    "nl":"' OL" },
            { "en":"Map",                                  "de":"Karte",                          "nl":"Kaart",                        },
            { "en":"Coat of Arms",                         "de":"Wappen",                         "nl":"Wapen",                       "fr":"Blason"      },
        ],
        "includes": ["units"],
    },
            
    "city": {
        "translations": [
            { "en":"Base data",                              "de":"Basisdaten"                                                              },
            { "en":"[[Location]]:",                          "de":"[[Geografische Lage]]:",                    "nl":"Ligging", },
            { "en":"[[Altitude]]:",                          "de":u"[[H\xF6he]]:",                             "nl":"Hoogte:", },
            { "en":"Highest point:",                         "de":u"H\xF6chster Punkt:",                       "nl":"Hoogste punt:",},
            { "en":"Lowest point:",                          "de":"Niedrigster Punkt:",                        "nl":"Laagste punt:"},
            { "en":"[[Postal code]]:",                       "de":"[[Postleitzahl]]:",                         "nl":"[[Postcode]]:",                 },
            { "en":"[[Postal code]]s:",                      "de":"[[Postleitzahl]]en:",                       "nl":"[[Postcode]]s:",                 },
            { "en":"[[Area code]]:",                         "de":"[[Telefonvorwahl|Vorwahl]]:",               "nl":"[[Netnummer]]:",             },
            { "en":"[[Area code]]s:",                        "de":"[[Telefonvorwahl|Vorwahlen]]:",             "nl":"[[Netnummer]]s:",             },
            { "en":"[[License plate]]:",                     "de":"[[KFZ-Kennzeichen]]:",                      "nl":"[[Autonummerbord]]:",         },
            { "en":"[[License plate]]:",                     "de":"[[Kfz-Kennzeichen]]:",                      "nl":"[[Autonummerbord]]:",           },
            { "en":"City structure:",                        "de":"Gliederung des Stadtgebiets:",              "nl":"Ondergemeentelijke indeling:",  },
            # town hall snail mail address
            { "en":"Municipality's address:",                "de":"Adresse der Gemeindeverwaltung:",           "nl":"Adres gemeentehuis:",       },
            # city hall snail mail address
            { "en":"Municipality's address:",                "de":"Adresse der Stadtverwaltung:",              "nl":"Adres stadhuis:",       },
            { "en":"Website:",                               "de":"Website:",                                  "nl":"Website:"     },
            { "en":"E-Mail adress:",                         "de":"[[E-Mail]]-Adresse:",                       "nl":"Email-adres:",               },
            { "en":"E-Mail adress:",                         "de":"E-Mail-Adresse:",                           "nl":"Email-adres:",               },
            # table header
            { "en":"Politics",                               "de":"Politik",                                   "nl":"Politiek",                  },
            # female mayor
            { "en":"[[Mayor]]:",                             "de":u"[[B\xFCrgermeister]]in:",                  "nl":"[[Burgermeester]]:",               },
            { "en":"[[Mayor]]:",                             "de":u"[[B\xFCrgermeisterin]]:",                  "nl":"[[Burgermeester]]:",          },
            # male mayor
            { "en":"[[Mayor]]:",                             "de":u"[[B\xFCrgermeister]]:",                    "nl":"[[Burgemeester]]:",           },
            { "en":"Governing [[Political party|party]]:",   "de":"Regierende [[Politische Partei|Partei]]",   "nl":"Regerende partij",               },
            { "en":"Governing [[Political party|parties]]:", "de":"Regierende [[Politische Partei|Parteien]]", "nl":"Regerende partijen",             },
            { "en":"Majority [[Political party|party]]:",   "de":"[[Politische Partei|Mehrheitspartei]]",      "nl":"Meerderheidspartij"},
            { "en":"Debts:",                                 "de":"Schulden:",                                     },
            { "en":"[[Unemployment]]:",                      "de":"[[Arbeitslosenquote]]:",                    "nl":"Werkloosheidspercentage:", },
            {                                                "de":u"[[Ausl\xE4nderanteil]]:",                  "nl":"Percentage buitenlanders",            },
            { "en":"Age distribution:",                      "de":"Altersstruktur:",                           "nl":"Leeftijdsopbouw:",          },
            {                                                "de":"Stadtteile",                                "nl":"wijken"},
            {                                                "de":"[[Stadtbezirk]]e",                          "nl":"deelgemeenten"},
            { "en":"Independent",                            "de":"Parteilos",                                 "nl":"geen partij"},
            { "en":"Region",                                 "de":"[[Region]]",                                "nl":"Landstreek"},
            

        ],
        "includes": ["images", "geography"],
    },
    
    # translations for cities in Germany
    "city-de": {
        "translations": [
            { "en":"[[Bundesland]]:",          "de":"[[Bundesland]]:",                      "nl":"[[Deelstaat (Duitsland)|Deelstaat]]",     },
            { "en":"[[Regierungsbezirk]]:",    "de":"[[Regierungsbezirk]]:",                "nl":"[[Regierungsbezirk]]:",                   },
            { "en":"[[District]]:",            "de":"[[Landkreis|Kreis]]:",                 "nl":"[[District]]",                            },
            { "en":"[[District]]:",            "de":"[[Landkreis]]:",                       "nl":"[[District]]",                            },
            { "en":"district-free town",       "de":"[[kreisfreie Stadt]]",                 "nl":"[[stadsdistrict]]",                       },
            { "en":"District-free town",       "de":"[[Kreisfreie Stadt]]",                 "nl":"[[Stadsdistrict]]",                       },
            { "en":"[[Municipality key]]:",    "de":"[[Amtliche Gemeindekennzahl]]:", },
            { "en":"[[Municipality key]]:",    "de":u"[[Amtlicher Gemeindeschl\xFCssel]]:",                                              },
            { "en":"urban districts",          "de":"[[Stadtbezirk]]e",                     "nl":"stadsdelen",                                             },
            # female first mayor, no exact translation in en:
            { "en":"[[Mayor]]:",               "de":u"[[Oberb\xFCrgermeisterin]]:",         "nl":"[[Burgermeester]]:"},
            { "en":"[[Mayor]]:",               "de":u"[[Oberb\xFCrgermeister]]in:",         "nl":"[[Burgermeester]]:"},
            # male first mayor, no exact translation in en:
            { "en":"[[Mayor]]:",               "de":u"[[Oberb\xFCrgermeister]]:",           "nl":"[[Burgermeester]]:"},
            # "bis" is used between postal codes
            { "en":" to ",                     "de":" bis ",                                "nl":"t/m"},          
            # parties
            { "en":"[[Christian Democratic Union of Germany|CDU]]", "de":"[[CDU]]",                            "nl":"[[Christlich Demokratische Union|CDU]]"},
            { "en":"[[Social Democratic Party of Germany|SPD]]", "de":"[[SPD]]",                               "nl":"[[Sozialdemokratische Partei Deutschlands|SPD]]"},
            { "en":"[[Christian Social Union in Bavaria|CSU]]", "de":"[[CSU]]",                                "nl":"[[CSU]]"},
            { "en":"[[Free Democratic Party of Germany|FDP]]", "de":"[[FDP (Deutschland)|FDP]]",               "nl":"[[FDP]]"},
            { "en":u"[[German Green Party|Bündnis 90/Die Gr\xFCnen]]", "de":u"[[Bündnis 90/Die Gr\xFCnen]]",   "nl":u"[[Die Gr\xFCnen]]"},
            # Bundeslaender
            { "en":"[[Party of Democratic Socialism|PDS]]",  "de":"[[PDS]]",                                   "nl":"[[PDS]]"},
            { "en":"[[Bavaria]]",               "de":"[[Bayern]]",                          "nl":"[[Beieren]]"},
            { "en":"[[Bremen (state)|Bremen]]", "de":"[[Bremen (Land)|Bremen]]",            "nl":"[[Bremen]]"},
            { "en":"[[Hesse]]",                 "de":"[[Hessen]]",                          "nl":"[[Hessen]]"},
            { "en":"[[Mecklenburg-Western Pomerania]]", "de":"[[Mecklenburg-Vorpommern]]"   "nl":"[[Mecklenburg-Voorpommeren]]"},
            { "en":"[[Lower Saxony]]",          "de":"[[Niedersachsen]]",                   "nl":"[[Nedersaksen]]"},
            { "en":"[[North Rhine-Westphalia]]", "de":"[[Nordrhein-Westfalen]]",            "nl":"[[Noordrijn-Westfalen]]"},
            { "en":"[[Rhineland-Palatinate]]",  "de":"[[Rheinland-Pfalz]]",                 "nl":"[[Rijnland-Palts]]"},
            { "en":"[[Saxony]]",                "de":"[[Sachsen (Bundesland)|Sachsen]]",    "nl":"[[Saksen (deelstaat)|Saksen]]"},
            { "en":"[[Saxony-Anhalt]]",         "de":"[[Sachsen-Anhalt]]",                  "nl":"[[Saksen-Anhalt]]"},
            { "en":"[[Schleswig-Holstein]]",    "de":"[[Schleswig-Holstein]]",              "nl":"[[Sleeswijk-Holstein]]"},
            { "en":"[[Thuringia]]",             "de":u"[[Th\xFCringen]]",                   "nl":u"[[Th\xFCringen]]",},

        ],
        "regexes": {
            "de": {
                # image alt text
                "Deutschlandkarte, (?P<city>.+) markiert":                                                           {"en":"Map of Germany, \g<city> marked", "nl":"Kaart van Duitsland met de locatie van \g<city>", },
                "Karte Deutschlands, (?P<city>.+) markiert":                                                         {"en":"Map of Germany, \g<city> marked", "nl":"Kaart van Duitsland met de locatie van \g<city>", },
                "Karte (?P<city>.+) in Deutschland":                                                                 {"en":"Map of Germany, \g<city> marked", "nl":"Kaart van Duitsland met de locatie van \g<city>", },
                # nl: doesn't want Municipality Number and city council's address
                u"\| +\[\[Amtliche Gemeindekennzahl\]\]\:[ \|\r\n]+[\d -]+[\r\n]+\|[-]+ bgcolor=\"#FFFFFF\"[\r\n]+": {                                        "nl":"", },
                # maybe you don't want the town hall's postal address
                # u"\| +\[\[Adresse der (Stadt|Gemeinde)verwaltung\: \|\| [\d -]+[\r\n]+\|-+ bgcolor=\"#FFFFFF\"[\r\n]+":      },
            },
        },
        "includes": ["city", "months"],
        
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
        "regexes": {
            "fr": {
                "\[\[[aA]rrondissements (des |du |de la |de l\'|d\'|de )":  {"de":u"[[Arrondissemens im D\xE9partement ", },
                "\[\[[cC]ommunes (des |du |de la |de l\'|d\'|de )":         {"de":u"[[Kommunen im D\xE9partement ",       },
                "\[\[[cC]antons (des |du |de la|de l\'|d\'|de )":           {"de":u"[[Kantone im D\xE9partement ",        },
                "Blason (des |du |de la |de l\'|d\'|de )":                  {"de":"Wappen von ",                          },
            },  
        },
        "includes": ["numbers", "images", "geography"],
    },          
}

import wikipedia, string, re

class Global:
    debug = False

# prints text on the screen only if in -debug mode
def print_debug(text):
    if Global.debug:
        print text

# Translate the string given as argument 'text' from language 'from_lang' to 
# language 'to_lang', using translation list 'type' in above dictionary.
# if debug_mode=True, status messages are displayed.
def translate(text, type, from_lang, debug_mode=False, to_lang=wikipedia.mylang):
    if debug_mode:
        Global.debug = True
    if type == "":
        return text
    else:
        print_debug("\n Translating type " + type)
        # check if the translation database knows this type of table
        if not types.has_key(type):
            print "Unknown table type: " + type
            return
        if types.get(type).has_key("translations"):
            print_debug("\nDirect translations for type " + type + "\n")
            for item in types.get(type).get("translations"):
                # check if the translation database includes the source language
                if not item.has_key(from_lang):
                    print_debug(from_lang + " translation for item not found in translation table, skipping item")
                    continue
                # if it's necessary to replace a substring
                if string.find(text, item.get(from_lang)) > -1:
                     # check if the translation database includes the target language
                     if not item.has_key(wikipedia.mylang):
                         print_debug("Can't translate \"" + item.get(from_lang) + "\". Please make sure that there is a translation in copy_table.py.")
                     else:
                         print_debug(item.get(from_lang) + " => " + item.get(wikipedia.mylang))
                         # translate a substring
                         text = string.replace(text, item.get(from_lang), item.get(wikipedia.mylang))
        if types.get(type).has_key("regexes"):
            # work on regular expressions
            print_debug("\nWorking on regular expressions for type " + type + "\n")
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
                text = translate(text, inc, from_lang, debug_mode, to_lang)
        return text
