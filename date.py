# -*- coding: utf-8  -*-
"""
This file is not runnable, but it only consists of various
lists which are required by some other programs.
"""
#
# © Rob W.W. Hooft, 2003
# © Daniel Herding, 2004
# © Ævar Arnfjörð Bjarmason, 2004
# © Andre Engels, 2005
# © Yuri Astrakhan, 2005
#
# Distribute under the terms of the PSF license.
#

# used for date recognition
import types
import re


# date formats for various languages, required for interwiki.py with the -days argument
date_format = {
    1: { 
        'af':u'%d Januarie',
        'ang':u'%d Æfterra Géola',
        'ar':u'%d يناير',
        'ast':u'%d de xineru',
        'be':u'%d студзеня',
        'bg':u'%d януари',
        'bs':u'%d. januar',
        'ca':u'%d de gener',
        'cs':u'%d. leden',
        'csb':u'%d stëcznika',
        'cy':u'%d Ionawr',
        'da':u'%d. januar',
        'de':u'%d. Januar',
        'el':u'%d Ιανουαρίου',
        'en':u'January %d',
        'eo':u'%d-a de januaro',
        'es':u'%d de enero',
        'et':u'%d. jaanuar',
        'eu':u'Urtarrilaren %d',
        'fi':u'%d. tammikuuta',
        'fo':u'%d. januar',
        'fr':u'%d janvier',
        'fy':u'%d jannewaris',
        'ga':u'%d Eanáir',
        'gl':u'%d de xaneiro',
        'he':u'%d בינואר',
        'hr':u'%d. siječnja',
        'hu':u'Január %d',
        'ia':u'%d de januario',
        'id':u'%d Januari',
        'ie':u'%d januar', # not all months for ie added yet
        'io':u'%d di januaro',
        'is':u'%d. janúar',
        'it':u'%d gennaio',
        'ja':u'1月%d日',
        'ka':u'%d იანვარი', # ka only January and December added for now
        'ko':u'1월 %d일',
        'ku':u"%d'ê rêbendanê",
        'la':u'%d Ianuarii',
        'lb':u'%d. Januar',
        'lt':u'Sausio %d',
        'ml':u'ജനുവരി %d',
        'nds':u'%d Januar',
        'nl':u'%d januari',
        'nn':u'%d. januar',
        'no':u'%d. januar',
        'oc':u'%d de geni%%C3%%A8r',
        'pl':u'%d stycznia',
        'pt':u'%d de Janeiro',
        'ro':u'%d ianuarie',
        'ru':u'%d января',
        'sk':u'%d. január',
        'sl':u'%d. januar',
        'sr':u'%d. јануар',
        'sv':u'%d januari',
        'tl':u'Enero %d',
        'tr':u'%d Ocak',
        'tt':u'%d. Ğínwar',
        'uk':u'%d січня',
        'ur':u'%d جنوری',
        'vi':u'%d tháng 1',
        'wa':u"%d di djanvî", # Walloon names depend on the day number; taking the most common form
        'zh':u'1月%d日'
    },
    2: {
        'af':u'%d Februarie',
        'ang':u'%d Solmónaþ',
        'ar':u'%d فبراير',
        'ast':u'%d de febreru',
        'be':u'%d лютага',
        'bg':u'%d февруари',
        'bs':u'Februar %d',
        'ca':u'%d de febrer',
        'cs':u'%d. únor',
        'csb':u'%d gromicznika',
        'cy':u'%d Chwefror',
        'da':u'%d. februar',
        'de':u'%d. Februar',
        'el':u'%d Φεβρουαρίου',
        'en':u'February %d',
        'eo':u'%d-a de februaro',
        'es':u'%d de febrero',
        'et':u'%d. veebruar',
        'eu':u'Ottsailaren %d',
        'fi':u'%d. helmikuuta',
        'fo':u'%d. februar',
        'fr':u'%d février',
        'fy':u'%d febrewaris',
        'ga':u'%d Feabhra',
        'gl':u'%d de febreiro',
        'he':u'%d בפברואר',
        'hr':u'%d. veljače',
        'hu':u'Február %d',
        'ia':u'%d de februario',
        'id':u'%d Februari',
        'io':u'%d di februaro',
        'is':u'%d. febrúar',
        'it':u'%d febbraio',
        'ja':u'2月%d日',
        'ko':u'2월 %d일',
        'ku':u"%d'ê reşemiyê",
        'la':u'%d Februarii',
        'lb':u'%d. Februar',
        'lt':u'Vasario %d',
        'ml':u'ഫെബ്രുവരി %d',
        'nds':u'%d Februar',
        'nl':u'%d februari',
        'nn':u'%d. februar',
        'no':u'%d. februar',
        'oc':u'%d de febri%%C3%%A8r',
        'pl':u'%d lutego',
        'pt':u'%d de Fevereiro',
        'ro':u'%d februarie',
        'ru':u'%d февраля',
        'sk':u'%d. február',
        'sl':u'%d. februar',
        'sr':u'%d. фебруар',
        'sv':u'%d februari',
        'tl':u'Pebrero %d',
        'tr':u'%d Şubat',
        'tt':u'%d. Febräl',
        'uk':u'%d лютого',
        'ur':u'%d فروری',
        'vi':u'%d tháng 2',
        'wa':u"%d di fevrî",
        'zh':u'2月%d日'
    },
    3: {
        'af':u'%d Maart',
        'ang':u'%d Hréþmónaþ',
        'ar':u'%d مارس',
        'ast':u'%d de marzu',
        'be':u'%d сакавіка',
        'bg':u'%d март',
        'bs':u'Mart %d',
        'ca':u'%d de_mar%%C3%%A7',
        'cs':u'%d. březen',
        'csb':u'%d strumiannika',
        'cy':u'%d Mawrth',
        'da':u'%d. marts',
        'de':u'%d. März',
        'en':u'March %d',
        'el':u'%d Μαρτίου',
        'eo':u'%d-a de marto',
        'es':u'%d de marzo',
        'et':u'%d. märts',
        'eu':u'Martxoaren %d',
        'fi':u'%d. maaliskuuta',
        'fo':u'%d. mars',
        'fr':u'%d mars',
        'fy':u'%d maart',
        'ga':u'%d Márta',
        'gl':u'%d de marzo',
        'he':u'%d במרץ',
        'hr':u'%d. ožujka',
        'hu':u'Március %d',
        'ia':u'%d de martio',
        'id':u'%d Maret',
        'io':u'%d di marto',
        'is':u'%d. mars',
        'it':u'%d marzo',
        'ja':u'3月%d日',
        'ko':u'3월 %d일',
        'ku':u"%d'ê adarê",
        'la':u'%d Martii',
        'lb':u'%d. Mäerz',
        'lt':u'Kovo %d',
        'ml':u'മാര്ച് %d',
        'nds':u'%d März',
        'nl':u'%d maart',
        'nn':u'%d. mars',
        'no':u'%d. mars',
        'oc':u'%d de_mar%%C3%%A7',
        'pl':u'%d marca',
        'pt':u'%d de Março',
        'ro':u'%d martie',
        'ru':u'%d марта',
        'sk':u'%d. marec',
        'sl':u'%d. marec',
        'sr':u'%d. март',
        'sv':u'%d mars',
        'tl':u'Marso %d',
        'tr':u'%d Mart',
        'tt':u'%d. Mart',
        'uk':u'%d березня',
        'ur':u'%d مارچ',
        'vi':u'%d tháng 3',
        'wa':u"%d di måss",
        'zh':u'3月%d日'
    },
    4: {
        'af':u'%d April',
        'ang':u'%d Éastermónaþ',
        'ar':u'%d أبريل',
        'ast':u"%d d'abril",
        'be':u'%d красавіка',
        'bg':u'%d април',
        'bs':u'April %d',
        'ca':u"%d d'abril",
        'cs':u'%d. duben',
        'csb':u'%d łżëkwiôta',
        'cy':u'%d Ebrill',
        'da':u'%d. april',
        'de':u'%d. April',
        'el':u'%d Απριλίου',
        'en':u'April %d',
        'eo':u'%d-a de aprilo',
        'es':u'%d de abril',
        'et':u'%d. aprill',
        'eu':u'Aprilaren %d',
        'fi':u'%d. huhtikuuta',
        'fo':u'%d. apríl',
        'fr':u'%d avril',
        'fy':u'%d april',
        'ga':u'%d Aibreán',
        'gl':u'%d de abril',
        'he':u'%d באפריל',
        'hr':u'%d. travnja',
        'hu':u'Április %d',
        'ia':u'%d de april',
        'id':u'%d April',
        'ie':u'%d april',
        'io':u'%d di aprilo',
        'is':u'%d. apríl',
        'it':u'%d aprile',
        'ja':u'4月%d日',
        'ko':u'4월 %d일',
        'ku':u"%d'ê avrêlê",
        'la':u'%d Aprilis',
        'lb':u'%d. Abrëll',
        'lt':u'Balandžio %d',
        'ml':u'ഏപ്രില് %d',
        'nds':u'%d April',
        'nl':u'%d april',
        'nn':u'%d. april',
        'no':u'%d. april',
        'oc':u"%d d'abril",
        'pl':u'%d kwietnia',
        'pt':u'%d de Abril',
        'ro':u'%d aprilie',
        'ru':u'%d апреля',
        'sk':u'%d. apríl',
        'sl':u'%d. april',
        'sr':u'%d. април',
        'sv':u'%d april',
        'tl':u'Abríl %d',
        'tr':u'%d Nisan',
        'tt':u'%d. Äpril',
        'uk':u'%d квітня',
        'ur':u'%d اپریل',
        'vi':u'%d tháng 4',
        'wa':u"%d di avri",
        'zh':u'4月%d日'
    },
    5: {
        'af':u'%d Mei',
        'ang':u'%d Þrimilcemónaþ',
        'ar':u'%d مايو',
        'ast':u'%d de mayu',
        'be':u'%d траўня',
        'bg':u'%d май',
        'bs':u'Maj %d',
        'ca':u'%d de maig',
        'cs':u'%d. květen',
        'csb':u'%d môja',
        'cy':u'%d Mai',
        'da':u'%d. maj',
        'el':u'%d Μαΐου',
        'en':u'May %d',
        'et':u'%d. mai',
        'eu':u'Maiatzaren %d',
        'de':u'%d. Mai',
        'eo':u'%d-a de majo',
        'es':u'%d de mayo',
        'fi':u'%d. toukokuuta',
        'fo':u'%d. mai',
        'fr':u'%d mai',
        'fy':u'%d maaie',
        'ga':u'%d Bealtaine',
        'gl':u'%d de maio',
        'he':u'%d במאי',
        'hr':u'%d. svibnja',
        'hu':u'Május %d',
        'ia':u'%d de maio',
        'id':u'%d Mei',
        'ie':u'%d may',
        'io':u'%d di mayo',
        'is':u'%d. maí',
        'it':u'%d maggio',
        'ja':u'5月%d日',
        'ko':u'5월 %d일',
        'ku':u"%d'ê gulanê",
        'la':u'%d Maii',
        'lb':u'%d. Mee',
        'lt':u'Gegužės %d',
        'ml':u'മേയ് %d',
        'nds':u'%d Mai',
        'nl':u'%d mei',
        'nn':u'%d. mai',
        'no':u'%d. mai',
        'oc':u'%d de mai',
        'pl':u'%d maja',
        'pt':u'%d de Maio',
        'ro':u'%d mai',
        'ru':u'%d мая',
        'sk':u'%d. máj',
        'sl':u'%d. maj',
        'sr':u'%d. мај',
        'sv':u'%d maj',
        'tl':u'Mayo %d',
        'tr':u'%d Mayıs',
        'tt':u'%d. May',
        'uk':u'%d травня',
        'ur':u'%d مئ',
        'vi':u'%d tháng 5',
        'wa':u"%d di may",
        'zh':u'5月%d日'
    },
    6: {
        'af':u'%d Junie',
        'ang':u'%d Séremónaþ',
        'ar':u'%d يونيو',
        'ast':u'%d de xunu',
        'be':u'%d чэрвеня',
        'bg':u'%d юни',
        'bs':u'Jun %d',
        'ca':u'%d de juny',
        'cs':u'%d. červen',
        'csb':u'%d czerwińca',
        'cy':u'%d Mehefin',
        'da':u'%d. juni',
        'de':u'%d. Juni',
        'el':u'%d Ιουνίου',
        'en':u'June %d',
        'eo':u'%d-a de junio',
        'es':u'%d de junio',
        'et':u'%d. juuni',
        'eu':u'Ekainaren %d',
        'fi':u'%d. kesäkuuta',
        'fo':u'%d. juni',
        'fr':u'%d juin',
        'fy':u'%d juny',
        'ga':u'%d Meitheamh',
        'gl':u'%d de xuño',
        'he':u'%d ביוני',
        'hr':u'%d. lipnja',
        'hu':u'Június %d',
        'ia':u'%d de junio',
        'id':u'%d Juni',
        'io':u'%d di junio',
        'is':u'%d. júní',
        'it':u'%d giugno',
        'ja':u'6月%d日',
        'ko':u'6월 %d일',
        'ku':u"%d'ê pûşperê",
        'la':u'%d Iunii',
        'lb':u'%d. Juni',
        'lt':u'Birželio %d',
        'ml':u'ജൂണ്‍ %d',
        'nds':u'%d Juni',
        'nl':u'%d juni',
        'nn':u'%d. juni',
        'no':u'%d. juni',
        'oc':u'%d de junh',
        'pl':u'%d czerwca',
        'pt':u'%d de Junho',
        'ro':u'%d iunie',
        'ru':u'%d июня',
        'sk':u'%d. jún',
        'sl':u'%d. junij',
        'sr':u'%d. јун',
        'sv':u'%d juni',
        'tl':u'Hunyo %d',
        'tr':u'%d Haziran',
        'tt':u'%d. Yün',
        'uk':u'%d червня',
        'ur':u'%d جون',
        'vi':u'%d tháng 6',
        'wa':u"%d di djun",
        'zh':u'6月%d日'
    },
    7: {
        'af':u'%d Julie',
        'ang':u'%d Mǽdmónaþ',
        'ar':u'%d يوليو',
        'ast':u'%d de xunetu',
        'be':u'%d ліпеня',
        'bg':u'%d юли',
        'bs':u'Jul %d',
        'ca':u'%d de juliol',
        'cs':u'%d. červenec',
        'csb':u'%d lëpinca',
        'cy':u'%d Gorffenaf',
        'da':u'%d. juli',
        'de':u'%d. Juli',
        'en':u'July %d',
        'el':u'%d Ιουλίου',
        'eo':u'%d-a de julio',
        'es':u'%d de julio',
        'et':u'%d. juuli',
        'eu':u'Uztailaren %d',
        'fi':u'%d. heinäkuuta',
        'fo':u'%d. juli',
        'fr':u'%d juillet',
        'fy':u'%d july',
        'ga':u'%d Iúil',
        'gl':u'%d de xullo',
        'he':u'%d ביולי',
        'hr':u'%d. srpnja',
        'hu':u'Július %d',
        'ia':u'%d de julio',
        'id':u'%d Juli',
        'io':u'%d di julio',
        'is':u'%d. júlí',
        'it':u'%d luglio',
        'ja':u'7月%d日',
        'ko':u'7월 %d일',
        'ku':u"%d'ê tîrmehê",
        'la':u'%d Iulii',
        'lb':u'%d. Juli',
        'lt':u'Liepos %d',
        'ml':u'ജൂലൈ %d',
        'nds':u'%d Juli',
        'nl':u'%d juli',
        'nn':u'%d. juli',
        'no':u'%d. juli',
        'oc':u'%d de julhet',
        'pl':u'%d lipca',
        'pt':u'%d de Julho',
        'ro':u'%d iulie',
        'ru':u'%d июля',
        'sk':u'%d. júl',
        'sl':u'%d. julij',
        'sr':u'%d. јул',
        'sv':u'%d juli',
        'tl':u'Hulyo %d',
        'tr':u'%d Temmuz',
        'tt':u'%d Yül',
        'uk':u'%d липня',
        'ur':u'%d جلائ',
        'vi':u'%d tháng 7',
        'wa':u"%d di djulete",
        'zh':u'7月%d日'
    },
    8: {
        'af':u'%d Augustus',
        'ang':u'%d Wéodmónaþ',
        'ar':u'%d أغسطس',
        'ast':u"%d d'agostu",
        'be':u'%d жніўня',
        'bg':u'%d август',
        'bs':u'Avgust %d',
        'ca':u"%d d'agost",
        'cs':u'%d. srpen',
        'csb':u'%d zélnika',
        'cy':u'%d Awst',
        'da':u'%d. august',
            'de':u'%d. August',
        'el':u'%d Αυγούστου',
        'en':u'August %d',
        'eo':u'%d-a de aŭgusto',
        'es':u'%d de agosto',
        'et':u'%d. august',
        'eu':u'Abuztuaren %d',
        'fi':u'%d. elokuuta',
        'fo':u'%d. august',
        'fr':u'%d août',
        'fy':u'%d augustus',
        'ga':u'%d Lúnasa',
        'gl':u'%d de agosto',
        'he':u'%d באוגוסט',
        'hr':u'%d. kolovoza',
        'hu':u'Augusztus %d',
        'ia':u'%d de augusto',
        'id':u'%d Agustus',
        'ie':u'%d august',
        'io':u'%d di agosto',
        'is':u'%d. ágúst',
        'it':u'%d agosto',
        'ja':u'8月%d日',
        'ko':u'8월 %d일',
        'ku':u"%d'ê gelawêjê",
        'la':u'%d Augusti',
        'lb':u'%d. August',
        'lt':u'Rugpjūčio %d',
        'ml':u'ആഗസ്റ്റ്‌ %d',
        'nds':u'%d August',
        'nl':u'%d augustus',
        'nn':u'%d. august',
        'no':u'%d. august',
        'oc':u"%d d'agost",
        'pl':u'%d sierpnia',
        'pt':u'%d de Agosto',
        'ro':u'%d august',
        'ru':u'%d августа',
        'sk':u'%d. august',
        'sl':u'%d. avgust',
        'sr':u'%d. август',
        'sv':u'%d augusti',
        'tl':u'Agosto %d',
        'tr':u'%d Ağustos',
        'tt':u'%d. August',
        'uk':u'%d серпня',
        'ur':u'%d اگست',
        'vi':u'%d tháng 8',
        'wa':u"%d d' awousse",
        'zh':u'8月%d日'
    },
    9: {
        'af':u'%d September',
        'ang':u'%d Háligmónaþ',
        'ar':u'%d سبتمبر',
        'ast':u'%d de setiembre',
        'be':u'%d верасьня',
        'bg':u'%d септември',
        'bs':u'Septembar %d',
        'ca':u'%d de setembre',
        'cs':u'%d. září',
        'csb':u'%d séwnika',
        'cy':u'%d Medi',
        'da':u'%d. september',
        'de':u'%d. September',
        'el':u'%d Σεπτεμβρίου',
        'en':u'September %d',
        'eo':u'%d-a de septembro',
        'es':u'%d de septiembre',
        'et':u'%d. september',
        'eu':u'Irailaren %d',
        'fi':u'%d. syyskuuta',
        'fo':u'%d. september',
        'fr':u'%d septembre',
        'fy':u'%d septimber',
        'ga':u'%d Meán Fómhair',
        'gl':u'%d de setembro',
        'he':u'%d בספטמבר',
        'hr':u'%d. rujna',
        'hu':u'Szeptember %d',
        'ia':u'%d de septembre',
        'id':u'%d September',
        'io':u'%d di septembro',
        'is':u'%d. september',
        'it':u'%d settembre',
        'ja':u'9月%d日',
        'ko':u'9월 %d일',
        'ku':u"%d'ê rezberê",
        'la':u'%d Septembris',
        'lb':u'%d. September',
        'lt':u'Rugsėjo %d',
        'ml':u'സപ്തന്പര് %d',
        'nds':u'%d September',
        'nl':u'%d september',
        'nn':u'%d. september',
        'no':u'%d. september',
        'oc':u'%d de setembre',
        'pl':u'%d września',
        'pt':u'%d de Setembro',
        'ro':u'%d septembrie',
        'ru':u'%d сентября',
        'sk':u'%d. september',
        'sl':u'%d. september',
        'sr':u'%d. септембар',
        'sv':u'%d september',
        'tl':u'Setyembre %d',
        'tr':u'%d Eylül',
        'tt':u'%d. Sentäber',
        'uk':u'%d вересня',
        'ur':u'%d ستمب',
        'vi':u'%d tháng 9',
        'wa':u'%d di setimbe',
        'zh':u'9月%d日'
    },
    10:{
        'af':u'%d Oktober',
        'ang':u'%d Winterfylleþ',
        'ar':u'%d أكتوبر',
        'ast':u"%d d'ochobre",
        'be':u'%d кастрычніка',
        'bg':u'%d октомври',
        'bs':u'Oktobar %d',
        'ca':u"%d d'octubre",
        'cs':u'%d. říjen',
        'csb':u'%d rujana',
        'cy':u'%d Hydref',
        'da':u'%d. oktober',
        'de':u'%d. Oktober',
        'el':u'%d Οκτωβρίου',
        'en':u'October %d',
        'eo':u'%d-a de oktobro',
        'es':u'%d de octubre',
        'et':u'%d. oktoober',
        'eu':u'Urriaren %d',
        'fi':u'%d. lokakuuta',
        'fo':u'%d. oktober',
        'fr':u'%d octobre',
        'fy':u'%d oktober',
        'ga':u'%d Deireadh Fómhair',
        'gl':u'%d de outubro',
        'he':u'%d באוקטובר',
        'hr':u'%d. listopada',
        'hu':u'Október %d',
        'ia':u'%d de octobre',
        'id':u'%d Oktober',
        'io':u'%d di oktobro',
        'is':u'%d. október',
        'it':u'%d ottobre',
        'ja':u'10月%d日',
        'ko':u'10월 %d일',
        'ku':u"%d'ê kewçêrê",
        'la':u'%d Octobris',
        'lb':u'%d. Oktober',
        'lt':u'Spalio %d',
        'ml':u'ഒക്ടോബര് %d',
        'nds':u'%d Oktober',
        'nl':u'%d oktober',
        'nn':u'%d. oktober',
        'no':u'%d. oktober',
        'oc':u"%d d'octobre",
        'pl':u'%d października',
        'pt':u'%d de Outubro',
        'ro':u'%d octombrie',
        'ru':u'%d октября',
        'sk':u'%d. október',
        'sl':u'%d. oktober',
        'sr':u'%d. октобар',
        'sv':u'%d oktober',
        'tl':u'Oktubre %d',
        'tr':u'%d Ekim',
        'tt':u'%d. Öktäber',
        'uk':u'%d жовтня',
        'ur':u'%d اکتوبر',
        'vi':u'%d tháng 10',
        'wa':u"%d d' octôbe",
        'zh':u'10月%d日'
    },
    11:{
        'af':u'%d November',
        'ang':u'%d Blótmónaþ',
        'ar':u'%d نوفمبر',
        'ast':u'%d de payares',
        'be':u'%d лістапада',
        'bg':u'%d ноември',
        'bs':u'Novembar %d',
        'ca':u'%d de novembre',
        'cs':u'%d. listopad',
        'csb':u'%d lëstopadnika',
        'cy':u'%d Tachwedd',
        'da':u'%d. november',
        'de':u'%d. November',
        'el':u'%d Νοεμβρίου',
        'en':u'November %d',
        'eo':u'%d-a de novembro',
        'es':u'%d de noviembre',
        'et':u'%d. november',
        'eu':u'Azaroaren %d',
        'fi':u'%d. marraskuuta',
        'fo':u'%d. november',
        'fr':u'%d novembre',
        'fy':u'%d novimber',
        'ga':u'%d Samhain',
        'gl':u'%d de novembro',
        'he':u'%d בנובמבר',
        'hr':u'%d studenog',
        'hu':u'November %d',
        'ia':u'%d de novembre',
        'id':u'%d November',
        'io':u'%d di novembro',
        'it':u'%d novembre',
        'is':u'%d. nóvember',
        'ja':u'11月%d日',
        'ko':u'11월 %d일',
        'ku':u"%d'ê sermawezê",
        'la':u'%d Novembris',
        'lb':u'%d. November',
        'lt':u'Lapkričio  %d',
        'ml':u'നവന്പര് %d',
        'nds':u'%d November',
        'nl':u'%d november',
        'nn':u'%d. november',
        'no':u'%d. november',
        'oc':u'%d de novembre',
        'pl':u'%d listopada',
        'pt':u'%d de Novembro',
        'ro':u'%d noiembrie',
        'ru':u'%d ноября',
        'sk':u'%d. november',
        'sl':u'%d. november',
        'sr':u'%d. новембар',
        'sv':u'%d november',
        'tl':u'Nobyembre %d',
        'tr':u'%d Kasım',
        'tt':u'%d. Nöyäber',
        'uk':u'%d листопада',
        'ur':u'%d نومب',
        'vi':u'%d tháng 11',
        'wa':u'%d di nôvimbe',
        'zh':u'11月%d日'
    },
    12:{
        'af':u'%d Desember',
        'ang':u'%d Géolmónaþ',
        'ar':u'%d ديسمبر',
        'ast':u"%d d'avientu",
        'be':u'%d сьнежня',
        'bg':u'%d декември',
        'bs':u'Decembar %d',
        'ca':u'%d de desembre',
        'cs':u'%d. prosinec',
        'csb':u'%d gòdnika',
        'cy':u'%d Rhagfyr',
        'da':u'%d. december',
        'de':u'%d. Dezember',
        'el':u'%d Δεκεμβρίου',
        'en':u'December %d',
        'eo':u'%d-a de decembro',
        'es':u'%d de diciembre',
        'et':u'%d. detsember',
        'eu':u'Abenduaren %d',
        'fi':u'%d. joulukuuta',
        'fo':u'%d. desember',
        'fr':u'%d décembre',
        'fy':u'%d desimber',
        'ga':u'%d Mí na Nollag',
        'gl':u'%d de decembro',
        'he':u'%d בדצמבר',
        'hr':u'%d prosinca',
        'hu':u'December %d',
        'ia':u'%d de decembre',
        'id':u'%d Desember',
        'io':u'%d di decembro',
        'is':u'%d. desember',
        'it':u'%d dicembre',
        'ja':u'12月%d日',
        'ka':u'%d დეკემბერი',
        'ko':u'12월 %d일',
        'ku':u"%d'ê berfanbarê",
        'la':u'%d Decembris',
        'lb':u'%d. Dezember',
        'lt':u'Gruodžio %d',
        'ml':u'ഡിസന്പര് %d',
        'nds':u'%d Dezember',
        'nl':u'%d december',
        'nn':u'%d. desember',
        'no':u'%d. desember',
        'oc':u'%d de decembre',
        'pl':u'%d grudnia',
        'pt':u'%d de Dezembro',
        'ro':u'%d decembrie',
        'ru':u'%d декабря',
        'sk':u'%d. december',
        'sl':u'%d. december',
        'sr':u'%d. децембар',
        'sv':u'%d december',
        'tl':u'Disyembre %d',
        'tr':u'%d Aralık',
        'tt':u'%d.Dekäber',
        'uk':u'%d грудня',
        'ur':u'%d دسمب',
        'vi':u'%d tháng 12',
        'wa':u'%d di decimbe',
        'zh':u'12月%d日'
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
        'af':u'%d v.C.',    # original - '%d v.Chr.'
        #'bg':u'%d г. пр.н.е.', # All years BC redirect to centuries for bg:
        'bs': u'%d p.ne.',
        'ca': u'%d aC',
        'da': u'%d f.Kr.',
        'de': u'%d v. Chr.',
        'en': u'%d BC',
        'eo': u'-%d',
        'es': u'%d adC',
        'et': u'%d eKr',
        'fi': u'%d eaa',
        'fo': u'%d f. Kr.',
        'fr': u'-%d',
        'he':u'%d לפנה"ס',
        'hr': u'%d p.n.e.',
        'is': u'%d f. Kr.',
        'it': u'%d AC',
        'ko': u'기원전 %d년',
        'la': u'%d a.C.n',
        'lb': u'-%d',
        'nds': u'%d v. Chr.',
        'nl': u'%d v. Chr.',
        'nn': u'-%d',
        'no': u'%d f.Kr.',
        'pl': u'%d p.n.e.',
        'pt': u'%d a.C.',
        'ro': u'%d î.Hr.',
        'ru': u'%d до н. э.',
        'sl': u'%d pr. n. št.',
        'sr': u'%d. пне.',
        'sv': u'%d f.Kr.',
        'uk':u'%d до Р.Х.',
        'zh': u'前%d年'
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
        'ja':u'%d年',
        'zh':u'%d年',
        'ko':u'%d년',
        'minnan':u'%d nî',
        'ur':u'%dسبم'
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

romanNums = ['-', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX',
             'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX',
             'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXVIX',
             'XXX']
             
numberPattern = u'(\d+)'
romanNumPattern = u'([IVX]+)'

def escapePattern( pattern ):
    """Converts a string pattern into a regex expression.
    Substitutes %d with (\d+), and %s with ([IVX]+).
    Returns a compiled regex object"""

    # TODO: need to rewrite to handle special characters that regex might misinterpret
    pt = pattern
    pt = re.compile(u'%d').sub( u'(\d+)', pt )
    pt = re.compile(u'%s').sub( u'([IVX]+)', pt )
    return re.compile(pt)


def dh( value, pattern, encf, decf ):
    """Try to get a value from the str
    """
    if type(value) is int:
        return pattern % encf(value)
    else:
        pt = re.compile(u'%d').sub(numberPattern, pattern )
        m = re.compile(pt).match( value )
        if m:
            try:
                year = decf( int( m.group(1) ))
                if value == pattern % encf(year):
                    return year
            except:
                pass
        return None

def dh_lt( value ):
    """Try to get a value from the str - lithuanian
    """
    pattern = u'%s amžiaus %d-as dešimtmetis'
    revpattern = romanNumPattern +u' amžiaus '+ numberPattern +u'-as dešimtmetis'
    encf = lambda i: (romanNums[i/100+1], i%100/10+1)
    
    if type(value) is int:
        return pattern % encf(value)
    else:
        m = re.compile(revpattern).match( value )
        if m:
            try:
                rom = romanNums.index(m.group(1))
                num = int(m.group(2))
                year = (rom-1)*100 + (num-1)*10
                if value == pattern % encf(year):
                    return year
            except:
                pass
        return None
        
def dh_pl( value ):
    """Try to get a value from the str - polish
    """
    pattern = u'Lata %d. %s wieku'
    revpattern = u'Lata '+ numberPattern +u'. '+ romanNumPattern +u' wieku'
    encf = lambda i: (i%100, romanNums[i/100+1])
    
    if type(value) is int:
        return pattern % encf(value)
    else:
        m = re.compile(revpattern).match( value )
        if m:
            try:
                num = int(m.group(1))
                rom = romanNums.index(m.group(2))
                year = (rom-1)*100 + num
                if value == pattern % encf(year):
                    return year
            except:
                pass
        return None
        
def dh_sk( value ):
    """Try to get a value from the str - slovak
    """
    pattern = u'%d. roky %d. storočia'
    revpattern = numberPattern +u'. roky '+ numberPattern +u'. storočia'
    encf = lambda i: (i%100, i/100+1)
    
    if type(value) is int:
        return pattern % encf(value)
    else:
        m = re.compile(revpattern).match( value )
        if m:
            try:
                num1 = int(m.group(1))
                num2 = int(m.group(2))
                year = (num2-1)*100 + num1
                if value == pattern % encf(year):
                    return year
            except:
                pass
        return None

def dh_roman( value, pattern ):
    """Try to get a value from the str - single roman numeral
    """
    if type(value) is int:
        return pattern % romanNums[ value ]
    else:
        m = escapePattern(pattern).match( value )
        if m:
            try:
                val = romanNums.index(m.group(1))
                if value == pattern % romanNums[ val ]:
                    return val
            except:
                pass
        return None

def noConv( i ):
    return i
#
# lambda val: dh( val, u'pattern string', encodingFunc, decodingFunc )
#
# encodingFunc converts from 'i' to a some number(s) used in localized string
# decodingFunc converts the first number found in the string back into normalized i
#   Normalized i is the 0-ending year:  1980, 1990, etc.
#   No error check is performed (it assumes 'i' is already in that form)
#   encodingFunc can return a bunch of values together (.., .., ..)
#
# Usage scenarios:
#  decadesAD['en'](1980) => u'1980s'
#  decadesAD['en'](u'1980s') => 1980
#  decadesAD['en'](u'anything else') => None
#
decadesAD = {
    'bg' :      lambda val: dh( val, u'%d-те',                   noConv, noConv ),
    'ca' :      lambda val: dh( val, u'Dècada del %d',           noConv, noConv ),
    'cy' :      lambda val: dh( val, u'%dau',                    noConv, noConv ),
    'da' :      lambda val: dh( val, u"%d'erne",                 noConv, noConv ),
    'de' :      lambda val: dh( val, u'%der',                    noConv, noConv ),
    'el' :      lambda val: dh( val, u'Δεκαετία %d',             noConv, noConv ),
    'en' :      lambda val: dh( val, u'%ds',                     noConv, noConv ),
    'eo' :      lambda val: dh( val, u'%d-aj jaroj',             noConv, noConv ),
    'es' :      lambda val: dh( val, u'Años %d',                 noConv, noConv ),
    'et' :      lambda val: dh( val, u'%d. aastad',              noConv, noConv ),
    'fi' :      lambda val: dh( val, u'%d-luku',                 noConv, noConv ),
    'fr' :      lambda val: dh( val, u'Années %d',               noConv, noConv ),
    'is' :      lambda val: dh( val, u'%d–%d',                   lambda i: (i+1,i+10), lambda i: i-1 ),     # '1971–1980'
    'it' :      lambda val: dh( val, u'Anni %d',                 noConv, noConv ),
    'ja' :      lambda val: dh( val, u'%d年代',                  noConv, noConv ),
    'la' :      lambda val: dh( val, u'Decennium %d',            lambda i: i/10+1, lambda i: (i-1)*10 ),
    'lt' :      lambda val: dh_lt( val ),                                                                   # 1970 => 'XX amžiaus 8-as dešimtmetis'
    'mi' :      lambda val: dh( val, u'Ngahurutanga %d',         lambda i: i/10+1, lambda i: (i-1)*10 ),
    'nl' :      lambda val: dh( val, u'%d-%d',                   lambda i: (i,i+9), noConv ),               # '1970-1979'
    'no' :      lambda val: dh( val, u'%d-årene',                noConv, noConv ),
    'pl' :      lambda val: dh_pl( val ),                                                                   # 1970 => 'Lata 70. XX wieku'
    'pt' :      lambda val: dh( val, u'Década de %d',            noConv, noConv ),
    'ro' :      lambda val: dh( val, u'Anii %d',                 noConv, noConv ),
    'ru' :      lambda val: dh( val, u'%d-е',                    noConv, noConv ),
    'simple' :  lambda val: dh( val, u'%ds',                     noConv, noConv ),
    'sk' :      lambda val: dh_sk( val ),                                                                   # 1970 => '70. roky 20. storočia'
    'sl' :      lambda val: dh( val, u'%d.',                     noConv, noConv ),
    'sv' :      lambda val: dh( val, u'%d-talet',                noConv, noConv ),
    'zh' :      lambda val: dh( val, u'%d年代',                  noConv, noConv ),
}

decadesBC = {
    'de' :      lambda val: dh( val, u'%der v. Chr.',            noConv, noConv ),
    'en' :      lambda val: dh( val, u'%ds BC',                  noConv, noConv ),
    'es' :      lambda val: dh( val, u'Años %d adC',             noConv, noConv ),
    'fr' :      lambda val: dh( val, u'Années -%d',              noConv, noConv ),
    'it' :      lambda val: dh( val, u'Anni %d AC',              noConv, noConv ),
    'pt' :      lambda val: dh( val, u'Década de %d a.C.',       noConv, noConv ),
    'ru' :      lambda val: dh( val, u'%d-е до н. э.',           noConv, noConv ),
    'sl' :      lambda val: dh( val, u'%d. pr. n. št.',          noConv, noConv ),
}

centuriesBC = {
    'af' :      lambda val: dh( val, u'%de eeu v. C.',           noConv, noConv ),
    'ca' :      lambda val: dh_roman( val, u'Segle %s aC' ),
    'da' :      lambda val: dh( val, u'%d. århundrede f.Kr.',    noConv, noConv ),
    'de' :      lambda val: dh( val, u'%d. Jahrhundert v. Chr.', noConv, noConv ),
    'en' :      lambda val: dh( val, u'%dth century BC',         noConv, noConv ),
    'eo' :      lambda val: dh( val, u'%d-a jarcento a.K.',      noConv, noConv ),
    'es' :      lambda val: dh_roman( val, u'Siglo %s adC' ),	
    'fr' :      lambda val: dh_roman( val, u'%se siècle av. J.-C.' ),
    'it' :      lambda val: dh_roman( val, u'%s secolo AC' ),
    'ja' :      lambda val: dh( val, u'紀元前%d世紀',             noConv, noConv ),
    'nl' :      lambda val: dh( val, u'%de eeuw v. Chr.',        noConv, noConv ),
    'pl' :      lambda val: dh_roman( val, u'%s wiek p.n.e.' ),
    'sl' :      lambda val: dh( val, u'%d. stoletje pr. n. št.', noConv, noConv ),
    'zh' :      lambda val: dh( val, u'前%d世纪',                 noConv, noConv ),
}