#coding: iso-8859-1
"""
This file is not runnable, but it only consists of various
lists which are required by some other programs.
"""
#
# (C) Rob W.W. Hooft, 2003
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
#

# date formats for various languages, required for interwiki.py with the -days argument
date_format = {
    1: { 'sl':'%d. januar',    'it':'%d gennaio',   'en':'January %d',   'de':'%d. Januar',    'fr':'%d janvier',         'af':'01-%02d', 'ca':'%d de gener',       'oc':'%d de geni%%C3%%A8r',  'nl':'%d januari',   'bg':'%d януари'        },
    2: { 'sl':'%d. februar',   'it':'%d febbraio',  'en':'February %d',  'de':'%d. Februar',   'fr':'%d f&eacute;vrier',  'af':'02-%02d', 'ca':'%d de febrer',      'oc':'%d de febri%%C3%%A8r', 'nl':'%d februari',  'bg':'%d Февруари',   },
    3: { 'sl':'%d. marec',     'it':'%d marzo',     'en':'March %d',     'de':'%d. M&auml;rz', 'fr':'%d mars',            'af':'03-%02d', 'ca':'%d de_mar%%C3%%A7', 'oc':'%d de_mar%%C3%%A7',    'nl':'%d maart',     'bg':'%d Март',           },
    4: { 'sl':'%d. april',     'it':'%d aprile',    'en':'April %d',     'de':'%d. April',     'fr':'%d avril',           'af':'04-%02d', 'ca':'%d d\'abril',       'oc':'%d d\'abril',          'nl':'%d april',     'bg':'%d Април',         },
    5: { 'sl':'%d. maj',       'it':'%d maggio',    'en':'May %d',       'de':'%d. Mai',       'fr':'%d mai',             'af':'05-%02d', 'ca':'%d de maig',        'oc':'%d de mai',            'nl':'%d mei',       'bg':'%d Май',             },
    6: { 'sl':'%d. junij',     'it':'%d giugno',    'en':'June %d',      'de':'%d. Juni',      'fr':'%d juin',            'af':'06-%02d', 'ca':'%d de juny',        'oc':'%d de junh',           'nl':'%d juni',      'bg':'%d Юни',             },
    7: { 'sl':'%d. julij',     'it':'%d luglio',    'en':'July %d',      'de':'%d. Juli',      'fr':'%d juillet',         'af':'07-%02d', 'ca':'%d de juliol',      'oc':'%d de julhet',         'nl':'%d juli',      'bg':'%d Юли',             },
    8: { 'sl':'%d. avgust',    'it':'%d agosto',    'en':'August %d',    'de':'%d. August',    'fr':'%d ao&ucirc;t',      'af':'08-%02d', 'ca':'%d d\'agost',       'oc':'%d d\'agost',          'nl':'%d augustus',  'bg':'%d Август',       },
    9: { 'sl':'%d. september', 'it':'%d settembre', 'en':'September %d', 'de':'%d. September', 'fr':'%d septembre',       'af':'09-%02d', 'ca':'%d de setembre',    'oc':'%d de setembre',       'nl':'%d september', 'bg':'%d Септември', },
    10:{ 'sl':'%d. oktober',   'it':'%d ottobre',   'en':'October %d',   'de':'%d. Oktober',   'fr':'%d octobre',         'af':'10-%02d', 'ca':'%d d\'octubre',     'oc':'%d d\'octobre',        'nl':'%d oktober',   'bg':'%d Октомври',   },
    11:{ 'sl':'%d. november',  'it':'%d novembre',  'en':'November %d',  'de':'%d. November',  'fr':'%d novembre',        'af':'11-%02d', 'ca':'%d de novembre',    'oc':'%d de novembre',       'nl':'%d november',  'bg':'%d Ноември',     },
    12:{ 'sl':'%d. december',  'it':'%d dicembre',  'en':'December %d',  'de':'%d. Dezember',  'fr':'%d d&eacute;cembre', 'af':'12-%02d', 'ca':'%d de desembre',    'oc':'%d de decembre',       'nl':'%d december',  'bg':'%d Декември',   },
    }

class FormatDate:
    def __init__(self, code):
        self.code = code

    def __call__(self, m, d):
        import wikipedia
        return wikipedia.html2unicode((date_format[m][self.code]) % d,
                                      language = self.code)
    
# number of days in each month, required for interwiki.py with the -days argument
days_in_month = {
    1:  31,
    2:  29,
    3:  31,
    4:  30,
    5:  31,
    6:  30,
    7:  31,
    8:  31,
    9:  30,
    10: 31,
    11: 30,
    12: 31
    }

# format for dates B.C., required for interwiki.py with the -years argument and for titletranslate.py
yearBCfmt = {'da':'%d f.Kr.',
             'de':'%d v. Chr.',
             'en':'%d BC',
             'fr':'-%d',
             'pl':'%d p.n.e.',
             'es':'%d adC',
             'eo':'-%d',
             'nl':'%d v. Chr.'} # No default

# format for dates A.D., required for interwiki.py with the -years argument
# if a language is not listed here, interwiki.py assumes '%d' as the date format.
yearADfmt = {'ja':'%d&#24180;',
             'zh':'%d&#24180;',
             'ko':'%d&#45380;'
            }
             
             
# date format translation list required for titletranslate.py and for pagelist.py
datetable = {'nl':
             {
    'januari':{  'sl':'%d. januar',    'it':'%d gennaio',   'en':'January %d',   'de':'%d. Januar',    'fr':'%d janvier',   'af':'01-%02d', 'ca':'%d de gener',       'oc':'%d de geni%%C3%%A8r',  },
    'februari':{ 'sl':'%d. februar',   'it':'%d febbraio',  'en':'February %d',  'de':'%d. Februar',   'fr':'%d fevrier',   'af':'02-%02d', 'ca':'%d de febrer',      'oc':'%d de febri%%C3%%A8r', },
    'maart':{    'sl':'%d. marec',     'it':'%d marzo',     'en':'March %d',     'de':'%d. M&auml;rz', 'fr':'%d mars',      'af':'03-%02d', 'ca':'%d de_mar%%C3%%A7', 'oc':'%d de_mar%%C3%%A7',    },
    'april':{    'sl':'%d. april',     'it':'%d aprile',    'en':'April %d',     'de':'%d. April',     'fr':'%d avril',     'af':'04-%02d', 'ca':'%d d\'abril',       'oc':'%d d\'abril',          },
    'mei':{      'sl':'%d. maj',       'it':'%d maggio',    'en':'May %d',       'de':'%d. Mai',       'fr':'%d mai',       'af':'05-%02d', 'ca':'%d de maig',        'oc':'%d de mai',            },
    'juni':{     'sl':'%d. junij',     'it':'%d giugno',    'en':'June %d',      'de':'%d. Juni',      'fr':'%d juin',      'af':'06-%02d', 'ca':'%d de juny',        'oc':'%d de junh',           },
    'juli':{     'sl':'%d. julij',     'it':'%d luglio',    'en':'July %d',      'de':'%d. Juli',      'fr':'%d juillet',   'af':'07-%02d', 'ca':'%d de juliol',      'oc':'%d de julhet',         },
    'augustus':{ 'sl':'%d. avgust',    'it':'%d agosto',    'en':'August %d',    'de':'%d. August',    'fr':'%d aout',      'af':'08-%02d', 'ca':'%d d\'agost',       'oc':'%d d\'agost',          },
    'september':{'sl':'%d. september', 'it':'%d settembre', 'en':'September %d', 'de':'%d. September', 'fr':'%d septembre', 'af':'09-%02d', 'ca':'%d de setembre',    'oc':'%d de setembre',       },
    'oktober':{  'sl':'%d. oktober',   'it':'%d ottobre',   'en':'October %d',   'de':'%d. Oktober',   'fr':'%d octobre',   'af':'10-%02d', 'ca':'%d d\'octubre',     'oc':'%d d\'octobre',        },
    'november':{ 'sl':'%d. november',  'it':'%d novembre',  'en':'November %d',  'de':'%d. November',  'fr':'%d novembre',  'af':'11-%02d', 'ca':'%d de novembre',    'oc':'%d de novembre',       },
    'december':{ 'sl':'%d. december',  'it':'%d dicembre',  'en':'December %d',  'de':'%d. Dezember',  'fr':'%d decembre',  'af':'12-%02d', 'ca':'%d de desembre',    'oc':'%d de decembre',       },
    }}
