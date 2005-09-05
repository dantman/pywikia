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
# © Yuri Astrakhan, 2005 (years/decades/centuries/milleniums  str <=> int  conversions)
#
# Distribute under the terms of the PSF license.
#

# used for date recognition
import types
import re
import wikipedia


# Month names, must be in order (used as indexes)
monthNames = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]

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

# For all languages the maximal value a year BC can have; before this date the
# language switches to decades or centuries
maxyearBC = {
        'ca':500,
        'de':400,
        'en':499,
        'nl':1000,
        'pl':776
        }

maxyearAD = {
        'es':2005,
        }

romanNums = ['-', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX',
             'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX',
             'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXVIX',
             'XXX']

_escPtrnCache = {}
def escapePattern( pattern ):
    """Converts a string pattern into a regex expression.
    Substitutes %d with (\d+), and %s with ([IVX]+).
    Returns a compiled regex object"""

    if pattern not in _escPtrnCache:
        pt = re.escape( pattern )
        pt = re.compile(u'\\\%d').sub( u'(\d+)', pt )       # %d matches any integer
        pt = re.compile(u'\\\%s').sub( u'([IVX]+)', pt )    # %s matches any roman number
        cm = re.compile( u'^' + pt + u'$' )

        pos = 0
        decoders = []
        while True :
            pos = pattern.find( '%', pos )
            if pos == -1 or pos+1 == len(pattern): break    # break if no more instances, or '%' is in the last position
            pos = pos+1
            if pattern[pos] == 'd':
                decoders.append( lambda v: int(v) )
            elif pattern[pos] == 's':
                decoders.append( lambda v: romanNums.index(v) )
            
        _escPtrnCache[pattern] = (cm, decoders)

    return _escPtrnCache[pattern]


def dh( value, pattern, encf, decf ):
    """This function helps in year parsing.
        Usually it will be used as a lambda call in a map:
            lambda val: dh( val, u'pattern string', encodingFunc, decodingFunc )

        encodingFunc converts from an integer parameter to a single number or a tuple parameter that
            can be passed as format argument to the pattern:   pattern % encodingFunc(year)
            
        decodingFunc converts a list of positive integers found in the original value string
            into a year value. dh() searches creates this list based on the pattern string.
            dh() interprets %d as a decimal and %s as a roman numeral number.

        Usage scenarios:
            decadesAD['en'](1980) => u'1980s'
            decadesAD['en'](u'1980s') => 1980
            decadesAD['en'](u'anything else') => raise ValueError (or some other exception?)
    """
    if type(value) is int:
        return pattern % encf(value)
    else:
        cm, dcrs = escapePattern(pattern)
        m = cm.match(value)
        if m:
            values = [ dcrs[i](m.group(i+1)) for i in range(len(dcrs))]     # decode each found value using provided decoder
            year = decf( values )
            if value == pattern % encf(year):
                return year
            
        raise ValueError("reverse encoding didn't match")

def dh_dec( value, pattern ):
    """decoding helper for a single integer value, no conversion, round to decimals (used in decades)"""
    return dh( value, pattern, dec0, singleVal )

def dh_noConv( value, pattern ):
    """decoding helper for a single integer value, no conversion, no rounding (used in centuries, milleniums)"""
    return dh( value, pattern, noConv, singleVal )

def dh_roman( value, pattern ):
    """decoding helper for a single roman number (used in centuries, milleniums)"""
    return dh( value, pattern, lambda i: romanNums[i], singleVal )

def dh_thai_solar_calendar( value, pattern ):
    """decoding helper for the Thai solar calendar"""
    return dh( value, pattern, lambda i: i + 543, lambda l: l[0] - 543 )

def singleVal( v ):
    return v[0]

def noConv( i ):
    return i

def dec0( i ):
    return (i/10)*10        # round to the nearest decade, decade starts with a '0'-ending year 

def dec1( i ):
    return dec0(i)+1        # round to the nearest decade, decade starts with a '1'-ending year

def slh( value, lst ):
    """This function helps in simple list value matching.
        Usually it will be used as a lambda call in a map:
            lambda val: slh( val, [u'January',u'February',...] )

        Usage scenarios:
            map['MonthNames']['en'](1) => u'January'
            map['MonthNames']['en'](u'January') => 1
            map['MonthNames']['en'](u'anything else') => raise ValueError
    """
    if type(value) is int:
        return lst[value-1]
    else:
        return lst.index(value)+1

#
# All years/decades/centuries/milleniums are designed in such a way
# as to allow for easy date to string and string to date conversion.
# For example, using any map with either an integer or a string will produce its oposite value:
#            decadesBC['en'](1980) => u'1980s BC'
#            decadesBC['en'](u'1980s BC') => 1980
# This is useful when trying to decide if a certain article is a localized date or not, or generating dates.
# See dh() for additional information.
#
dateFormats = {
    'January': { 
            'af' :      lambda val: dh_noConv( val, u'%d Januarie' ),
            'ang':      lambda val: dh_noConv( val, u'%d Æfterra Géola' ),
            'ar' :      lambda val: dh_noConv( val, u'%d يناير' ),
            'ast':      lambda val: dh_noConv( val, u'%d de xineru' ),
            'be' :      lambda val: dh_noConv( val, u'%d студзеня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d януари' ),
            'bs' :      lambda val: dh_noConv( val, u'%d. januar' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de gener' ),
            'co' :      lambda val: dh_noConv( val, u'%d di ghjennaghju' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. leden' ),
            'csb':      lambda val: dh_noConv( val, u'%d stëcznika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Ionawr' ),
            'da' :      lambda val: dh_noConv( val, u'%d. januar' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Januar' ),
            'el' :      lambda val: dh_noConv( val, u'%d Ιανουαρίου' ),
            'en' :      lambda val: dh_noConv( val, u'January %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de januaro' ),
            'es' :      lambda val: dh_noConv( val, u'%d de enero' ),
            'et' :      lambda val: dh_noConv( val, u'%d. jaanuar' ),
            'eu' :      lambda val: dh_noConv( val, u'Urtarrilaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. tammikuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. januar' ),
            'fr' :      lambda val: dh_noConv( val, u'%d janvier' ),
            'fy' :      lambda val: dh_noConv( val, u'%d jannewaris' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Eanáir' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de xaneiro' ),
            'he' :      lambda val: dh_noConv( val, u'%d בינואר' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. siječnja' ),
            'hu' :      lambda val: dh_noConv( val, u'Január %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de januario' ),
            'id' :      lambda val: dh_noConv( val, u'%d Januari' ),
            'ie' :      lambda val: dh_noConv( val, u'%d januar' ), # not all months for ie added yet
            'io' :      lambda val: dh_noConv( val, u'%d di januaro' ),
            'is' :      lambda val: dh_noConv( val, u'%d. janúar' ),
            'it' :      lambda val: dh_noConv( val, u'%d gennaio' ),
            'ja' :      lambda val: dh_noConv( val, u'1月%d日' ),
            'ka' :      lambda val: dh_noConv( val, u'%d იანვარი' ), # ka only January and December added for now
            'ko' :      lambda val: dh_noConv( val, u'1월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê rêbendanê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Ianuarii' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Januar' ),
            'lt' :      lambda val: dh_noConv( val, u'Sausio %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ജനുവരി %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Januar' ),
            'nl' :      lambda val: dh_noConv( val, u'%d januari' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. januar' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. januar' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de genièr' ),
            'pl' :      lambda val: dh_noConv( val, u'%d stycznia' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Janeiro' ),
            'ro' :      lambda val: dh_noConv( val, u'%d ianuarie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d января' ),
            'se' :      lambda val: dh_noConv( val, u'ođđajagimánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. január' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. januar' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. јануар' ),
            'sv' :      lambda val: dh_noConv( val, u'%d januari' ),
            'tl' :      lambda val: dh_noConv( val, u'Enero %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Ocak' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Ğínwar' ),
            'uk' :      lambda val: dh_noConv( val, u'%d січня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d جنوری' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 1' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di djanvî" ), # Walloon names depend on the day number; taking the most common form
            'zh' :      lambda val: dh_noConv( val, u'1月%d日' ),
    },
    
    'February': {
            'af' :      lambda val: dh_noConv( val, u'%d Februarie' ),
            'ang':      lambda val: dh_noConv( val, u'%d Solmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d فبراير' ),
            'ast':      lambda val: dh_noConv( val, u'%d de febreru' ),
            'be' :      lambda val: dh_noConv( val, u'%d лютага' ),
            'bg' :      lambda val: dh_noConv( val, u'%d февруари' ),
            'bs' :      lambda val: dh_noConv( val, u'Februar %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de febrer' ),
            'co' :      lambda val: dh_noConv( val, u'%d di frivaghju' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. únor' ),
            'csb':      lambda val: dh_noConv( val, u'%d gromicznika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Chwefror' ),
            'da' :      lambda val: dh_noConv( val, u'%d. februar' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Februar' ),
            'el' :      lambda val: dh_noConv( val, u'%d Φεβρουαρίου' ),
            'en' :      lambda val: dh_noConv( val, u'February %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de februaro' ),
            'es' :      lambda val: dh_noConv( val, u'%d de febrero' ),
            'et' :      lambda val: dh_noConv( val, u'%d. veebruar' ),
            'eu' :      lambda val: dh_noConv( val, u'Ottsailaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. helmikuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. februar' ),
            'fr' :      lambda val: dh_noConv( val, u'%d février' ),
            'fy' :      lambda val: dh_noConv( val, u'%d febrewaris' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Feabhra' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de febreiro' ),
            'he' :      lambda val: dh_noConv( val, u'%d בפברואר' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. veljače' ),
            'hu' :      lambda val: dh_noConv( val, u'Február %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de februario' ),
            'id' :      lambda val: dh_noConv( val, u'%d Februari' ),
            'io' :      lambda val: dh_noConv( val, u'%d di februaro' ),
            'is' :      lambda val: dh_noConv( val, u'%d. febrúar' ),
            'it' :      lambda val: dh_noConv( val, u'%d febbraio' ),
            'ja' :      lambda val: dh_noConv( val, u'2月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'2월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê reşemiyê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Februarii' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Februar' ),
            'lt' :      lambda val: dh_noConv( val, u'Vasario %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ഫെബ്രുവരി %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Februar' ),
            'nl' :      lambda val: dh_noConv( val, u'%d februari' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. februar' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. februar' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de febrièr' ),
            'pl' :      lambda val: dh_noConv( val, u'%d lutego' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Fevereiro' ),
            'ro' :      lambda val: dh_noConv( val, u'%d februarie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d февраля' ),
            'se' :      lambda val: dh_noConv( val, u'guovvamánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. február' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. februar' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. фебруар' ),
            'sv' :      lambda val: dh_noConv( val, u'%d februari' ),
            'tl' :      lambda val: dh_noConv( val, u'Pebrero %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Şubat' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Febräl' ),
            'uk' :      lambda val: dh_noConv( val, u'%d лютого' ),
            'ur' :      lambda val: dh_noConv( val, u'%d فروری' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 2' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di fevrî" ),
            'zh' :      lambda val: dh_noConv( val, u'2月%d日' ),
    },
    
    'March': {
            'af' :      lambda val: dh_noConv( val, u'%d Maart' ),
            'ang':      lambda val: dh_noConv( val, u'%d Hréþmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d مارس' ),
            'ast':      lambda val: dh_noConv( val, u'%d de marzu' ),
            'be' :      lambda val: dh_noConv( val, u'%d сакавіка' ),
            'bg' :      lambda val: dh_noConv( val, u'%d март' ),
            'bs' :      lambda val: dh_noConv( val, u'Mart %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de març' ),
            'co' :      lambda val: dh_noConv( val, u'%d di marzu' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. březen' ),
            'csb':      lambda val: dh_noConv( val, u'%d strumiannika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Mawrth' ),
            'da' :      lambda val: dh_noConv( val, u'%d. marts' ),
            'de' :      lambda val: dh_noConv( val, u'%d. März' ),
            'en' :      lambda val: dh_noConv( val, u'March %d' ),
            'el' :      lambda val: dh_noConv( val, u'%d Μαρτίου' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de marto' ),
            'es' :      lambda val: dh_noConv( val, u'%d de marzo' ),
            'et' :      lambda val: dh_noConv( val, u'%d. märts' ),
            'eu' :      lambda val: dh_noConv( val, u'Martxoaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. maaliskuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. mars' ),
            'fr' :      lambda val: dh_noConv( val, u'%d mars' ),
            'fy' :      lambda val: dh_noConv( val, u'%d maart' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Márta' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de marzo' ),
            'he' :      lambda val: dh_noConv( val, u'%d במרץ' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. ožujka' ),
            'hu' :      lambda val: dh_noConv( val, u'Március %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de martio' ),
            'id' :      lambda val: dh_noConv( val, u'%d Maret' ),
            'io' :      lambda val: dh_noConv( val, u'%d di marto' ),
            'is' :      lambda val: dh_noConv( val, u'%d. mars' ),
            'it' :      lambda val: dh_noConv( val, u'%d marzo' ),
            'ja' :      lambda val: dh_noConv( val, u'3月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'3월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê adarê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Martii' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Mäerz' ),
            'lt' :      lambda val: dh_noConv( val, u'Kovo %d' ),
            'ml' :      lambda val: dh_noConv( val, u'മാര്ച് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d März' ),
            'nl' :      lambda val: dh_noConv( val, u'%d maart' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. mars' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. mars' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de març' ),
            'pl' :      lambda val: dh_noConv( val, u'%d marca' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Março' ),
            'ro' :      lambda val: dh_noConv( val, u'%d martie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d марта' ),
            'se' :      lambda val: dh_noConv( val, u'njukčamánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. marec' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. marec' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. март' ),
            'sv' :      lambda val: dh_noConv( val, u'%d mars' ),
            'tl' :      lambda val: dh_noConv( val, u'Marso %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Mart' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Mart' ),
            'uk' :      lambda val: dh_noConv( val, u'%d березня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d مارچ' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 3' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di måss" ),
            'zh' :      lambda val: dh_noConv( val, u'3月%d日' ),
    },
    
    'April': {
            'af' :      lambda val: dh_noConv( val, u'%d April' ),
            'ang':      lambda val: dh_noConv( val, u'%d Éastermónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d أبريل' ),
            'ast':      lambda val: dh_noConv( val, u"%d d'abril" ),
            'be' :      lambda val: dh_noConv( val, u'%d красавіка' ),
            'bg' :      lambda val: dh_noConv( val, u'%d април' ),
            'bs' :      lambda val: dh_noConv( val, u'April %d' ),
            'ca' :      lambda val: dh_noConv( val, u"%d d'abril" ),
            'co' :      lambda val: dh_noConv( val, u"%d d'aprile" ),
            'cs' :      lambda val: dh_noConv( val, u'%d. duben' ),
            'csb':      lambda val: dh_noConv( val, u'%d łżëkwiôta' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Ebrill' ),
            'da' :      lambda val: dh_noConv( val, u'%d. april' ),
            'de' :      lambda val: dh_noConv( val, u'%d. April' ),
            'el' :      lambda val: dh_noConv( val, u'%d Απριλίου' ),
            'en' :      lambda val: dh_noConv( val, u'April %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de aprilo' ),
            'es' :      lambda val: dh_noConv( val, u'%d de abril' ),
            'et' :      lambda val: dh_noConv( val, u'%d. aprill' ),
            'eu' :      lambda val: dh_noConv( val, u'Aprilaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. huhtikuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. apríl' ),
            'fr' :      lambda val: dh_noConv( val, u'%d avril' ),
            'fy' :      lambda val: dh_noConv( val, u'%d april' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Aibreán' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de abril' ),
            'he' :      lambda val: dh_noConv( val, u'%d באפריל' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. travnja' ),
            'hu' :      lambda val: dh_noConv( val, u'Április %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de april' ),
            'id' :      lambda val: dh_noConv( val, u'%d April' ),
            'ie' :      lambda val: dh_noConv( val, u'%d april' ),
            'io' :      lambda val: dh_noConv( val, u'%d di aprilo' ),
            'is' :      lambda val: dh_noConv( val, u'%d. apríl' ),
            'it' :      lambda val: dh_noConv( val, u'%d aprile' ),
            'ja' :      lambda val: dh_noConv( val, u'4月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'4월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê avrêlê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Aprilis' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Abrëll' ),
            'lt' :      lambda val: dh_noConv( val, u'Balandžio %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ഏപ്രില് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d April' ),
            'nl' :      lambda val: dh_noConv( val, u'%d april' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. april' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. april' ),
            'oc' :      lambda val: dh_noConv( val, u"%d d'abril" ),
            'pl' :      lambda val: dh_noConv( val, u'%d kwietnia' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Abril' ),
            'ro' :      lambda val: dh_noConv( val, u'%d aprilie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d апреля' ),
            'se' :      lambda val: dh_noConv( val, u'cuoŋománu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. apríl' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. april' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. април' ),
            'sv' :      lambda val: dh_noConv( val, u'%d april' ),
            'tl' :      lambda val: dh_noConv( val, u'Abríl %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Nisan' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Äpril' ),
            'uk' :      lambda val: dh_noConv( val, u'%d квітня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d اپریل' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 4' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di avri" ),
            'zh' :      lambda val: dh_noConv( val, u'4月%d日' ),
    },
    
    'May': {
            'af' :      lambda val: dh_noConv( val, u'%d Mei' ),
            'ang':      lambda val: dh_noConv( val, u'%d Þrimilcemónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d مايو' ),
            'ast':      lambda val: dh_noConv( val, u'%d de mayu' ),
            'be' :      lambda val: dh_noConv( val, u'%d траўня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d май' ),
            'bs' :      lambda val: dh_noConv( val, u'Maj %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de maig' ),
            'co' :      lambda val: dh_noConv( val, u'%d di maghju' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. květen' ),
            'csb':      lambda val: dh_noConv( val, u'%d môja' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Mai' ),
            'da' :      lambda val: dh_noConv( val, u'%d. maj' ),
            'el' :      lambda val: dh_noConv( val, u'%d Μαΐου' ),
            'en' :      lambda val: dh_noConv( val, u'May %d' ),
            'et' :      lambda val: dh_noConv( val, u'%d. mai' ),
            'eu' :      lambda val: dh_noConv( val, u'Maiatzaren %d' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Mai' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de majo' ),
            'es' :      lambda val: dh_noConv( val, u'%d de mayo' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. toukokuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. mai' ),
            'fr' :      lambda val: dh_noConv( val, u'%d mai' ),
            'fy' :      lambda val: dh_noConv( val, u'%d maaie' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Bealtaine' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de maio' ),
            'he' :      lambda val: dh_noConv( val, u'%d במאי' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. svibnja' ),
            'hu' :      lambda val: dh_noConv( val, u'Május %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de maio' ),
            'id' :      lambda val: dh_noConv( val, u'%d Mei' ),
            'ie' :      lambda val: dh_noConv( val, u'%d may' ),
            'io' :      lambda val: dh_noConv( val, u'%d di mayo' ),
            'is' :      lambda val: dh_noConv( val, u'%d. maí' ),
            'it' :      lambda val: dh_noConv( val, u'%d maggio' ),
            'ja' :      lambda val: dh_noConv( val, u'5月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'5월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê gulanê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Maii' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Mee' ),
            'lt' :      lambda val: dh_noConv( val, u'Gegužės %d' ),
            'ml' :      lambda val: dh_noConv( val, u'മേയ് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Mai' ),
            'nl' :      lambda val: dh_noConv( val, u'%d mei' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. mai' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. mai' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de mai' ),
            'pl' :      lambda val: dh_noConv( val, u'%d maja' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Maio' ),
            'ro' :      lambda val: dh_noConv( val, u'%d mai' ),
            'ru' :      lambda val: dh_noConv( val, u'%d мая' ),
            'se' :      lambda val: dh_noConv( val, u'miessemánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. máj' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. maj' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. мај' ),
            'sv' :      lambda val: dh_noConv( val, u'%d maj' ),
            'tl' :      lambda val: dh_noConv( val, u'Mayo %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Mayıs' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. May' ),
            'uk' :      lambda val: dh_noConv( val, u'%d травня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d مئ' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 5' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di may" ),
            'zh' :      lambda val: dh_noConv( val, u'5月%d日' ),
    },
    
    'June': {
            'af' :      lambda val: dh_noConv( val, u'%d Junie' ),
            'ang':      lambda val: dh_noConv( val, u'%d Séremónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d يونيو' ),
            'ast':      lambda val: dh_noConv( val, u'%d de xunu' ),
            'be' :      lambda val: dh_noConv( val, u'%d чэрвеня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d юни' ),
            'bs' :      lambda val: dh_noConv( val, u'Jun %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de juny' ),
            'co' :      lambda val: dh_noConv( val, u'%d di ghjugnu' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. červen' ),
            'csb':      lambda val: dh_noConv( val, u'%d czerwińca' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Mehefin' ),
            'da' :      lambda val: dh_noConv( val, u'%d. juni' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Juni' ),
            'el' :      lambda val: dh_noConv( val, u'%d Ιουνίου' ),
            'en' :      lambda val: dh_noConv( val, u'June %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de junio' ),
            'es' :      lambda val: dh_noConv( val, u'%d de junio' ),
            'et' :      lambda val: dh_noConv( val, u'%d. juuni' ),
            'eu' :      lambda val: dh_noConv( val, u'Ekainaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. kesäkuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. juni' ),
            'fr' :      lambda val: dh_noConv( val, u'%d juin' ),
            'fy' :      lambda val: dh_noConv( val, u'%d juny' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Meitheamh' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de xuño' ),
            'he' :      lambda val: dh_noConv( val, u'%d ביוני' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. lipnja' ),
            'hu' :      lambda val: dh_noConv( val, u'Június %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de junio' ),
            'id' :      lambda val: dh_noConv( val, u'%d Juni' ),
            'io' :      lambda val: dh_noConv( val, u'%d di junio' ),
            'is' :      lambda val: dh_noConv( val, u'%d. júní' ),
            'it' :      lambda val: dh_noConv( val, u'%d giugno' ),
            'ja' :      lambda val: dh_noConv( val, u'6月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'6월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê pûşperê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Iunii' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Juni' ),
            'lt' :      lambda val: dh_noConv( val, u'Birželio %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ജൂണ്‍ %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Juni' ),
            'nl' :      lambda val: dh_noConv( val, u'%d juni' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. juni' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. juni' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de junh' ),
            'pl' :      lambda val: dh_noConv( val, u'%d czerwca' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Junho' ),
            'ro' :      lambda val: dh_noConv( val, u'%d iunie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d июня' ),
            'se' :      lambda val: dh_noConv( val, u'geassemánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. jún' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. junij' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. јун' ),
            'sv' :      lambda val: dh_noConv( val, u'%d juni' ),
            'tl' :      lambda val: dh_noConv( val, u'Hunyo %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Haziran' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Yün' ),
            'uk' :      lambda val: dh_noConv( val, u'%d червня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d جون' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 6' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di djun" ),
            'zh' :      lambda val: dh_noConv( val, u'6月%d日' ),
    },
    
    'July': {
            'af' :      lambda val: dh_noConv( val, u'%d Julie' ),
            'ang':      lambda val: dh_noConv( val, u'%d Mǽdmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d يوليو' ),
            'ast':      lambda val: dh_noConv( val, u'%d de xunetu' ),
            'be' :      lambda val: dh_noConv( val, u'%d ліпеня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d юли' ),
            'bs' :      lambda val: dh_noConv( val, u'Jul %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de juliol' ),
            'co' :      lambda val: dh_noConv( val, u'%d di lugliu' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. červenec' ),
            'csb':      lambda val: dh_noConv( val, u'%d lëpinca' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Gorffenaf' ),
            'da' :      lambda val: dh_noConv( val, u'%d. juli' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Juli' ),
            'en' :      lambda val: dh_noConv( val, u'July %d' ),
            'el' :      lambda val: dh_noConv( val, u'%d Ιουλίου' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de julio' ),
            'es' :      lambda val: dh_noConv( val, u'%d de julio' ),
            'et' :      lambda val: dh_noConv( val, u'%d. juuli' ),
            'eu' :      lambda val: dh_noConv( val, u'Uztailaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. heinäkuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. juli' ),
            'fr' :      lambda val: dh_noConv( val, u'%d juillet' ),
            'fy' :      lambda val: dh_noConv( val, u'%d july' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Iúil' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de xullo' ),
            'he' :      lambda val: dh_noConv( val, u'%d ביולי' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. srpnja' ),
            'hu' :      lambda val: dh_noConv( val, u'Július %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de julio' ),
            'id' :      lambda val: dh_noConv( val, u'%d Juli' ),
            'io' :      lambda val: dh_noConv( val, u'%d di julio' ),
            'is' :      lambda val: dh_noConv( val, u'%d. júlí' ),
            'it' :      lambda val: dh_noConv( val, u'%d luglio' ),
            'ja' :      lambda val: dh_noConv( val, u'7月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'7월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê tîrmehê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Iulii' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Juli' ),
            'lt' :      lambda val: dh_noConv( val, u'Liepos %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ജൂലൈ %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Juli' ),
            'nl' :      lambda val: dh_noConv( val, u'%d juli' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. juli' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. juli' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de julhet' ),
            'pl' :      lambda val: dh_noConv( val, u'%d lipca' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Julho' ),
            'ro' :      lambda val: dh_noConv( val, u'%d iulie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d июля' ),
            'se' :      lambda val: dh_noConv( val, u'suoidnemánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. júl' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. julij' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. јул' ),
            'sv' :      lambda val: dh_noConv( val, u'%d juli' ),
            'tl' :      lambda val: dh_noConv( val, u'Hulyo %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Temmuz' ),
            'tt' :      lambda val: dh_noConv( val, u'%d Yül' ),
            'uk' :      lambda val: dh_noConv( val, u'%d липня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d جلائ' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 7' ),
            'wa' :      lambda val: dh_noConv( val, u"%d di djulete" ),
            'zh' :      lambda val: dh_noConv( val, u'7月%d日' ),
    },
    
    'August': {
            'af' :      lambda val: dh_noConv( val, u'%d Augustus' ),
            'ang':      lambda val: dh_noConv( val, u'%d Wéodmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d أغسطس' ),
            'ast':      lambda val: dh_noConv( val, u"%d d'agostu" ),
            'be' :      lambda val: dh_noConv( val, u'%d жніўня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d август' ),
            'bs' :      lambda val: dh_noConv( val, u'Avgust %d' ),
            'ca' :      lambda val: dh_noConv( val, u"%d d'agost" ),
            'co' :      lambda val: dh_noConv( val, u"%d d'aostu" ),
            'cs' :      lambda val: dh_noConv( val, u'%d. srpen' ),
            'csb':      lambda val: dh_noConv( val, u'%d zélnika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Awst' ),
            'da' :      lambda val: dh_noConv( val, u'%d. august' ),
            'de' :      lambda val: dh_noConv( val, u'%d. August' ),
            'el' :      lambda val: dh_noConv( val, u'%d Αυγούστου' ),
            'en' :      lambda val: dh_noConv( val, u'August %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de aŭgusto' ),
            'es' :      lambda val: dh_noConv( val, u'%d de agosto' ),
            'et' :      lambda val: dh_noConv( val, u'%d. august' ),
            'eu' :      lambda val: dh_noConv( val, u'Abuztuaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. elokuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. august' ),
            'fr' :      lambda val: dh_noConv( val, u'%d août' ),
            'fy' :      lambda val: dh_noConv( val, u'%d augustus' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Lúnasa' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de agosto' ),
            'he' :      lambda val: dh_noConv( val, u'%d באוגוסט' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. kolovoza' ),
            'hu' :      lambda val: dh_noConv( val, u'Augusztus %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de augusto' ),
            'id' :      lambda val: dh_noConv( val, u'%d Agustus' ),
            'ie' :      lambda val: dh_noConv( val, u'%d august' ),
            'io' :      lambda val: dh_noConv( val, u'%d di agosto' ),
            'is' :      lambda val: dh_noConv( val, u'%d. ágúst' ),
            'it' :      lambda val: dh_noConv( val, u'%d agosto' ),
            'ja' :      lambda val: dh_noConv( val, u'8月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'8월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê gelawêjê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Augusti' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. August' ),
            'lt' :      lambda val: dh_noConv( val, u'Rugpjūčio %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ആഗസ്റ്റ്‌ %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d August' ),
            'nl' :      lambda val: dh_noConv( val, u'%d augustus' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. august' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. august' ),
            'oc' :      lambda val: dh_noConv( val, u"%d d'agost" ),
            'pl' :      lambda val: dh_noConv( val, u'%d sierpnia' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Agosto' ),
            'ro' :      lambda val: dh_noConv( val, u'%d august' ),
            'ru' :      lambda val: dh_noConv( val, u'%d августа' ),
            'se' :      lambda val: dh_noConv( val, u'borgemánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. august' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. avgust' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. август' ),
            'sv' :      lambda val: dh_noConv( val, u'%d augusti' ),
            'tl' :      lambda val: dh_noConv( val, u'Agosto %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Ağustos' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. August' ),
            'uk' :      lambda val: dh_noConv( val, u'%d серпня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d اگست' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 8' ),
            'wa' :      lambda val: dh_noConv( val, u"%d d' awousse" ),
            'zh' :      lambda val: dh_noConv( val, u'8月%d日' ),
    },
    
    'September': {
            'af' :      lambda val: dh_noConv( val, u'%d September' ),
            'ang':      lambda val: dh_noConv( val, u'%d Háligmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d سبتمبر' ),
            'ast':      lambda val: dh_noConv( val, u'%d de setiembre' ),
            'be' :      lambda val: dh_noConv( val, u'%d верасьня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d септември' ),
            'bs' :      lambda val: dh_noConv( val, u'Septembar %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de setembre' ),
            'co' :      lambda val: dh_noConv( val, u'%d di settembre' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. září' ),
            'csb':      lambda val: dh_noConv( val, u'%d séwnika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Medi' ),
            'da' :      lambda val: dh_noConv( val, u'%d. september' ),
            'de' :      lambda val: dh_noConv( val, u'%d. September' ),
            'el' :      lambda val: dh_noConv( val, u'%d Σεπτεμβρίου' ),
            'en' :      lambda val: dh_noConv( val, u'September %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de septembro' ),
            'es' :      lambda val: dh_noConv( val, u'%d de septiembre' ),
            'et' :      lambda val: dh_noConv( val, u'%d. september' ),
            'eu' :      lambda val: dh_noConv( val, u'Irailaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. syyskuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. september' ),
            'fr' :      lambda val: dh_noConv( val, u'%d septembre' ),
            'fy' :      lambda val: dh_noConv( val, u'%d septimber' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Meán Fómhair' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de setembro' ),
            'he' :      lambda val: dh_noConv( val, u'%d בספטמבר' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. rujna' ),
            'hu' :      lambda val: dh_noConv( val, u'Szeptember %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de septembre' ),
            'id' :      lambda val: dh_noConv( val, u'%d September' ),
            'io' :      lambda val: dh_noConv( val, u'%d di septembro' ),
            'is' :      lambda val: dh_noConv( val, u'%d. september' ),
            'it' :      lambda val: dh_noConv( val, u'%d settembre' ),
            'ja' :      lambda val: dh_noConv( val, u'9月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'9월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê rezberê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Septembris' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. September' ),
            'lt' :      lambda val: dh_noConv( val, u'Rugsėjo %d' ),
            'ml' :      lambda val: dh_noConv( val, u'സപ്തന്പര് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d September' ),
            'nl' :      lambda val: dh_noConv( val, u'%d september' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. september' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. september' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de setembre' ),
            'pl' :      lambda val: dh_noConv( val, u'%d września' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Setembro' ),
            'ro' :      lambda val: dh_noConv( val, u'%d septembrie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d сентября' ),
            'se' :      lambda val: dh_noConv( val, u'čakčamánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. september' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. september' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. септембар' ),
            'sv' :      lambda val: dh_noConv( val, u'%d september' ),
            'tl' :      lambda val: dh_noConv( val, u'Setyembre %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Eylül' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Sentäber' ),
            'uk' :      lambda val: dh_noConv( val, u'%d вересня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d ستمب' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 9' ),
            'wa' :      lambda val: dh_noConv( val, u'%d di setimbe' ),
            'zh' :      lambda val: dh_noConv( val, u'9月%d日' ),
    },
    
    'October': {
            'af' :      lambda val: dh_noConv( val, u'%d Oktober' ),
            'ang':      lambda val: dh_noConv( val, u'%d Winterfylleþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d أكتوبر' ),
            'ast':      lambda val: dh_noConv( val, u"%d d'ochobre" ),
            'be' :      lambda val: dh_noConv( val, u'%d кастрычніка' ),
            'bg' :      lambda val: dh_noConv( val, u'%d октомври' ),
            'bs' :      lambda val: dh_noConv( val, u'Oktobar %d' ),
            'ca' :      lambda val: dh_noConv( val, u"%d d'octubre" ),
            'co' :      lambda val: dh_noConv( val, u"%d d'uttrovi" ),
            'cs' :      lambda val: dh_noConv( val, u'%d. říjen' ),
            'csb':      lambda val: dh_noConv( val, u'%d rujana' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Hydref' ),
            'da' :      lambda val: dh_noConv( val, u'%d. oktober' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Oktober' ),
            'el' :      lambda val: dh_noConv( val, u'%d Οκτωβρίου' ),
            'en' :      lambda val: dh_noConv( val, u'October %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de oktobro' ),
            'es' :      lambda val: dh_noConv( val, u'%d de octubre' ),
            'et' :      lambda val: dh_noConv( val, u'%d. oktoober' ),
            'eu' :      lambda val: dh_noConv( val, u'Urriaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. lokakuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. oktober' ),
            'fr' :      lambda val: dh_noConv( val, u'%d octobre' ),
            'fy' :      lambda val: dh_noConv( val, u'%d oktober' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Deireadh Fómhair' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de outubro' ),
            'he' :      lambda val: dh_noConv( val, u'%d באוקטובר' ),
            'hr' :      lambda val: dh_noConv( val, u'%d. listopada' ),
            'hu' :      lambda val: dh_noConv( val, u'Október %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de octobre' ),
            'id' :      lambda val: dh_noConv( val, u'%d Oktober' ),
            'io' :      lambda val: dh_noConv( val, u'%d di oktobro' ),
            'is' :      lambda val: dh_noConv( val, u'%d. október' ),
            'it' :      lambda val: dh_noConv( val, u'%d ottobre' ),
            'ja' :      lambda val: dh_noConv( val, u'10月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'10월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê kewçêrê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Octobris' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Oktober' ),
            'lt' :      lambda val: dh_noConv( val, u'Spalio %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ഒക്ടോബര് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Oktober' ),
            'nl' :      lambda val: dh_noConv( val, u'%d oktober' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. oktober' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. oktober' ),
            'oc' :      lambda val: dh_noConv( val, u"%d d'octobre" ),
            'pl' :      lambda val: dh_noConv( val, u'%d października' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Outubro' ),
            'ro' :      lambda val: dh_noConv( val, u'%d octombrie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d октября' ),
            'se' :      lambda val: dh_noConv( val, u'golggotmánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. október' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. oktober' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. октобар' ),
            'sv' :      lambda val: dh_noConv( val, u'%d oktober' ),
            'tl' :      lambda val: dh_noConv( val, u'Oktubre %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Ekim' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Öktäber' ),
            'uk' :      lambda val: dh_noConv( val, u'%d жовтня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d اکتوبر' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 10' ),
            'wa' :      lambda val: dh_noConv( val, u"%d d' octôbe" ),
            'zh' :      lambda val: dh_noConv( val, u'10月%d日' ),
    },
    
    'November': {
            'af' :      lambda val: dh_noConv( val, u'%d November' ),
            'ang':      lambda val: dh_noConv( val, u'%d Blótmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d نوفمبر' ),
            'ast':      lambda val: dh_noConv( val, u'%d de payares' ),
            'be' :      lambda val: dh_noConv( val, u'%d лістапада' ),
            'bg' :      lambda val: dh_noConv( val, u'%d ноември' ),
            'bs' :      lambda val: dh_noConv( val, u'Novembar %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de novembre' ),
            'co' :      lambda val: dh_noConv( val, u'%d di nuvembri' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. listopad' ),
            'csb':      lambda val: dh_noConv( val, u'%d lëstopadnika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Tachwedd' ),
            'da' :      lambda val: dh_noConv( val, u'%d. november' ),
            'de' :      lambda val: dh_noConv( val, u'%d. November' ),
            'el' :      lambda val: dh_noConv( val, u'%d Νοεμβρίου' ),
            'en' :      lambda val: dh_noConv( val, u'November %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de novembro' ),
            'es' :      lambda val: dh_noConv( val, u'%d de noviembre' ),
            'et' :      lambda val: dh_noConv( val, u'%d. november' ),
            'eu' :      lambda val: dh_noConv( val, u'Azaroaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. marraskuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. november' ),
            'fr' :      lambda val: dh_noConv( val, u'%d novembre' ),
            'fy' :      lambda val: dh_noConv( val, u'%d novimber' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Samhain' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de novembro' ),
            'he' :      lambda val: dh_noConv( val, u'%d בנובמבר' ),
            'hr' :      lambda val: dh_noConv( val, u'%d studenog' ),
            'hu' :      lambda val: dh_noConv( val, u'November %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de novembre' ),
            'id' :      lambda val: dh_noConv( val, u'%d November' ),
            'io' :      lambda val: dh_noConv( val, u'%d di novembro' ),
            'it' :      lambda val: dh_noConv( val, u'%d novembre' ),
            'is' :      lambda val: dh_noConv( val, u'%d. nóvember' ),
            'ja' :      lambda val: dh_noConv( val, u'11月%d日' ),
            'ko' :      lambda val: dh_noConv( val, u'11월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê sermawezê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Novembris' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. November' ),
            'lt' :      lambda val: dh_noConv( val, u'Lapkričio  %d' ),
            'ml' :      lambda val: dh_noConv( val, u'നവന്പര് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d November' ),
            'nl' :      lambda val: dh_noConv( val, u'%d november' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. november' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. november' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de novembre' ),
            'pl' :      lambda val: dh_noConv( val, u'%d listopada' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Novembro' ),
            'ro' :      lambda val: dh_noConv( val, u'%d noiembrie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d ноября' ),
            'se' :      lambda val: dh_noConv( val, u'skábmamánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. november' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. november' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. новембар' ),
            'sv' :      lambda val: dh_noConv( val, u'%d november' ),
            'tl' :      lambda val: dh_noConv( val, u'Nobyembre %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Kasım' ),
            'tt' :      lambda val: dh_noConv( val, u'%d. Nöyäber' ),
            'uk' :      lambda val: dh_noConv( val, u'%d листопада' ),
            'ur' :      lambda val: dh_noConv( val, u'%d نومب' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 11' ),
            'wa' :      lambda val: dh_noConv( val, u'%d di nôvimbe' ),
            'zh' :      lambda val: dh_noConv( val, u'11月%d日' ),
    },
    
    'December': {
            'af' :      lambda val: dh_noConv( val, u'%d Desember' ),
            'ang':      lambda val: dh_noConv( val, u'%d Géolmónaþ' ),
            'ar' :      lambda val: dh_noConv( val, u'%d ديسمبر' ),
            'ast':      lambda val: dh_noConv( val, u"%d d'avientu" ),
            'be' :      lambda val: dh_noConv( val, u'%d сьнежня' ),
            'bg' :      lambda val: dh_noConv( val, u'%d декември' ),
            'bs' :      lambda val: dh_noConv( val, u'Decembar %d' ),
            'ca' :      lambda val: dh_noConv( val, u'%d de desembre' ),
            'co' :      lambda val: dh_noConv( val, u'%d di decembre' ),
            'cs' :      lambda val: dh_noConv( val, u'%d. prosinec' ),
            'csb':      lambda val: dh_noConv( val, u'%d gòdnika' ),
            'cy' :      lambda val: dh_noConv( val, u'%d Rhagfyr' ),
            'da' :      lambda val: dh_noConv( val, u'%d. december' ),
            'de' :      lambda val: dh_noConv( val, u'%d. Dezember' ),
            'el' :      lambda val: dh_noConv( val, u'%d Δεκεμβρίου' ),
            'en' :      lambda val: dh_noConv( val, u'December %d' ),
            'eo' :      lambda val: dh_noConv( val, u'%d-a de decembro' ),
            'es' :      lambda val: dh_noConv( val, u'%d de diciembre' ),
            'et' :      lambda val: dh_noConv( val, u'%d. detsember' ),
            'eu' :      lambda val: dh_noConv( val, u'Abenduaren %d' ),
            'fi' :      lambda val: dh_noConv( val, u'%d. joulukuuta' ),
            'fo' :      lambda val: dh_noConv( val, u'%d. desember' ),
            'fr' :      lambda val: dh_noConv( val, u'%d décembre' ),
            'fy' :      lambda val: dh_noConv( val, u'%d desimber' ),
            'ga' :      lambda val: dh_noConv( val, u'%d Mí na Nollag' ),
            'gl' :      lambda val: dh_noConv( val, u'%d de decembro' ),
            'he' :      lambda val: dh_noConv( val, u'%d בדצמבר' ),
            'hr' :      lambda val: dh_noConv( val, u'%d prosinca' ),
            'hu' :      lambda val: dh_noConv( val, u'December %d' ),
            'ia' :      lambda val: dh_noConv( val, u'%d de decembre' ),
            'id' :      lambda val: dh_noConv( val, u'%d Desember' ),
            'io' :      lambda val: dh_noConv( val, u'%d di decembro' ),
            'is' :      lambda val: dh_noConv( val, u'%d. desember' ),
            'it' :      lambda val: dh_noConv( val, u'%d dicembre' ),
            'ja' :      lambda val: dh_noConv( val, u'12月%d日' ),
            'ka' :      lambda val: dh_noConv( val, u'%d დეკემბერი' ),
            'ko' :      lambda val: dh_noConv( val, u'12월 %d일' ),
            'ku' :      lambda val: dh_noConv( val, u"%d'ê berfanbarê" ),
            'la' :      lambda val: dh_noConv( val, u'%d Decembris' ),
            'lb' :      lambda val: dh_noConv( val, u'%d. Dezember' ),
            'lt' :      lambda val: dh_noConv( val, u'Gruodžio %d' ),
            'ml' :      lambda val: dh_noConv( val, u'ഡിസന്പര് %d' ),
            'nds':      lambda val: dh_noConv( val, u'%d Dezember' ),
            'nl' :      lambda val: dh_noConv( val, u'%d december' ),
            'nn' :      lambda val: dh_noConv( val, u'%d. desember' ),
#uses template  'no' :      lambda val: dh_noConv( val, u'%d. desember' ),
            'oc' :      lambda val: dh_noConv( val, u'%d de decembre' ),
            'pl' :      lambda val: dh_noConv( val, u'%d grudnia' ),
            'pt' :      lambda val: dh_noConv( val, u'%d de Dezembro' ),
            'ro' :      lambda val: dh_noConv( val, u'%d decembrie' ),
            'ru' :      lambda val: dh_noConv( val, u'%d декабря' ),
            'se' :      lambda val: dh_noConv( val, u'juovlamánu %d.' ),
            'sk' :      lambda val: dh_noConv( val, u'%d. december' ),
            'sl' :      lambda val: dh_noConv( val, u'%d. december' ),
            'sr' :      lambda val: dh_noConv( val, u'%d. децембар' ),
            'sv' :      lambda val: dh_noConv( val, u'%d december' ),
            'tl' :      lambda val: dh_noConv( val, u'Disyembre %d' ),
            'tr' :      lambda val: dh_noConv( val, u'%d Aralık' ),
            'tt' :      lambda val: dh_noConv( val, u'%d.Dekäber' ),
            'uk' :      lambda val: dh_noConv( val, u'%d грудня' ),
            'ur' :      lambda val: dh_noConv( val, u'%d دسمب' ),
            'vi' :      lambda val: dh_noConv( val, u'%d tháng 12' ),
            'wa' :      lambda val: dh_noConv( val, u'%d di decimbe' ),
            'zh' :      lambda val: dh_noConv( val, u'12月%d日' ),
    },
    
    'monthNames': {
            'af' :      lambda val: slh( val, [u'Januarie', u'Februarie', u'Maart', u'April', u'Mei', u'Junie', u'Julie', u'Augustus', u'September', u'Oktober', u'November', u'Desember'] ),
            'als':      lambda val: slh( val, [u'Januar', u'Februar', u'März', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            'an' :      lambda val: slh( val, [u'Chinero', u'Frebero', u'Marzo', u'Abril', u'Mayo', u'Chunio', u'Chulio', u'Agosto', u'Setiembre', u'Otubre', u'Nobiembre', u'Abiento'] ),
            'ang':      lambda val: slh( val, [u'Se æfterra Gēola', u'Solmónaþ', u'Hrēþmōnaþ', u'Ēastermōnaþ', u'Þrimilcemónaþ', u'Séremónaþ', u'Mǽdmónaþ', u'Wéodmónaþ', u'Háligmónaþ', u'Winterfylleþ', u'Blótmónaþ', u'Géolmónaþ'] ),
            'ar' :      lambda val: slh( val, [u'يناير', u'فبراير', u'مارس', u'إبريل', u'مايو', u'يونيو', u'يوليو', u'أغسطس', u'سبتمبر', u'أكتوبر', u'نوفمبر', u'ديسمبر'] ),
            'ast':      lambda val: slh( val, [u'Xineru', u'Febreru', u'Marzu', u'Abril', u'Mayu', u'Xunu', u'Xunetu', u'Agostu', u'Setiembre', u'Ochobre', u'Payares', u'Avientu'] ),
            'be' :      lambda val: slh( val, [u'Студзень', u'Люты', u'Сакавік', u'Красавік', u'Травень', u'Чэрвень', u'Ліпень', u'Жнівень', u'Верасень', u'Кастрычнік', u'Лістапад', u'Сьнежань'] ),
            'bg' :      lambda val: slh( val, [u'Януари', u'Февруари', u'Март', u'Април', u'Май', u'Юни', u'Юли', u'Август', u'Септември', u'Октомври', u'Ноември', u'Декември'] ),
            'bs' :      lambda val: slh( val, [u'Januar', u'Februar', u'Mart', u'April', u'Maj', u'Juni', u'Juli', u'Avgust', u'Septembar', u'Oktobar', u'Novembar', u'Decembar'] ),
            'ca' :      lambda val: slh( val, [u'Gener', u'Febrer', u'Març', u'Abril', u'Maig', u'Juny', u'Juliol', u'Agost', u'Setembre', u'Octubre', u'Novembre', u'Desembre'] ),
            'cs' :      lambda val: slh( val, [u'Leden', u'Únor', u'Březen', u'Duben', u'Květen', u'Červen', u'Červenec', u'Srpen', u'Září', u'Říjen', u'Listopad', u'Prosinec'] ),
            'csb':      lambda val: slh( val, [u'Stëcznik', u'Gromicznik', u'Strumiannik', u'Łżëkwiôt', u'Môj', u'Czerwińc', u'Lëpinc', u'Zélnik', u'Séwnik', u'Rujan', u'Lëstopadnik', u'Gòdnik'] ),
            'cv' :      lambda val: slh( val, [u'Кăрлач', u'Нарăс', u'Пуш', u'Ака', u'Çу', u'Çěртме', u'Утă', u'Çурла', u'Авăн', u'Юпа', u'Чӳк', u'Раштав'] ),
            'cy' :      lambda val: slh( val, [u'Ionawr', u'Chwefror', u'Mawrth', u'Ebrill', u'Mai', u'Mehefin', u'Gorffennaf', u'Awst', u'Medi', u'Hydref', u'Tachwedd', u'Rhagfyr'] ),
            'da' :      lambda val: slh( val, [u'Januar', u'Februar', u'Marts', u'April', u'Maj', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'December'] ),
            'de' :      lambda val: slh( val, [u'Januar', u'Februar', u'März', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            'el' :      lambda val: slh( val, [u'Ιανουάριος', u'Φεβρουάριος', u'Μάρτιος', u'Απρίλιος', u'Μάιος', u'Ιούνιος', u'Ιούλιος', u'Αύγουστος', u'Σεπτέμβριος', u'Οκτώβριος', u'Νοέμβριος', u'Δεκέμβριος'] ),
            'en' :      lambda val: slh( val, monthNames ),
            'eo' :      lambda val: slh( val, [u'Januaro', u'Februaro', u'Marto', u'Aprilo', u'Majo', u'Junio', u'Julio', u'Aŭgusto', u'Septembro', u'Oktobro', u'Novembro', u'Decembro'] ),
            'es' :      lambda val: slh( val, [u'Enero', u'Febrero', u'Marzo', u'Abril', u'Mayo', u'Junio', u'Julio', u'Agosto', u'Septiembre', u'Octubre', u'Noviembre', u'Diciembre'] ),
            'et' :      lambda val: slh( val, [u'Jaanuar', u'Veebruar', u'Märts', u'Aprill', u'Mai', u'Juuni', u'Juuli', u'August', u'September', u'Oktoober', u'November', u'Detsember'] ),
            'eu' :      lambda val: slh( val, [u'Urtarril', u'Otsail', u'Martxo', u'Apiril', u'Maiatz', u'Ekain', u'Uztail', u'Abuztu', u'Irail', u'Urri', u'Azaro', u'Abendu'] ),
            'fa' :      lambda val: slh( val, [u'ژانویه', u'فوریه', u'مارس', u'آوریل', u'مه', u'ژوئن', u'ژوئیه', u'اوت', u'سپتامبر', u'اکتبر', u'نوامبر', u'دسامبر'] ),
            'fi' :      lambda val: slh( val, [u'Tammikuu', u'Helmikuu', u'Maaliskuu', u'Huhtikuu', u'Toukokuu', u'Kesäkuu', u'Heinäkuu', u'Elokuu', u'Syyskuu', u'Lokakuu', u'Marraskuu', u'Joulukuu'] ),
            'fo' :      lambda val: slh( val, [u'Januar', u'Februar', u'Mars', u'Apríl', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Desember'] ),
            'fr' :      lambda val: slh( val, [u'Janvier', u'Février', u'Mars (mois)', u'Avril', u'Mai', u'Juin', u'Juillet', u'Août', u'Septembre', u'Octobre', u'Novembre', u'Décembre'] ),
            'fur':      lambda val: slh( val, [u'Zenâr', u'Fevrâr', u'Març', u'Avrîl', u'Mai', u'Zugn', u'Lui', u'Avost', u'Setembar', u'Otubar', u'Novembar', u'Dicembar'] ),
            'fy' :      lambda val: slh( val, [u'Jannewaris', u'Febrewaris', u'Maart', u'April', u'Maaie', u'Juny', u'July', u'Augustus', u'Septimber', u'Oktober', u'Novimber', u'Desimber'] ),
            'ga' :      lambda val: slh( val, [u'Eanáir', u'Feabhra', u'Márta', u'Aibreán', u'Bealtaine', u'Meitheamh', u'Iúil', u'Lúnasa', u'Meán Fómhair', u'Deireadh Fómhair', u'Samhain', u'Nollaig'] ),
            'gl' :      lambda val: slh( val, [u'Xaneiro', u'Febreiro', u'Marzo', u'Abril', u'Maio', u'Xuño', u'Xullo', u'Agosto', u'Setembro', u'Outubro', u'Novembro', u'Decembro'] ),
            'he' :      lambda val: slh( val, [u'ינואר', u'פברואר', u'מרץ', u'אפריל', u'מאי', u'יוני', u'יולי', u'אוגוסט', u'ספטמבר', u'אוקטובר', u'נובמבר', u'דצמבר'] ),
            'hr' :      lambda val: slh( val, [u'Siječanj', u'Veljača', u'Ožujak', u'Travanj', u'Svibanj', u'Lipanj', u'Srpanj', u'Kolovoz', u'Rujan', u'Listopad', u'Studeni', u'Prosinac'] ),
            'hu' :      lambda val: slh( val, [u'Január', u'Február', u'Március', u'Április', u'Május', u'Június', u'Július', u'Augusztus', u'Szeptember', u'Október', u'November', u'December'] ),
            'ia' :      lambda val: slh( val, [u'Januario', u'Februario', u'Martio', u'April', u'Maio', u'Junio', u'Julio', u'Augusto', u'Septembre', u'Octobre', u'Novembre', u'Decembre'] ),
            'id' :      lambda val: slh( val, [u'Januari', u'Februari', u'Maret', u'April', u'Mei', u'Juni', u'Juli', u'Agustus', u'September', u'Oktober', u'November', u'Desember'] ),
            'ie' :      lambda val: slh( val, [u'Januar', u'Februar', u'Marte', u'April', u'May', u'Junio', u'Juli', u'August', u'Septembre', u'Octobre', u'Novembre', u'Decembre'] ),
            'io' :      lambda val: slh( val, [u'Januaro', u'Februaro', u'Marto', u'Aprilo', u'Mayo', u'Junio', u'Julio', u'Agosto', u'Septembro', u'Oktobro', u'Novembro', u'Decembro'] ),
            'is' :      lambda val: slh( val, [u'Janúar', u'Febrúar', u'Mars (mánuður)', u'Apríl', u'Maí', u'Júní', u'Júlí', u'Ágúst', u'September', u'Október', u'Nóvember', u'Desember'] ),
            'it' :      lambda val: slh( val, [u'Gennaio', u'Febbraio', u'Marzo', u'Aprile', u'Maggio', u'Giugno', u'Luglio', u'Agosto', u'Settembre', u'Ottobre', u'Novembre', u'Dicembre'] ),
            'ja' :      lambda val: slh( val, [u'1月', u'2月', u'3月', u'4月', u'5月', u'6月', u'7月', u'8月', u'9月', u'10月', u'11月', u'12月'] ),
            'jv' :      lambda val: slh( val, [u'Januari', u'Februari', u'Maret', u'April', u'Mei', u'Juni', u'Juli', u'Agustus', u'September', u'Oktober', u'November', u'Desember'] ),
            'ka' :      lambda val: slh( val, [u'იანვარი', u'თებერვალი', u'მარტი', u'აპრილი', u'მაისი', u'ივნისი', u'ივლისი', u'აგვისტო', u'სექტემბერი', u'ოქტომბერი', u'ნოემბერი', u'დეკემბერი'] ),
            'kn' :      lambda val: slh( val, [u'ಜನವರಿ', u'ಫೆಬ್ರವರಿ', u'ಮಾರ್ಚಿ', u'ಎಪ್ರಿಲ್', u'ಮೇ', u'ಜೂನ', u'ಜುಲೈ', u'ಆಗಸ್ಟ್ ', u'ಸೆಪ್ಟೆಂಬರ್', u'ಅಕ್ಟೋಬರ್', u'ನವೆಂಬರ್', u'ಡಿಸೆಂಬರ್'] ),
            'ko' :      lambda val: slh( val, [u'1월', u'2월', u'3월', u'4월', u'5월', u'6월', u'7월', u'8월', u'9월', u'10월', u'11월', u'12월'] ),
            'ku' :      lambda val: slh( val, [u'Rêbendan', u'Reşemî', u'Adar', u'Avrêl', u'Gulan', u'Pûşper', u'Tîrmeh', u'Gelawêj (meh)', u'Rezber', u'Kewçêr', u'Sermawez', u'Berfanbar'] ),
            'kw' :      lambda val: slh( val, [u'Mys Genver', u'Mys Whevrer', u'Mys Merth', u'Mys Ebrel', u'Mys Me', u'Mys Metheven', u'Mys Gortheren', u'Mys Est', u'Mys Gwyngala', u'Mys Hedra', u'Mys Du', u'Mys Kevardhu'] ),
            'la' :      lambda val: slh( val, [u'Ianuarius', u'Februarius', u'Martius', u'Aprilis', u'Maius', u'Iunius', u'Iulius', u'Augustus (mensis)', u'September', u'October', u'November', u'December'] ),
            'lb' :      lambda val: slh( val, [u'Januar', u'Februar', u'Mäerz', u'Abrëll', u'Mee', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            'li' :      lambda val: slh( val, [u'Jannewarie', u'Fibberwarie', u'Miert', u'April', u'Mei', u'Juni', u'Juli', u'Augustus (maond)', u'September', u'Oktober', u'November', u'December'] ),
            'lt' :      lambda val: slh( val, [u'Sausis', u'Vasaris', u'Kovas', u'Balandis', u'Gegužė', u'Birželis', u'Liepa', u'Rugpjūtis', u'Rugsėjis', u'Spalis', u'Lapkritis', u'Gruodis'] ),
            'mi' :      lambda val: slh( val, [u'Kohi-tātea', u'Hui-tanguru', u'Poutū-te-rangi', u'Paenga-whāwhā', u'Haratua', u'Pipiri', u'Hōngongoi', u'Here-turi-kōkā', u'Mahuru', u'Whiringa-ā-nuku', u'Whiringa-ā-rangi', u'Hakihea'] ),
            'mr' :      lambda val: slh( val, [u'जानेवारी', u'फेब्रुवारी', u'मार्च', u'एप्रिल', u'मे', u'जून', u'जुलै', u'ऑगस्ट', u'सप्टेंबर', u'ऑक्टोबर', u'नोव्हेंबर', u'डिसेंबर'] ),
            'ms' :      lambda val: slh( val, [u'Januari', u'Februari', u'Mac', u'April', u'Mei', u'Jun', u'Julai', u'Ogos', u'September', u'Oktober', u'November', u'Disember'] ),
            'nl' :      lambda val: slh( val, [u'Januari', u'Februari', u'Maart', u'April', u'Mei', u'Juni', u'Juli', u'Augustus (maand)', u'September', u'Oktober', u'November', u'December'] ),
            'nn' :      lambda val: slh( val, [u'Januar', u'Februar', u'Mars', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Desember'] ),
            'no' :      lambda val: slh( val, [u'Januar', u'Februar', u'Mars', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Desember'] ),
            'oc' :      lambda val: slh( val, [u'Genièr', u'Febrièr', u'Març', u'Abril', u'Mai', u'Junh', u'Julhet', u'Agost', u'Setembre', u'Octobre', u'Novembre', u'Decembre'] ),
            'pl' :      lambda val: slh( val, [u'Styczeń', u'Luty', u'Marzec', u'Kwiecień', u'Maj', u'Czerwiec', u'Lipiec', u'Sierpień', u'Wrzesień', u'Październik', u'Listopad', u'Grudzień'] ),
            'pt' :      lambda val: slh( val, [u'Janeiro', u'Fevereiro', u'Março', u'Abril', u'Maio', u'Junho', u'Julho', u'Agosto', u'Setembro', u'Outubro', u'Novembro', u'Dezembro'] ),
            'ro' :      lambda val: slh( val, [u'Ianuarie', u'Februarie', u'Martie', u'Aprilie', u'Mai', u'Iunie', u'Iulie', u'August', u'Septembrie', u'Octombrie', u'Noiembrie', u'Decembrie'] ),
            'ru' :      lambda val: slh( val, [u'Январь', u'Февраль', u'Март', u'Апрель', u'Май', u'Июнь', u'Июль', u'Август', u'Сентябрь', u'Октябрь', u'Ноябрь', u'Декабрь'] ),
            'scn':      lambda val: slh( val, [u'Jinnaru', u'Frivaru', u'Marzu', u'Aprili', u'Maiu', u'Giugnu', u'Giugnettu', u'Austu', u'Sittemmiru', u'Uttuviru', u'Nuvemmiru', u'Dicemmiru'] ),
            'sco':      lambda val: slh( val, [u'Januar', u'Februar', u'Mairch', u'Aprile', u'Mey', u'Juin', u'Julie', u'Augist', u'September', u'October', u'November', u'December'] ),
            'se' :      lambda val: slh( val, [u'Ođđajagimánnu', u'Guovvamánnu', u'Njukčamánnu', u'Cuoŋománnu', u'Miessemánnu', u'Geassemánnu', u'Suoidnemánnu', u'Borgemánnu', u'Čakčamánnu', u'Golggotmánnu', u'Skábmamánnu', u'Juovlamánnu'] ),
            'simple' :      lambda val: slh( val, monthNames ),
            'sk' :      lambda val: slh( val, [u'Január', u'Február', u'Marec', u'Apríl', u'Máj', u'Jún', u'Júl', u'August', u'September', u'Október', u'November', u'December'] ),
            'sl' :      lambda val: slh( val, [u'Januar', u'Februar', u'Marec', u'April', u'Maj', u'Junij', u'Julij', u'Avgust', u'September', u'Oktober', u'November', u'December'] ),
            'sq' :      lambda val: slh( val, [u'Janari', u'Shkurti', u'Marsi (muaj)', u'Prilli', u'Maji', u'Qershori', u'Korriku', u'Gushti', u'Shtatori', u'Tetori', u'Nëntori', u'Dhjetori'] ),
            'sr' :      lambda val: slh( val, [u'Јануар', u'Фебруар', u'Март', u'Април', u'Мај', u'Јун', u'Јул', u'Август', u'Септембар', u'Октобар', u'Новембар', u'Децембар'] ),
            'su' :      lambda val: slh( val, [u'Januari', u'Pébruari', u'Maret', u'April', u'Méi', u'Juni', u'Juli', u'Agustus', u'Séptémber', u'Oktober', u'Nopémber', u'Désémber'] ),
            'sv' :      lambda val: slh( val, [u'Januari', u'Februari', u'Mars', u'April', u'Maj', u'Juni', u'Juli', u'Augusti', u'September', u'Oktober', u'November', u'December'] ),
            'th' :      lambda val: slh( val, [u'มกราคม', u'กุมภาพันธ์', u'มีนาคม', u'เมษายน', u'พฤษภาคม', u'มิถุนายน', u'กรกฎาคม', u'สิงหาคม', u'กันยายน', u'ตุลาคม', u'พฤศจิกายน', u'ธันวาคม'] ),
            'tl' :      lambda val: slh( val, [u'Enero', u'Pebrero', u'Marso', u'Abril', u'Mayo', u'Hunyo', u'Hulyo', u'Agosto', u'Setyembre', u'Oktubre', u'Nobyembre', u'Disyembre'] ),
            'tpi':      lambda val: slh( val, [u'Janueri', u'Februeri', u'Mas', u'Epril', u'Me', u'Jun', u'Julai', u'Ogas', u'Septemba', u'Oktoba', u'Novemba', u'Disemba'] ),
            'tr' :      lambda val: slh( val, [u'Ocak', u'Şubat', u'Mart', u'Nisan', u'Mayıs', u'Haziran', u'Temmuz', u'Ağustos', u'Eylül', u'Ekim', u'Kasım', u'Aralık'] ),
            'tt' :      lambda val: slh( val, [u'Ğínwar', u'Febräl', u'Mart', u'Äpril', u'May', u'Yün', u'Yül', u'August', u'Sentäber', u'Öktäber', u'Nöyäber', u'Dekäber'] ),
            'uk' :      lambda val: slh( val, [u'Січень', u'Лютий', u'Березень', u'Квітень', u'Травень', u'Червень', u'Липень', u'Серпень', u'Вересень', u'Жовтень', u'Листопад', u'Грудень'] ),
            'ur' :      lambda val: slh( val, [u'جنوری', u'فروری', u'مارچ', u'اپريل', u'مئ', u'جون', u'جولائ', u'اگست', u'ستمبر', u'اکتوبر', u'نومبر', u'دسمبر'] ),
            'vi' :      lambda val: slh( val, [u'Tháng một', u'Tháng hai', u'Tháng ba', u'Tháng tư', u'Tháng năm', u'Tháng sáu', u'Tháng bảy', u'Tháng tám', u'Tháng chín', u'Tháng mười', u'Tháng mười một', u'Tháng mười hai'] ),
            'vo' :      lambda val: slh( val, [u'Yanul', u'Febul', u'Mäzul', u'Prilul', u'Mayul', u'Yunul', u'Yulul', u'Gustul', u'Setul', u'Tobul', u'Novul', u'Dekul'] ),
            'wa' :      lambda val: slh( val, [u'Djanvî', u'Fevrî', u'Måss', u'Avri', u'May', u'Djun', u'Djulete', u'Awousse', u'Setimbe', u'Octôbe', u'Nôvimbe', u'Decimbe'] ),
            'zh' :      lambda val: slh( val, [u'1月', u'2月', u'3月', u'4月', u'5月', u'6月', u'7月', u'8月', u'9月', u'10月', u'11月', u'12月'] ),

            # 'sc' :      lambda val: slh( val, [u'Ghennarzu', u'Frearzu', u'Martzu', u'', u'', u'', u'', u'', u'', u'', u'', u''] ),
            # 'hi' :      lambda val: slh( val, [u'', u'', u'', u'', u'मई', u'', u'', u'', u'', u'', u'', u''] ),
            # 'ml' :      lambda val: slh( val, [u'', u'', u'', u'', u'', u'ജൂണ്‍', u'', u'', u'', u'', u'', u''] ),
    },
    
    'yearsAD': {
        'af' :      lambda val: dh_noConv( val, u'%d' ),
        'ast':      lambda val: dh_noConv( val, u'%d' ),
        'be' :      lambda val: dh_noConv( val, u'%d' ),
        'bg' :      lambda val: dh_noConv( val, u'%d' ),
        'bs' :      lambda val: dh_noConv( val, u'%d' ),
        'ca' :      lambda val: dh_noConv( val, u'%d' ),
        'cs' :      lambda val: dh_noConv( val, u'%d' ),
        'csb':      lambda val: dh_noConv( val, u'%d' ),
        'cy' :      lambda val: dh_noConv( val, u'%d' ),
        'da' :      lambda val: dh_noConv( val, u'%d' ),
        'de' :      lambda val: dh_noConv( val, u'%d' ),
        'el' :      lambda val: dh_noConv( val, u'%d' ),
        'en' :      lambda val: dh_noConv( val, u'%d' ),
        'eo' :      lambda val: dh_noConv( val, u'%d' ),
        'es' :      lambda val: dh_noConv( val, u'%d' ),
        'et' :      lambda val: dh_noConv( val, u'%d' ),
        'eu' :      lambda val: dh_noConv( val, u'%d' ),
        'fi' :      lambda val: dh_noConv( val, u'%d' ),
        'fo' :      lambda val: dh_noConv( val, u'%d' ),
        'fr' :      lambda val: dh_noConv( val, u'%d' ),
        'fy' :      lambda val: dh_noConv( val, u'%d' ),
        'gl' :      lambda val: dh_noConv( val, u'%d' ),
        'he' :      lambda val: dh_noConv( val, u'%d' ),
        'hr' :      lambda val: dh_noConv( val, u'%d' ),
        'hu' :      lambda val: dh_noConv( val, u'%d' ),
        'ia' :      lambda val: dh_noConv( val, u'%d' ),
        'id' :      lambda val: dh_noConv( val, u'%d' ),
        'io' :      lambda val: dh_noConv( val, u'%d' ),
        'is' :      lambda val: dh_noConv( val, u'%d' ),
        'it' :      lambda val: dh_noConv( val, u'%d' ),
        'ja' :      lambda val: dh_noConv( val, u'%d年' ),
        'ka' :      lambda val: dh_noConv( val, u'%d' ),
        'ko' :      lambda val: dh_noConv( val, u'%d년' ),
        'ku' :      lambda val: dh_noConv( val, u'%d' ),
        'kw' :      lambda val: dh_noConv( val, u'%d' ),
        'la' :      lambda val: dh_noConv( val, u'%d' ),
        'lb' :      lambda val: dh_noConv( val, u'%d' ),
        'lt' :      lambda val: dh_noConv( val, u'%d' ),
        'mi' :      lambda val: dh_noConv( val, u'%d' ),
        'minnan' :  lambda val: dh_noConv( val, u'%d nî' ),
        'nb' :      lambda val: dh_noConv( val, u'%d' ),
        'nds':      lambda val: dh_noConv( val, u'%d' ),
        'nl' :      lambda val: dh_noConv( val, u'%d' ),
        'nn' :      lambda val: dh_noConv( val, u'%d' ),
        'no' :      lambda val: dh_noConv( val, u'%d' ),
        'os' :      lambda val: dh_noConv( val, u'%d' ),
        'pl' :      lambda val: dh_noConv( val, u'%d' ),
        'pt' :      lambda val: dh_noConv( val, u'%d' ),
        'ro' :      lambda val: dh_noConv( val, u'%d' ),
        'ru' :      lambda val: dh_noConv( val, u'%d' ),
        'simple' :  lambda val: dh_noConv( val, u'%d' ),
        'sk' :      lambda val: dh_noConv( val, u'%d' ),
        'sl' :      lambda val: dh_noConv( val, u'%d' ),
        'sr' :      lambda val: dh_noConv( val, u'%d' ),
        'sv' :      lambda val: dh_noConv( val, u'%d' ),
        'th' :      lambda val: dh_thai_solar_calendar( val, u'พ.ศ. %d' ),
        'tr' :      lambda val: dh_noConv( val, u'%d' ),
        'tt' :      lambda val: dh_noConv( val, u'%d' ),
        'uk' :      lambda val: dh_noConv( val, u'%d' ),
        'ur' :      lambda val: dh_noConv( val, u'%dسبم' ),
        'wa' :      lambda val: dh_noConv( val, u'%d' ),
        'zh' :      lambda val: dh_noConv( val, u'%d年' ),
    },

    'yearsBC': {
        'af' :      lambda val: dh_noConv( val, u'%d v.C.' ),       # original - '%d v.Chr.'
        'bg' :      lambda val: dh_noConv( val, u'%d г. пр.н.е.' ),
        'bs' :      lambda val: dh_noConv( val, u'%d p.ne.' ),
        'ca' :      lambda val: dh_noConv( val, u'%d aC' ),
        'da' :      lambda val: dh_noConv( val, u'%d f.Kr.' ),
        'de' :      lambda val: dh_noConv( val, u'%d v. Chr.' ),
        'en' :      lambda val: dh_noConv( val, u'%d BC' ),
        'eo' :      lambda val: dh_noConv( val, u'-%d' ),
        'es' :      lambda val: dh_noConv( val, u'%d adC' ),
        'et' :      lambda val: dh_noConv( val, u'%d eKr' ),
        'fi' :      lambda val: dh_noConv( val, u'%d eaa' ),
        'fo' :      lambda val: dh_noConv( val, u'%d f. Kr.' ),
        'fr' :      lambda val: dh_noConv( val, u'-%d' ),
        'he' :      lambda val: dh_noConv( val, u'%d לפנה"ס' ),
        'hr' :      lambda val: dh_noConv( val, u'%d p.n.e.' ),
        'id' :      lambda val: dh_noConv( val, u'%d SM' ),
        'is' :      lambda val: dh_noConv( val, u'%d f. Kr.' ),
        'it' :      lambda val: dh_noConv( val, u'%d AC' ),
        'ko' :      lambda val: dh_noConv( val, u'기원전 %d년' ),
        'la' :      lambda val: dh_noConv( val, u'%d a.C.n' ),
        'lb' :      lambda val: dh_noConv( val, u'-%d' ),
        'nds':      lambda val: dh_noConv( val, u'%d v. Chr.' ),
        'nl' :      lambda val: dh_noConv( val, u'%d v. Chr.' ),
        'nn' :      lambda val: dh_noConv( val, u'-%d' ),
        'no' :      lambda val: dh_noConv( val, u'%d f.Kr.' ),
        'pl' :      lambda val: dh_noConv( val, u'%d p.n.e.' ),
        'pt' :      lambda val: dh_noConv( val, u'%d a.C.' ),
        'ro' :      lambda val: dh_noConv( val, u'%d î.Hr.' ),
        'ru' :      lambda val: dh_noConv( val, u'%d до н. э.' ),
        'sl' :      lambda val: dh_noConv( val, u'%d pr. n. št.' ),
        'sr' :      lambda val: dh_noConv( val, u'%d. пне.' ),
        'sv' :      lambda val: dh_noConv( val, u'%d f.Kr.' ),
        'uk' :      lambda val: dh_noConv( val, u'%d до Р.Х.' ),
        'zh' :      lambda val: dh_noConv( val, u'前%d年' ),
    },

    'decadesAD': {
        'bg' :      lambda val: dh_dec( val, u'%d-те' ),
        'ca' :      lambda val: dh_dec( val, u'Dècada del %d' ),
        'cy' :      lambda val: dh_dec( val, u'%dau' ),
        'da' :      lambda val: dh_dec( val, u"%d'erne" ),
        'de' :      lambda val: dh_dec( val, u'%der' ),
        'el' :      lambda val: dh_dec( val, u'Δεκαετία %d' ),
        'en' :      lambda val: dh_dec( val, u'%ds' ),
        'eo' :      lambda val: dh_dec( val, u'%d-aj jaroj' ),
        'es' :      lambda val: dh_dec( val, u'Años %d' ),
        'et' :      lambda val: dh_dec( val, u'%d. aastad' ),
        'fi' :      lambda val: dh_dec( val, u'%d-luku' ),
        'fr' :      lambda val: dh_dec( val, u'Années %d' ),
        
        #1970s => '1971–1980'
        'is' :      lambda val: dh( val, u'%d–%d',                   lambda i: (dec1(i),dec1(i)+9), lambda v: v[0]-1 ),
        'it' :      lambda val: dh_dec( val, u'Anni %d' ),
        'ja' :      lambda val: dh_dec( val, u'%d年代' ),
        'ko' :      lambda val: dh_dec( val, u'%d년대' ),
        
        #1970s => 'Decennium 198' (1971-1980)
        'la' :      lambda val: dh( val, u'Decennium %d',            lambda i: dec1(i)/10+1, lambda v: (v[0]-1)*10 ),
        
        #1970s => 'XX amžiaus 8-as dešimtmetis' (1971-1980)
        'lt' :      lambda val: dh( val, u'%s amžiaus %d-as dešimtmetis',
                        lambda i: (romanNums[dec1(i)/100+1], dec1(i)%100/10+1),
                        lambda v: (v[0]-1)*100 + (v[1]-1)*10 ),
        
        #1970s => 'Ngahurutanga 198' (1971-1980)
        'mi' :      lambda val: dh( val, u'Ngahurutanga %d',         lambda i: dec0(i)/10+1, lambda v: (v[0]-1)*10 ),

        #1970s => '1970-1979'
        'nl' :      lambda val: dh( val, u'%d-%d',                   lambda i: (dec0(i),dec0(i)+9), singleVal ),
        'no' :      lambda val: dh_dec( val, u'%d-årene' ),
        
        #1970s => 'Lata 70. XX wieku'
        'pl' :      lambda val: dh( val, u'Lata %d. %s wieku',
                    lambda i: (dec0(i)%100, romanNums[ dec0(i)/100+1 ]),
                    lambda v: (v[1]-1)*100 + v[0] ),
                    
        'pt' :      lambda val: dh_dec( val, u'Década de %d' ),
        'ro' :      lambda val: dh_dec( val, u'Anii %d' ),
        'ru' :      lambda val: dh_dec( val, u'%d-е' ),
        'simple' :  lambda val: dh_dec( val, u'%ds' ),
        
        # 1970 => '70. roky 20. storočia'
        'sk' :      lambda val: dh( val, u'%d. roky %d. storočia',
                    lambda i: (dec0(i)%100, dec0(i)/100+1),
                    lambda v: (v[1]-1)*100 + v[0] ),

        'sl' :      lambda val: dh_dec( val, u'%d.' ),
        'sv' :      lambda val: dh_dec( val, u'%d-talet' ),
        'zh' :      lambda val: dh_dec( val, u'%d年代' ),
    },

    'decadesBC': {
        'de' :      lambda val: dh_dec( val, u'%der v. Chr.' ),
        'en' :      lambda val: dh_dec( val, u'%ds BC' ),
        'es' :      lambda val: dh_dec( val, u'Años %d adC' ),
        'fr' :      lambda val: dh_dec( val, u'Années -%d' ),
        'it' :      lambda val: dh_dec( val, u'Anni %d AC' ),
        'pt' :      lambda val: dh_dec( val, u'Década de %d a.C.' ),
        'ru' :      lambda val: dh_dec( val, u'%d-е до н. э.' ),
        'sl' :      lambda val: dh_dec( val, u'%d. pr. n. št.' ),
    },

    'centuriesAD': {
        'af' :      lambda val: dh_noConv( val, u'%dste eeu' ),
        'ang':      lambda val: dh_noConv( val, u'%de géarhundred' ),
        'ast':      lambda val: dh_roman( val, u'Sieglu %s' ),
        'be' :      lambda val: dh_noConv( val, u'%d стагодзьдзе' ),
        'bg' :      lambda val: dh_noConv( val, u'%d век' ),
        'ca' :      lambda val: dh_roman( val, u'Segle %s' ),
        'cs' :      lambda val: dh_noConv( val, u'%d. století' ),
        'da' :      lambda val: dh_noConv( val, u'%d. århundrede' ),
        'de' :      lambda val: dh_noConv( val, u'%d. Jahrhundert' ),
        'el' :      lambda val: dh_noConv( val, u'%dος αιώνας' ),
        'en' :      lambda val: dh_noConv( val, u'%dth century' ),
        'eo' :      lambda val: dh_noConv( val, u'%d-a jarcento' ),
        'es' :      lambda val: dh_roman( val, u'Siglo %s' ),
        'et' :      lambda val: dh_noConv( val, u'%d. sajand' ),
        'fi' :      lambda val: dh( val, u'%d00-luku',                   lambda i: i-1, lambda v: v[0]+1 ),
        'fr' :      lambda val: dh_roman( val, u'%se siècle' ),
        'fy' :      lambda val: dh_noConv( val, u'%de ieu' ),
        'he' :      lambda val: dh_noConv( val, u'המאה ה-%d' ),
        #'hi' : u'बीसवी शताब्दी'
        'hr' :      lambda val: dh_noConv( val, u'%d. stoljeće' ),
        'io' :      lambda val: dh_noConv( val, u'%dma yar-cento' ),
        'it' :      lambda val: dh_roman( val, u'%s secolo' ),
        'ja' :      lambda val: dh_noConv( val, u'%d世紀' ),
        'ko' :      lambda val: dh_noConv( val, u'%d세기' ),
        'la' :      lambda val: dh_noConv( val, u'Saeculum %d' ),
        'lb' :      lambda val: dh_noConv( val, u'%d. Joerhonnert' ),
        #'li': u'Twintegste ieuw'
        'lt' :      lambda val: dh_roman( val, u'%s amžius' ),
        'mi' :      lambda val: dh_noConv( val, u'Tua %d rau tau' ),
        'nl' :      lambda val: dh_noConv( val, u'%de eeuw' ),
        'no' :      lambda val: dh_noConv( val, u'%d. århundre' ),
        'pl' :      lambda val: dh_roman( val, u'%s wiek' ),
        'pt' :      lambda val: dh_roman( val, u'Século %s' ),
        'ro' :      lambda val: dh_roman( val, u'Secolul al %s-lea' ),
        'ru' :      lambda val: dh_roman( val, u'%s век' ),
        'simple' :  lambda val: dh_noConv( val, u'%dth century' ),
        'sk' :      lambda val: dh_noConv( val, u'%d. storočie' ),
        'sl' :      lambda val: dh_noConv( val, u'%d. stoletje' ),
        'sv' :      lambda val: dh( val, u'%d00-talet',                   lambda i: i-1, lambda v: v[0]+1 ),
        'tr' :      lambda val: dh_noConv( val, u'%d. yüzyıl' ),
        'uk' :      lambda val: dh_noConv( val, u'%d століття' ),
        'wa' :      lambda val: dh_noConv( val, u'%dinme sieke' ),
        'zh' :      lambda val: dh_noConv( val, u'%d世纪' ),
    },

    'centuriesBC': {
        'af' :      lambda val: dh_noConv( val, u'%de eeu v. C.' ),
        'ca' :      lambda val: dh_roman( val, u'Segle %s aC' ),
        'da' :      lambda val: dh_noConv( val, u'%d. århundrede f.Kr.' ),
        'de' :      lambda val: dh_noConv( val, u'%d. Jahrhundert v. Chr.' ),
        'en' :      lambda val: dh_noConv( val, u'%dth century BC' ),
        'eo' :      lambda val: dh_noConv( val, u'%d-a jarcento a.K.' ),
        'es' :      lambda val: dh_roman( val, u'Siglo %s adC' ),   
        'fr' :      lambda val: dh_roman( val, u'%se siècle av. J.-C.' ),
        'it' :      lambda val: dh_roman( val, u'%s secolo AC' ),
        'ja' :      lambda val: dh_noConv( val, u'紀元前%d世紀' ),
        'nl' :      lambda val: dh_noConv( val, u'%de eeuw v. Chr.' ),
        'pl' :      lambda val: dh_roman( val, u'%s wiek p.n.e.' ),
        'ru' :      lambda val: dh_roman( val, u'%s век до н. э.' ),
        'sl' :      lambda val: dh_noConv( val, u'%d. stoletje pr. n. št.' ),
        'zh' :      lambda val: dh_noConv( val, u'前%d世纪' ),
    },

    'milleniumsAD': {
        'bg' :      lambda val: dh_noConv( val, u'%d хилядолетие' ),
        'de' :      lambda val: dh_noConv( val, u'%d. Jahrtausend' ),
        'el' :      lambda val: dh_noConv( val, u'%dη χιλιετία' ),
        'en' :      lambda val: dh_noConv( val, u'%dnd millennium' ),
        'es' :      lambda val: dh_roman( val, u'%s milenio' ),
        'fr' :      lambda val: dh_roman( val, u'%se millénaire' ),
        'it' :      lambda val: dh_roman( val, u'%s millennio' ),
        'ja' :      lambda val: dh_noConv( val, u'%d千年紀' ),
        'lb' :      lambda val: dh_noConv( val, u'%d. Joerdausend' ),
        'lt' :      lambda val: dh_noConv( val, u'%d tūkstantmetis' ),
        #'pt' : u'Segundo milénio d.C.'
        'ro' :      lambda val: dh_roman( val, u'Mileniul %s' ),
        'ru' :      lambda val: dh_noConv( val, u'%d тысячелетие' ),
        'sk' :      lambda val: dh_noConv( val, u'%d. tisícročie' ),
        'sl' :      lambda val: dh_noConv( val, u'%d. tisočletje' ),
        #'sv' : u'1000-talet (millennium)'
        #'ur' : u'1000مبم'
    },
    
    'milleniumsBC': {
        'bg' :      lambda val: dh_noConv( val, u'%d хилядолетие пр.н.е.' ),
        'da' :      lambda val: dh_noConv( val, u'%d. årtusinde f.Kr.' ),
        'de' :      lambda val: dh_noConv( val, u'%d. Jahrtausend v. Chr.' ),
        'en' :      lambda val: dh_noConv( val, u'%dst millennium BC' ),
        'es' :      lambda val: dh_roman( val, u'%s milenio adC' ),
        'fr' :      lambda val: dh_roman( val, u'%ser millénaire av. J.-C.' ),
        'it' :      lambda val: dh_roman( val, u'%s millennio AC' ),
        'ja' :      lambda val: dh_noConv( val, u'紀元前%d千年紀' ),
        'lb' :      lambda val: dh_noConv( val, u'%d. Joerdausend v. Chr.' ),
        #'pt' : u'Primeiro milénio a.C.'
        'ro' :      lambda val: dh_roman( val, u'Mileniul %s î.Hr.' ),
        'ru' :      lambda val: dh_noConv( val, u'%d тысячелетие до н. э.' ),
        'zh' :      lambda val: dh_noConv( val, u'前%d千年' ),
    },
    
    'Cat_Year_MusicAlbums': {
        'en' :      lambda val: dh_noConv( val, u'Category:%d albums' ),
        'fr' :      lambda val: dh_noConv( val, u'Catégorie:Album musical sorti en %d' ),
        'pl' :      lambda val: dh_noConv( val, u'Kategoria:Albumy muzyczne wydane w roku %d' ),
        'sv' :      lambda val: dh_noConv( val, u'Kategori:%d års musikalbum' ),
    },
}


def getDictionaryYear( lang, title ):
    """Returns (dictName,value), where value can be a year, date, etc, and dictName is 'yearsBC','december',etc."""
    for dictName, dict in dateFormats.iteritems():
        try:
            year = dict[ lang ]( title )
            return (dictName,year)
        except:
            pass
    return (None,None)


class FormatDate(object):
    def __init__(self, site):
        self.site = site

    def __call__(self, m, d):
        return dateFormats[monthNames[m-1]][self.site.lang](d)

    
def formatYear(lang, year):
    if year < 0:
        return dateFormats['yearsBC'][lang](-year)
    else:
        return dateFormats['yearsAD'][lang](year)


def testYearMap( m, year, testYear ):
    """This is a test function, to be used interactivelly to test the validity of the above maps.
    To test, run this function with the map name, year to be tested, and the final year expected.
    Usage example:
        run python interpreter
        >>> import date
        >>> date.testYearMap( 'decadesAD', 1992, 1990 )
        >>> date.testYearMap( 'centuriesAD', 20, 20 )
    """
    import wikipedia
    for code, value in dateFormats[m].iteritems():
        wikipedia.output(u"%s: %d -> '%s' -> %d" % (code, year, value(year), value(value(year))))
        if value(value(year)) != testYear:
            raise ValueError("assert failed, years didn't match")

def testAll():
    """This is a test function, to be used interactivelly to test all year maps at once
    Usage example:
        run python interpreter
        >>> import date
        >>> date.testAll()
    """
    testYearMap( 'yearsAD', 1992, 1992 )
    testYearMap( 'yearsBC', 1992, 1992 )
    testYearMap( 'decadesAD', 1990, 1990 )
    testYearMap( 'decadesBC', 1990, 1990 )
    testYearMap( 'decadesAD', 1991, 1990 )
    testYearMap( 'decadesBC', 1991, 1990 )
    testYearMap( 'decadesAD', 1992, 1990 )
    testYearMap( 'decadesBC', 1992, 1990 )
    testYearMap( 'decadesAD', 1998, 1990 )
    testYearMap( 'decadesBC', 1998, 1990 )
    testYearMap( 'decadesAD', 1999, 1990 )
    testYearMap( 'decadesBC', 1999, 1990 )
    testYearMap( 'centuriesAD', 20, 20 )
    testYearMap( 'centuriesBC', 20, 20 )
    testYearMap( 'milleniumsAD', 2, 2 )
    testYearMap( 'milleniumsBC', 2, 2 )

    for d in dateFormats.keys():
        testYearMap( d, 30, 30 )
