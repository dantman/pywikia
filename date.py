#coding: utf-8
"""
This file is not runnable, but it only consists of various
lists which are required by some other programs.
"""
#
# © Rob W.W. Hooft, 2003
# © Daniel Herding, 2004
# © Ævar Arnfjörð Bjarmason, 2004
#
# Distribute under the terms of the PSF license.
#

# date formats for various languages, required for interwiki.py with the -days argument
date_format = {
	1: { 
		'sl':'%d. januar',
		'it':'%d gennaio',
		'en':'January %d',
		'de':'%d. Januar',
		'fr':'%d janvier',
		'af':'%d Januarie',
		'ca':'%d de gener',
		'oc':'%d de geni%%C3%%A8r',
		'nl':'%d januari',
		'bg':'%d януари',
		'is':'%d. janúar',
		'fo':'%d. januar',
                'eo':'%d-a de januaro',
                'pt':'%d de Janeiro',
                'ast':'%d de xineru',
                'es':'%d de enero'
	},
	2: {
		'sl':'%d. februar',
		'it':'%d febbraio',
		'en':'February %d',
		'de':'%d. Februar',
		'fr':'%d février',
		'af':'%d Februarie',
		'ca':'%d de febrer',
		'oc':'%d de febri%%C3%%A8r',
		'nl':'%d februari',
		'bg':'%d Февруари',
		'is':'%d. febrúar',
		'fo':'%d. februar',
                'eo':'%d-a de februaro',
                'pt':'%d de Fevereiro',
                'ast':'%d de febreru',
                'es':'%d de febrero'
	},
	3: {
		'sl':'%d. marec',
		'it':'%d marzo',
		'en':'March %d',
		'de':'%d. März',
		'fr':'%d mars',
		'af':'%d Maart',
		'ca':'%d de_mar%%C3%%A7',
		'oc':'%d de_mar%%C3%%A7',
		'nl':'%d maart',
		'bg':'%d Март',
		'is':'%d. mars',
		'fo':'%d. mars',
                'eo':'%d-a de marto',
                'pt':'%d de Março',
                'ast':'%d de marzu',
                'es':'%d de marzo'
	},
	4: {
		'sl':'%d. april',
		'it':'%d aprile',
		'en':'April %d',
		'de':'%d. April',
		'fr':'%d avril',
		'af':'%d April',
		'ca':'%d d\'abril',
		'oc':'%d d\'abril',
		'nl':'%d april',
		'bg':'%d Април',
		'is':'%d. apríl',
		'fo':'%d. apríl',
                'eo':'%d-a de aprilo',
                'pt':'%d de Abril',
                'ast':"%d d'abril",
                'es':'%d de abril'
	},
	5: {
		'sl':'%d. maj',
		'it':'%d maggio',
		'en':'May %d',
		'de':'%d. Mai',
		'fr':'%d mai',
		'af':'%d Mei',
		'ca':'%d de maig',
		'oc':'%d de mai',
		'nl':'%d mei',
		'bg':'%d Май',
		'is':'%d. maí',
		'fo':'%d. mai',
                'eo':'%d-a de majo',
                'pt':'%d de Maio',
                'ast':'%d de mayu',
                'es':'%d de mayo'
	},
	6: {
		'sl':'%d. junij',
		'it':'%d giugno',
		'en':'June %d',
		'de':'%d. Juni',
		'fr':'%d juin',
		'af':'%d Junie',
		'ca':'%d de juny',
		'oc':'%d de junh',
		'nl':'%d juni',
		'bg':'%d Юни',
		'is':'%d. júní',
		'fo':'%d. juni',
                'eo':'%d-a de junio',
                'pt':'%d de Junho',
                'ast':'%d de xunu',
                'es':'%d de junio'
	},
	7: {
		'sl':'%d. julij',
		'it':'%d luglio',
		'en':'July %d',
		'de':'%d. Juli',
		'fr':'%d juillet',
		'af':'%d Julie',
		'ca':'%d de juliol',
		'oc':'%d de julhet',
		'nl':'%d juli',
		'bg':'%d Юли',
		'is':'%d. júlí',
		'fo':'%d. juli',
                'eo':'%d-a de julio',
                'pt':'%d de Julho',
                'ast':'%d de xunetu',
                'es':'%d de julio'
	},
	8: {
		'sl':'%d. avgust',
		'it':'%d agosto',
		'en':'August %d',
		'de':'%d. August',
		'fr':'%d août',
		'af':'%d Augustus',
		'ca':'%d d\'agost',
		'oc':'%d d\'agost',
		'nl':'%d augustus',
		'bg':'%d Август',
		'is':'%d. ágúst',
		'fo':'%d. august',
                'eo':'%d-a de aŭgusto',
                'pt':'%d de Agosto',
                'ast':"%d d'agostu",
                'es':'%d de agosto'
	},
	9: {
		'sl':'%d. september',
		'it':'%d settembre',
		'en':'September %d',
		'de':'%d. September',
		'fr':'%d septembre',
		'af':'%d September',
		'ca':'%d de setembre',
		'oc':'%d de setembre',
		'nl':'%d september',
		'bg':'%d Септември',
		'is':'%d. september',
		'fo':'%d. september',
                'eo':'%d-a de septembro',
                'pt':'%d de Setembro',
                'ast':'%d de setiembre',
                'es':'%d de septiembre'
	},
	10:{
		'sl':'%d. oktober',
		'it':'%d ottobre',
		'en':'October %d',
		'de':'%d. Oktober',
		'fr':'%d octobre',
		'af':'%d Oktober',
		'ca':'%d d\'octubre',
		'oc':'%d d\'octobre',
		'nl':'%d oktober',
		'bg':'%d Октомври',
		'is':'%d. október',
		'fo':'%d. oktober',
                'eo':'%d-a de oktobro',
                'pt':'%d de Outubro',
                'ast':"%d d'ochobre",
                'es':'%d de octubre'
	},
	11:{
		'sl':'%d. november',
		'it':'%d novembre',
		'en':'November %d',
		'de':'%d. November',
		'fr':'%d novembre',
		'af':'%d November',
		'ca':'%d de novembre',
		'oc':'%d de novembre',
		'nl':'%d november',
		'bg':'%d Ноември',
		'is':'%d. nóvember',
		'fo':'%d. november',
                'eo':'%d-a de novembro',
                'pt':'%d de Novembro',
                'ast':'%d de payares',
                'es':'%d de noviembre'
	},
	12:{
		'sl':'%d. december',
		'it':'%d dicembre',
		'en':'December %d',
		'de':'%d. Dezember',
		'fr':'%d décembre',
		'af':'%d Desember',
		'ca':'%d de desembre',
		'oc':'%d de decembre',
		'nl':'%d december',
		'bg':'%d Декември',
		'is':'%d. desember',
		'fo':'%d. desember',
                'eo':'%d-a de decembro',
                'pt':'%d de Dezembro',
                'ast':"%d d'avientu",
                'es':'%d de diciembre'
	}
}

class FormatDate(object):
    def __init__(self, site):
        self.site = site

    def __call__(self, m, d):
        import wikipedia
        return wikipedia.html2unicode((date_format[m][self.site.lang]) % d,
                                      site = self.site)
    
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
yearBCfmt = {
                'af':'%d V.C.',
                'bg':'%d &#1075;. &#1087;&#1088;.&#1085;.&#1077;.',
                'bs':'%d p.ne.',
                'ca':'%d aC',
		'da':'%d f.Kr.',
		'de':'%d v. Chr.',
		'en':'%d BC',
		'eo':'-%d',
		'es':'%d adC',
                'et':'%d eKr',
                'fi':'%d eaa',
		'fo':'%d f. Kr.',
		'fr':'-%d',
                'he':'%d &#1500;&#1508;&#1504;&#1492;"&#1505;',
                'hr':'%d p.n.e.',
		'is':'%d f. Kr.',
                'it':'%d AC',
                'la':'%d a.C.n',
                'lb':'-%d',
                'nds':'%d v. Chr.',
		'nl':'%d v. Chr.',
                'no':'%d f.Kr.',
		'pl':'%d p.n.e.',
                'pt':'%d a.C.',
                'ru':'%d &#1076;&#1086; &#1085;.&#1101;.',
                'sr':'%d. &#1087;&#1085;&#1077;.',
                'sv':'%d f.Kr.',
                'zh':'&#21069;%d&#24180;'
} # No default

# For all languages the maximal value a year BC can have; before this date the
# language switches to decades or centuries
maxyearBC = {
                'ca':500,
		'de':400,
		'en':499,
		'nl':1000,
		'pl':776
            }

# format for dates A.D., required for interwiki.py with the -years argument
# if a language is not listed here, interwiki.py assumes '%d' as the date format.
yearADfmt = {
		'ja':'%d&#24180;',
		'zh':'%d&#24180;',
		'ko':'%d&#45380;',
                'minnan':'%d n&icirc;',
                'ur':'%d&#1587;&#1576;&#1605;'
}
             
             
# date format translation list required for titletranslate.py and for pagelist.py
datetable = {
	'nl':{
		'januari':1,
                'februari':2,
		'maart':3,
		'april':4,
		'mei':5,
		'juni':6,
		'juli':7,
		'augustus':8,
		'september':9,
		'oktober':10,
		'november':11,
		'december':12
        },
}

