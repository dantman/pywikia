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
# © Yuri Astrakhan, 2005 (years/decades/centuries/millenniums  str <=> int  conversions)
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'

# used for date recognition
import types
import re
import wikipedia


#
# Different collections of well known formats
#
enMonthNames    = [ u'January', u'February', u'March', u'April', u'May', u'June', u'July', u'August', u'September', u'October', u'November', u'December' ]
dayMnthFmts     = [ str(s) for s in enMonthNames ]      # convert to ascii
yrMnthFmts      = [ 'Year_' + s for s in dayMnthFmts ]  # e.g. 'Year_January'
adFormats       = [ 'MillenniumAD', 'CenturyAD', 'DecadeAD', 'YearAD' ]
bcFormats       = [ 'MillenniumBC', 'CenturyBC', 'DecadeBC', 'YearBC' ]
decadeFormats   = [ 'DecadeAD', 'DecadeBC' ]
centuryFormats  = [ 'CenturyAD', 'CenturyBC' ]
yearFormats     = [ 'YearAD', 'YearBC' ]
millFormats     = [ 'MillenniumAD', 'MillenniumBC' ]
snglValsFormats = [ 'CurrEvents' ]


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


def multi( value, tuplst ):
    """This method is used when different patterns are used for the same entry.
       Example: 1st century, 2nd century, etc.
       The tuplst is a list of tupples. Each tupple must contain two functions:
       first to encode/decode a single value (e.g. simpleInt),
       second is a predicate function with an integer parameter that returns true or false
       if the 1st function applies or not.
    """
    if type(value) is int:
        # Find a predicate that gives true for this int value, and run a function
        for func, pred in tuplst:
            if pred(value):
                return func(value)
    else:
        # Try all functions, and test result against predicates
        for func, pred in tuplst:
            try:
                res = func(value)
                if pred(res):
                    return res
            except:
                pass

    raise ValueError("could not find a matching function")     


def dh( value, pattern, encf, decf, filter = None ):
    """This function helps in year parsing.
        Usually it will be used as a lambda call in a map:
            lambda v: dh( v, u'pattern string', encodingFunc, decodingFunc )

        encodingFunc converts from an integer parameter to a single number or a tuple parameter that
            can be passed as format argument to the pattern:   pattern % encodingFunc(year)

        decodingFunc converts a list of positive integers found in the original value string
            into a year value. dh() searches creates this list based on the pattern string.
            dh() interprets %d as a decimal and %s as a roman numeral number.

        Usage scenarios:
            formats['DecadeAD']['en'](1980) => u'1980s'
            formats['DecadeAD']['en'](u'1980s') => 1980
            formats['DecadeAD']['en'](u'anything else') => raise ValueError (or some other exception?)
    """
    if type(value) is int:
        # Encode an integer value into a textual form.
        # This will be called from outside as well as recursivelly to verify parsed value
        if filter and not filter(value):
            raise ValueError("value %i is not allowed" % value)
        return pattern % encf(value)
    else:
        cm, dcrs = escapePattern(pattern)
        m = cm.match(value)
        if m:
            # decode each found value using provided decoder
            values = [ dcrs[i](m.group(i+1)) for i in range(len(dcrs))]
            year = decf( values )

            # recursive call to re-encode and see if we get the original (may through filter exception)
            if value == dh(year,pattern,encf,decf,filter):
                return year

        raise ValueError("reverse encoding didn't match")

def dh_dayOfMnth( value, pattern ):
    """decoding helper for a single integer value <=31, no conversion, no rounding (used in days of month)"""
    return dh( value, pattern, encNoConv, decSinglVal, lambda v: 1<=v and v<=31 )

def dh_MnthOfYear( value, pattern ):
    """decoding helper for a single integer value >=1000, no conversion, no rounding (used in month of the year)"""
    return dh( value, pattern, encNoConv, decSinglVal, lambda v: v>=1000 )

def dh_dec( value, pattern ):
    """decoding helper for a single integer value, no conversion, round to decimals (used in decades)"""
    return dh( value, pattern, encDec0, decSinglVal )

def dh_noConv( value, pattern ):
    """decoding helper for a single integer value, no conversion, no rounding (used in centuries, millenniums)"""
    return dh( value, pattern, encNoConv, decSinglVal )

def dh_noConvYear( value, pattern ):
    """decoding helper for a year value, no conversion, no rounding, limits to 3000"""
    return dh( value, pattern, encNoConv, decSinglVal, lambda v: 0<=v and v<=3000 )

def dh_simpleInt( value ):
    """decoding helper for a single integer value representing a number with no extra symbols"""
    return dh_noConv( value, u'%d' )

def dh_simpleYearAD( value ):
    """decoding helper for a single integer value representing a year with no extra symbols"""
    return dh_noConvYear( value, u'%d' )

def dh_roman( value, pattern ):
    """decoding helper for a single roman number (used in centuries, millenniums)"""
    return dh( value, pattern, lambda i: romanNums[i], decSinglVal )

def decSinglVal( v ):
    return v[0]

def encNoConv( i ):
    return i

def encDec0( i ):
    return (i/10)*10            # round to the nearest decade, decade starts with a '0'-ending year

def encDec1( i ):
    return encDec0(i)+1         # round to the nearest decade, decade starts with a '1'-ending year

def slh( value, lst ):
    """This function helps in simple list value matching.
    !!!!! The index starts at 1, so 1st element has index 1, not 0 !!!!!
        Usually it will be used as a lambda call in a map:
            lambda v: slh( v, [u'January',u'February',...] )

        Usage scenarios:
            formats['MonthName']['en'](1) => u'January'
            formats['MonthName']['en'](u'January') => 1
            formats['MonthName']['en'](u'anything else') => raise ValueError
    """
    if type(value) is int:
        return lst[value-1]
    else:
        return lst.index(value)+1

def dh_singVal( value, match ):
    """This function helps with matching a single value.
            formats['CurrEvents']['en'](0) => u'Current Events'
            formats['CurrEvents']['en'](u'Current Events') => 0"""
    if type(value) is int:
        if value == 0:
            return match
        else:
            raise ValueError("unknown value %d" % value)
    else:
        if value == match:
            return 0
        else:
            raise ValueError()


def monthName(lang,ind):
    return formats['MonthName'][lang](ind)

# Helper for KN: digits representation
_knDigits=u'೦೧೨೩೪೫೬೭೮೯'
_knDigitsToLocal=dict([(ord(unicode(i)), _knDigits[i]) for i in range(10)])
_knLocalToDigits=dict([(ord(_knDigits[i]), unicode(i)) for i in range(10)])

def dh_knYearConverter( value ):
    if type(value) is int:
        # Encode an integer value into a textual form.
        return unicode(value).translate(_knDigitsToLocal)
    else:
        # First make sure there are no real digits in the string
        tmp = value.translate(_knDigitsToLocal)         # Test
        if tmp == value:
            tmp = value.translate(_knLocalToDigits)     # Convert
            return dh_noConv( tmp, u'%d' )
        else:
            raise ValueError("string contains regular digits")

#
# All years/decades/centuries/millenniums are designed in such a way
# as to allow for easy date to string and string to date conversion.
# For example, using any map with either an integer or a string will produce its oposite value:
#            formats['DecadeBC']['en'](1980) => u'1980s BC'
#            formats['DecadeBC']['en'](u'1980s BC') => 1980
# This is useful when trying to decide if a certain article is a localized date or not, or generating dates.
# See dh() for additional information.
#

formats = {
    'January': {},
    'February': {},
    'March': {},
    'April': {},
    'May': {},
    'June': {},
    'July': {},
    'August': {},
    'September': {},
    'October': {},
    'November': {},
    'December': {},
    'Year_January': {},
    'Year_February': {},
    'Year_March': {},
    'Year_April': {},
    'Year_May': {},
    'Year_June': {},
    'Year_July': {},
    'Year_August': {},
    'Year_September': {},
    'Year_October': {},
    'Year_November': {},
    'Year_December': {},

    'MonthName': {
            'af' :      lambda v: slh( v, [u"Januarie", u"Februarie", u"Maart", u"April", u"Mei", u"Junie", u"Julie", u"Augustus", u"September", u"Oktober", u"November", u"Desember"] ),
            'als':      lambda v: slh( v, [u"Januar", u"Februar", u"März", u"April", u"Mai", u"Juni", u"Juli", u"August", u"September", u"Oktober", u"November", u"Dezember"] ),
            'an' :      lambda v: slh( v, [u"chinero", u"frebero", u"marzo", u"abril", u"mayo", u"chunio", u"chulio", u"agosto", u"setiembre", u"otubre", u"nobiembre", u"abiento"] ),
            'ang':      lambda v: slh( v, [u"Æfterra Gēola", u"Solmōnaþ", u"Hrēþmōnaþ", u"Ēastermōnaþ", u"Þrimilcemōnaþ", u"Sēremōnaþ", u"Mǣdmōnaþ", u"Wēodmōnaþ", u"Hāligmōnaþ", u"Winterfylleþ", u"Blōtmōnaþ", u"Gēolmōnaþ"] ),
            'ar' :      lambda v: slh( v, [u"يناير", u"فبراير", u"مارس", u"إبريل", u"مايو", u"يونيو", u"يوليو", u"أغسطس", u"سبتمبر", u"أكتوبر", u"نوفمبر", u"ديسمبر"] ),
            'ast':      lambda v: slh( v, [u"xineru", u"febreru", u"marzu", u"abril", u"mayu", u"xunu", u"xunetu", u"agostu", u"setiembre", u"ochobre", u"payares", u"avientu"] ),
            'be' :      lambda v: slh( v, [u"студзень", u"люты", u"сакавік", u"красавік", u"травень", u"чэрвень", u"ліпень", u"жнівень", u"верасень", u"кастрычнік", u"лістапад", u"сьнежань"] ),
            'bg' :      lambda v: slh( v, [u"януари", u"февруари", u"март", u"април", u"май", u"юни", u"юли", u"август", u"септември", u"октомври", u"ноември", u"декември"] ),
            'br' :      lambda v: slh( v, [u"Genver", u"C'hwevrer", u"Meurzh", u"Ebrel", u"Mae", u"Mezheven", u"Gouere", u"Eost", u"Gwengolo", u"Here", u"Du", u"Kerzu"] ),
            'bs' :      lambda v: slh( v, [u"januar", u"februar", u"mart", u"april", u"maj", u"juni", u"juli", u"avgust", u"septembar", u"oktobar", u"novembar", u"decembar"] ),
            'ca' :      lambda v: slh( v, [u"gener", u"febrer", u"març", u"abril", u"maig", u"juny", u"juliol", u"agost", u"setembre", u"octubre", u"novembre", u"desembre"] ),
            'co' :      lambda v: slh( v, [u"ghjennaghju", u"frivaghju", u"marzu", u"aprile", u"maghju", u"ghjugnu", u"lugliu", u"aostu", u"settembre", u"uttrovi", u"nuvembri", u"decembre"] ),
            'cs' :      lambda v: slh( v, [u"leden", u"únor", u"březen", u"duben", u"květen", u"červen", u"červenec", u"srpen", u"září", u"říjen", u"listopad", u"prosinec"] ),
            'csb':      lambda v: slh( v, [u"stëcznik", u"gromicznik", u"strumiannik", u"łżëkwiôt", u"môj", u"czerwińc", u"lëpinc", u"zélnik", u"séwnik", u"rujan", u"lëstopadnik", u"gòdnik"] ),
            'cv' :      lambda v: slh( v, [u"кăрлач", u"нарăс", u"Пуш", u"Ака", u"çу", u"çĕртме", u"утă", u"çурла", u"авăн", u"юпа", u"чӳк", u"раштав"] ),
            'cy' :      lambda v: slh( v, [u"Ionawr", u"Chwefror", u"Mawrth", u"Ebrill", u"Mai", u"Mehefin", u"Gorffennaf", u"Awst", u"Medi", u"Hydref", u"Tachwedd", u"Rhagfyr"] ),
            'da' :      lambda v: slh( v, [u"januar", u"februar", u"marts", u"april", u"maj", u"juni", u"juli", u"august", u"september", u"oktober", u"november", u"december"] ),
            'de' :      lambda v: slh( v, [u"Januar", u"Februar", u"März", u"April", u"Mai", u"Juni", u"Juli", u"August", u"September", u"Oktober", u"November", u"Dezember"] ),
            'el' :      lambda v: slh( v, [u"Ιανουάριος", u"Φεβρουάριος", u"Μάρτιος", u"Απρίλιος", u"Μάιος", u"Ιούνιος", u"Ιούλιος", u"Αύγουστος", u"Σεπτέμβριος", u"Οκτώβριος", u"Νοέμβριος", u"Δεκέμβριος"] ),
            'en' :      lambda v: slh( v, enMonthNames ),
            'eo' :      lambda v: slh( v, [u"Januaro", u"Februaro", u"Marto", u"Aprilo", u"Majo", u"Junio", u"Julio", u"Aŭgusto", u"Septembro", u"Oktobro", u"Novembro", u"Decembro"] ),
            'es' :      lambda v: slh( v, [u"enero", u"febrero", u"marzo", u"abril", u"mayo", u"junio", u"julio", u"agosto", u"septiembre", u"octubre", u"noviembre", u"diciembre"] ),
            'et' :      lambda v: slh( v, [u"jaanuar", u"veebruar", u"märts", u"aprill", u"mai", u"juuni", u"juuli", u"august", u"september", u"oktoober", u"november", u"detsember"] ),
            'eu' :      lambda v: slh( v, [u"Urtarril", u"Otsail", u"Martxo", u"Apiril", u"Maiatz", u"Ekain", u"Uztail", u"Abuztu", u"Irail", u"Urri", u"Azaro", u"Abendu"] ),
            'fa' :      lambda v: slh( v, [u"ژانویه", u"فوریه", u"مارس", u"آوریل", u"مه", u"ژوئن", u"ژوئیه", u"اوت", u"سپتامبر", u"اکتبر", u"نوامبر", u"دسامبر"] ),
            'fi' :      lambda v: slh( v, [u"tammikuu", u"helmikuu", u"maaliskuu", u"huhtikuu", u"toukokuu", u"kesäkuu", u"heinäkuu", u"elokuu", u"syyskuu", u"lokakuu", u"marraskuu", u"joulukuu"] ),
            'fo' :      lambda v: slh( v, [u"januar", u"februar", u"mars", u"apríl", u"mai", u"juni", u"juli", u"august", u"september", u"oktober", u"november", u"desember"] ),
            'fr' :      lambda v: slh( v, [u"janvier", u"février", u"mars (mois)", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre"] ),
            'fur':      lambda v: slh( v, [u"Zenâr", u"Fevrâr", u"Març", u"Avrîl", u"Mai", u"Zugn", u"Lui", u"Avost", u"Setembar", u"Otubar", u"Novembar", u"Dicembar"] ),
            'fy' :      lambda v: slh( v, [u"jannewaris", u"febrewaris", u"maart", u"april", u"maaie", u"juny", u"july", u"augustus", u"septimber", u"oktober", u"novimber", u"desimber"] ),
            'ga' :      lambda v: slh( v, [u"Eanáir", u"Feabhra", u"Márta", u"Aibreán", u"Bealtaine", u"Meitheamh", u"Iúil", u"Lúnasa", u"Meán Fómhair", u"Deireadh Fómhair", u"Samhain", u"Nollaig"] ),
            'gl' :      lambda v: slh( v, [u"xaneiro", u"febreiro", u"marzo", u"abril", u"maio", u"xuño", u"xullo", u"agosto", u"setembro", u"outubro", u"novembro", u"decembro"] ),
            'he' :      lambda v: slh( v, [u"ינואר", u"פברואר", u"מרץ", u"אפריל", u"מאי", u"יוני", u"יולי", u"אוגוסט", u"ספטמבר", u"אוקטובר", u"נובמבר", u"דצמבר"] ),
            'hi' :      lambda v: slh( v, [u"जनवरी", u"फ़रवरी", u"मार्च", u"अप्रैल", u"मई", u"जून", u"जुलाई", u"अगस्त", u"सितम्बर", u"अक्टूबर", u"नवम्बर", u"दिसम्बर"] ),
            'hr' :      lambda v: slh( v, [u"siječanj", u"veljača", u"ožujak", u"travanj", u"svibanj", u"lipanj", u"srpanj", u"kolovoz", u"rujan", u"listopad", u"studeni", u"prosinac"] ),
            'hu' :      lambda v: slh( v, [u"január", u"február", u"március", u"április", u"május", u"június", u"július", u"augusztus", u"szeptember", u"október", u"november", u"december"] ),
            'ia' :      lambda v: slh( v, [u"januario", u"februario", u"martio", u"april", u"maio", u"junio", u"julio", u"augusto", u"septembre", u"octobre", u"novembre", u"decembre"] ),
            'id' :      lambda v: slh( v, [u"Januari", u"Februari", u"Maret", u"April", u"Mei", u"Juni", u"Juli", u"Agustus", u"September", u"Oktober", u"November", u"Desember"] ),
            'ie' :      lambda v: slh( v, [u"januar", u"februar", u"marte", u"april", u"may", u"junio", u"juli", u"august", u"septembre", u"octobre", u"novembre", u"decembre"] ),
            'io' :      lambda v: slh( v, [u"januaro", u"februaro", u"Marto", u"aprilo", u"mayo", u"junio", u"julio", u"agosto", u"septembro", u"oktobro", u"novembro", u"decembro"] ),
            'is' :      lambda v: slh( v, [u"janúar", u"febrúar", u"mars (mánuður)", u"apríl", u"maí", u"júní", u"júlí", u"ágúst", u"september", u"október", u"nóvember", u"desember"] ),
            'it' :      lambda v: slh( v, [u"gennaio", u"febbraio", u"marzo", u"aprile", u"maggio", u"giugno", u"luglio", u"agosto", u"settembre", u"ottobre", u"novembre", u"dicembre"] ),
            'ja' :      lambda v: slh( v, makeMonthList( u"%d月" )),
            'jv' :      lambda v: slh( v, [u"Januari", u"Februari", u"Maret", u"April", u"Mei", u"Juni", u"Juli", u"Agustus", u"September", u"Oktober", u"November", u"Desember"] ),
            'ka' :      lambda v: slh( v, [u"იანვარი", u"თებერვალი", u"მარტი", u"აპრილი", u"მაისი", u"ივნისი", u"ივლისი", u"აგვისტო", u"სექტემბერი", u"ოქტომბერი", u"ნოემბერი", u"დეკემბერი"] ),
            'kn' :      lambda v: slh( v, [u"ಜನವರಿ", u"ಫೆಬ್ರವರಿ", u"ಮಾರ್ಚಿ", u"ಎಪ್ರಿಲ್", u"ಮೇ", u"ಜೂನ", u"ಜುಲೈ", u"ಆಗಸ್ಟ್", u"ಸೆಪ್ಟೆಂಬರ್", u"ಅಕ್ಟೋಬರ್", u"ನವೆಂಬರ್", u"ಡಿಸೆಂಬರ್"] ),
            'ko' :      lambda v: slh( v, makeMonthList( u"%d월" )),
            'ku' :      lambda v: slh( v, [u"rêbendan", u"reşemî", u"adar", u"avrêl", u"gulan", u"pûşper", u"tîrmeh", u"gelawêj (meh)", u"rezber", u"kewçêr", u"sermawez", u"berfanbar"] ),
            'kw' :      lambda v: slh( v, [u"Mys Genver", u"Mys Whevrer", u"Mys Merth", u"Mys Ebrel", u"Mys Me", u"Mys Metheven", u"Mys Gortheren", u"Mys Est", u"Mys Gwyngala", u"Mys Hedra", u"Mys Du", u"Mys Kevardhu"] ),
            'la' :      lambda v: slh( v, [u"Ianuarius", u"Februarius", u"Martius", u"Aprilis", u"Maius", u"Iunius", u"Iulius", u"Augustus (mensis)", u"September", u"October", u"November", u"December"] ),
            'lb' :      lambda v: slh( v, [u"Januar", u"Februar", u"Mäerz", u"Abrëll", u"Mee", u"Juni", u"Juli", u"August", u"September", u"Oktober", u"November", u"Dezember"] ),
            'li' :      lambda v: slh( v, [u"jannewarie", u"fibberwarie", u"miert", u"april", u"mei", u"juni", u"juli", u"augustus (maond)", u"september", u"oktober", u"november", u"december"] ),
            'lt' :      lambda v: slh( v, [u"Sausis", u"Vasaris", u"Kovas", u"Balandis", u"Gegužė", u"Birželis", u"Liepa", u"Rugpjūtis", u"Rugsėjis", u"Spalis", u"Lapkritis", u"Gruodis"] ),
            'mi' :      lambda v: slh( v, [u"Kohi-tātea", u"Hui-tanguru", u"Poutū-te-rangi", u"Paenga-whāwhā", u"Haratua", u"Pipiri", u"Hōngongoi", u"Here-turi-kōkā", u"Mahuru", u"Whiringa-ā-nuku", u"Whiringa-ā-rangi", u"Hakihea"] ),
            'ml' :      lambda v: slh( v, [u"ജനുവരി", u"ഫെബ്രുവരി", u"മാര്ച്", u"ഏപ്രില്", u"മേയ്", u"ജൂണ്‍", u"ജൂലൈ", u"ആഗസ്റ്റ്‌", u"സപ്തന്പര്", u"ഒക്ടോബര്", u"നവന്പര്", u"ഡിസന്പര്"] ),
            'mr' :      lambda v: slh( v, [u"जानेवारी", u"फेब्रुवारी", u"मार्च", u"एप्रिल", u"मे", u"जून", u"जुलै", u"ऑगस्ट", u"सप्टेंबर", u"ऑक्टोबर", u"नोव्हेंबर", u"डिसेंबर"] ),
            'ms' :      lambda v: slh( v, [u"Januari", u"Februari", u"Mac", u"April", u"Mei", u"Jun", u"Julai", u"Ogos", u"September", u"Oktober", u"November", u"Disember"] ),
            'nap':      lambda v: slh( v, [u"Jennaro", u"Frevaro", u"Màrzo", u"Abbrile", u"Maggio", u"Giùgno", u"Luglio", u"Aùsto", u"Settembre", u"Ottovre", u"Nuvembre", u"Dicembre"] ),
            'nds':      lambda v: slh( v, [u"Januar", u"Februar", u"März", u"April", u"Mai", u"Juni", u"Juli", u"August", u"September", u"Oktober", u"November", u"Dezember"] ),
            'nl' :      lambda v: slh( v, [u"januari", u"februari", u"maart", u"april", u"mei", u"juni", u"juli", u"augustus (maand)", u"september", u"oktober", u"november", u"december"] ),
            'nn' :      lambda v: slh( v, [u"januar", u"februar", u"månaden mars", u"april", u"mai", u"juni", u"juli", u"august", u"september", u"oktober", u"november", u"desember"] ),
            'no' :      lambda v: slh( v, [u"januar", u"februar", u"mars", u"april", u"mai", u"juni", u"juli", u"august", u"september", u"oktober", u"november", u"desember"] ),
            'oc' :      lambda v: slh( v, [u"genièr", u"febrièr", u"març", u"abril", u"mai", u"junh", u"julhet", u"agost", u"setembre", u"octobre", u"novembre", u"decembre"] ),
            'os' :      lambda v: slh( v, [u"январь", u"февраль", u"мартъи", u"апрель", u"май", u"июнь", u"июль", u"август", u"сентябрь", u"октябрь", u"ноябрь", u"декабрь"] ),
            'pl' :      lambda v: slh( v, [u"styczeń", u"luty", u"marzec", u"kwiecień", u"maj", u"czerwiec", u"lipiec", u"sierpień", u"wrzesień", u"październik", u"listopad", u"grudzień"] ),
            'pt' :      lambda v: slh( v, [u"Janeiro", u"Fevereiro", u"Março", u"Abril", u"Maio", u"Junho", u"Julho", u"Agosto", u"Setembro", u"Outubro", u"Novembro", u"Dezembro"] ),
            'ro' :      lambda v: slh( v, [u"ianuarie", u"februarie", u"martie", u"aprilie", u"mai", u"iunie", u"iulie", u"august", u"septembrie", u"octombrie", u"noiembrie", u"decembrie"] ),
            'ru' :      lambda v: slh( v, [u"январь", u"февраль", u"март", u"апрель", u"май", u"июнь", u"июль", u"август", u"сентябрь", u"октябрь", u"ноябрь", u"декабрь"] ),
            'sc' :      lambda v: slh( v, [u"Ghennarzu", u"Frearzu", u"Martzu", u"Abrile", u"Maju", u"Làmpadas", u"Triulas", u"Aùstu", u"Cabudanni", u"Santugaìne", u"Santadria", u"Nadale"] ),
            'scn':      lambda v: slh( v, [u"jinnaru", u"frivaru", u"marzu", u"aprili", u"maiu", u"giugnu", u"giugnettu", u"austu", u"sittèmmiru", u"uttùviru", u"nuvèmmiru", u"dicèmmiru"] ),
            'sco':      lambda v: slh( v, [u"Januar", u"Februar", u"Mairch", u"Aprile", u"Mey", u"Juin", u"Julie", u"August", u"September", u"October", u"November", u"December"] ),
            'se' :      lambda v: slh( v, [u"ođđajagimánnu", u"guovvamánnu", u"njukčamánnu", u"cuoŋománnu", u"miessemánnu", u"geassemánnu", u"suoidnemánnu", u"borgemánnu", u"čakčamánnu", u"golggotmánnu", u"skábmamánnu", u"juovlamánnu"] ),
            'simple':   lambda v: slh( v, [u"January", u"February", u"March", u"April", u"May", u"June", u"July", u"August", u"September", u"October", u"November", u"December"] ),
            'sk' :      lambda v: slh( v, [u"január", u"február", u"marec", u"apríl", u"máj", u"jún", u"júl", u"august", u"september", u"október", u"november", u"december"] ),
            'sl' :      lambda v: slh( v, [u"januar", u"februar", u"marec", u"april", u"maj", u"junij", u"julij", u"avgust", u"september", u"oktober", u"november", u"december"] ),
            'sq' :      lambda v: slh( v, [u"Janari", u"Shkurti", u"Marsi (muaj)", u"Prilli", u"Maji", u"Qershori", u"Korriku", u"Gushti", u"Shtatori", u"Tetori", u"Nëntori", u"Dhjetori"] ),
            'sr' :      lambda v: slh( v, [u"јануар", u"фебруар", u"март", u"април", u"мај", u"јун", u"јул", u"август", u"септембар", u"октобар", u"новембар", u"децембар"] ),
            'su' :      lambda v: slh( v, [u"Januari", u"Pébruari", u"Maret", u"April", u"Méi", u"Juni", u"Juli", u"Agustus", u"Séptémber", u"Oktober", u"Nopémber", u"Désémber"] ),
            'sv' :      lambda v: slh( v, [u"januari", u"februari", u"mars", u"april", u"maj", u"juni", u"juli", u"augusti", u"september", u"oktober", u"november", u"december"] ),
            'te' :      lambda v: slh( v, [u"జనవరి", u"ఫిబ్రవరి", u"మార్చి", u"ఏప్రిల్", u"మే", u"జూన్", u"జూలై", u"ఆగష్టు", u"సెప్టెంబర్", u"అక్టోబర్", u"నవంబర్", u"డిసెంబర్"] ),
            'th' :      lambda v: slh( v, [u"มกราคม", u"กุมภาพันธ์", u"มีนาคม", u"เมษายน", u"พฤษภาคม", u"มิถุนายน", u"กรกฎาคม", u"สิงหาคม", u"กันยายน", u"ตุลาคม", u"พฤศจิกายน", u"ธันวาคม"] ),
            'tl' :      lambda v: slh( v, [u"Enero", u"Pebrero", u"Marso", u"Abril", u"Mayo", u"Hunyo", u"Hulyo", u"Agosto", u"Setyembre", u"Oktubre", u"Nobyembre", u"Disyembre"] ),
            'tpi':      lambda v: slh( v, [u"Janueri", u"Februeri", u"Mas", u"Epril", u"Me", u"Jun", u"Julai", u"Ogas", u"Septemba", u"Oktoba", u"Novemba", u"Disemba"] ),
            'tr' :      lambda v: slh( v, [u"Ocak", u"Şubat", u"Mart", u"Nisan", u"Mayıs", u"Haziran", u"Temmuz", u"Ağustos", u"Eylül", u"Ekim", u"Kasım", u"Aralık"] ),
            'tt' :      lambda v: slh( v, [u"Ğínwar", u"Febräl", u"Mart", u"Äpril", u"May", u"Yün", u"Yül", u"August", u"Sentäber", u"Öktäber", u"Nöyäber", u"Dekäber"] ),
            'uk' :      lambda v: slh( v, [u"січень", u"лютий", u"березень", u"квітень", u"травень", u"червень", u"липень", u"серпень", u"вересень", u"жовтень", u"листопад", u"грудень"] ),
            'ur' :      lambda v: slh( v, [u"جنوری", u"فروری", u"مارچ", u"اپريل", u"مئ", u"جون", u"جولائ", u"اگست", u"ستمبر", u"اکتوبر", u"نومبر", u"دسمبر"] ),
            'vi' :      lambda v: slh( v, [u"tháng một", u"tháng hai", u"tháng ba", u"tháng tư", u"tháng năm", u"tháng sáu", u"tháng bảy", u"tháng tám", u"tháng chín", u"tháng mười", u"tháng mười một", u"tháng 12"] ),
            'vo' :      lambda v: slh( v, [u"Yanul", u"Febul", u"Mäzul", u"Prilul", u"Mayul", u"Yunul", u"Yulul", u"Gustul", u"Setul", u"Tobul", u"Novul", u"Dekul"] ),
            'wa' :      lambda v: slh( v, [u"djanvî", u"fevrî", u"Måss (moes)", u"avri", u"may", u"djun", u"djulete", u"awousse", u"setimbe", u"octôbe", u"nôvimbe", u"decimbe"] ),
            'zh' :      lambda v: slh( v, makeMonthList( u"%d月" )),
            'zh-min-nan': lambda v: slh( v, [u"It-goe̍h", u"Jī-goe̍h", u"Saⁿ-goe̍h", u"Sì-goe̍h", u"Gō·-goe̍h", u"La̍k-goe̍h", u"Chhit-goe̍h", u"Peh-goe̍h", u"Káu-goe̍h", u"Cha̍p-goe̍h", u"Cha̍p-it-goe̍h", u"Cha̍p-jī-goe̍h"] ),
            #'af' :      lambda v: slh( v, [u'Januarie', u'Februarie', u'Maart', u'April', u'Mei', u'Junie', u'Julie', u'Augustus', u'September', u'Oktober', u'November', u'Desember'] ),
            #'als':      lambda v: slh( v, [u'Januar', u'Februar', u'März', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            #'an' :      lambda v: slh( v, [u'Chinero', u'Frebero', u'Marzo', u'Abril', u'Mayo', u'Chunio', u'Chulio', u'Agosto', u'Setiembre', u'Otubre', u'Nobiembre', u'Abiento'] ),
            #'ang':      lambda v: slh( v, [u'Se æfterra Gēola', u'Solmónaþ', u'Hrēþmōnaþ', u'Ēastermōnaþ', u'Þrimilcemónaþ', u'Séremónaþ', u'Mǽdmónaþ', u'Wéodmónaþ', u'Háligmónaþ', u'Winterfylleþ', u'Blótmónaþ', u'Géolmónaþ'] ),
            #'ar' :      lambda v: slh( v, [u'يناير', u'فبراير', u'مارس', u'إبريل', u'مايو', u'يونيو', u'يوليو', u'أغسطس', u'سبتمبر', u'أكتوبر', u'نوفمبر', u'ديسمبر'] ),
            #'ast':      lambda v: slh( v, [u'Xineru', u'Febreru', u'Marzu', u'Abril', u'Mayu', u'Xunu', u'Xunetu', u'Agostu', u'Setiembre', u'Ochobre', u'Payares', u'Avientu'] ),
            #'be' :      lambda v: slh( v, [u'Студзень', u'Люты', u'Сакавік', u'Красавік', u'Травень', u'Чэрвень', u'Ліпень', u'Жнівень', u'Верасень', u'Кастрычнік', u'Лістапад', u'Сьнежань'] ),
            #'bg' :      lambda v: slh( v, [u'Януари', u'Февруари', u'Март', u'Април', u'Май', u'Юни', u'Юли', u'Август', u'Септември', u'Октомври', u'Ноември', u'Декември'] ),
            #'bs' :      lambda v: slh( v, [u'Januar', u'Februar', u'Mart', u'April', u'Maj', u'Juni', u'Juli', u'Avgust', u'Septembar', u'Oktobar', u'Novembar', u'Decembar'] ),
            #'ca' :      lambda v: slh( v, [u'Gener', u'Febrer', u'Març', u'Abril', u'Maig', u'Juny', u'Juliol', u'Agost', u'Setembre', u'Octubre', u'Novembre', u'Desembre'] ),
            #'cs' :      lambda v: slh( v, [u'Leden', u'Únor', u'Březen', u'Duben', u'Květen', u'Červen', u'Červenec', u'Srpen', u'Září', u'Říjen', u'Listopad', u'Prosinec'] ),
            #'csb':      lambda v: slh( v, [u'Stëcznik', u'Gromicznik', u'Strumiannik', u'Łżëkwiôt', u'Môj', u'Czerwińc', u'Lëpinc', u'Zélnik', u'Séwnik', u'Rujan', u'Lëstopadnik', u'Gòdnik'] ),
            #'cv' :      lambda v: slh( v, [u'Кăрлач', u'Нарăс', u'Пуш', u'Ака', u'Çу', u'Çěртме', u'Утă', u'Çурла', u'Авăн', u'Юпа', u'Чӳк', u'Раштав'] ),
            #'cy' :      lambda v: slh( v, [u'Ionawr', u'Chwefror', u'Mawrth', u'Ebrill', u'Mai', u'Mehefin', u'Gorffennaf', u'Awst', u'Medi', u'Hydref', u'Tachwedd', u'Rhagfyr'] ),
            #'da' :      lambda v: slh( v, [u'Januar', u'Februar', u'Marts', u'April', u'Maj', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'December'] ),
            #'de' :      lambda v: slh( v, [u'Januar', u'Februar', u'März', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            #'el' :      lambda v: slh( v, [u'Ιανουάριος', u'Φεβρουάριος', u'Μάρτιος', u'Απρίλιος', u'Μάιος', u'Ιούνιος', u'Ιούλιος', u'Αύγουστος', u'Σεπτέμβριος', u'Οκτώβριος', u'Νοέμβριος', u'Δεκέμβριος'] ),
            #'en' :      lambda v: slh( v, enMonthNames ),
            #'eo' :      lambda v: slh( v, [u'Januaro', u'Februaro', u'Marto', u'Aprilo', u'Majo', u'Junio', u'Julio', u'Aŭgusto', u'Septembro', u'Oktobro', u'Novembro', u'Decembro'] ),
            #'es' :      lambda v: slh( v, [u'Enero', u'Febrero', u'Marzo', u'Abril', u'Mayo', u'Junio', u'Julio', u'Agosto', u'Septiembre', u'Octubre', u'Noviembre', u'Diciembre'] ),
            #'et' :      lambda v: slh( v, [u'Jaanuar', u'Veebruar', u'Märts', u'Aprill', u'Mai', u'Juuni', u'Juuli', u'August', u'September', u'Oktoober', u'November', u'Detsember'] ),
            #'eu' :      lambda v: slh( v, [u'Urtarril', u'Otsail', u'Martxo', u'Apiril', u'Maiatz', u'Ekain', u'Uztail', u'Abuztu', u'Irail', u'Urri', u'Azaro', u'Abendu'] ),
            #'fa' :      lambda v: slh( v, [u'ژانویه', u'فوریه', u'مارس', u'آوریل', u'مه', u'ژوئن', u'ژوئیه', u'اوت', u'سپتامبر', u'اکتبر', u'نوامبر', u'دسامبر'] ),
            #'fi' :      lambda v: slh( v, [u'Tammikuu', u'Helmikuu', u'Maaliskuu', u'Huhtikuu', u'Toukokuu', u'Kesäkuu', u'Heinäkuu', u'Elokuu', u'Syyskuu', u'Lokakuu', u'Marraskuu', u'Joulukuu'] ),
            #'fo' :      lambda v: slh( v, [u'Januar', u'Februar', u'Mars', u'Apríl', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Desember'] ),
            #'fr' :      lambda v: slh( v, [u'Janvier', u'Février', u'Mars (mois)', u'Avril', u'Mai', u'Juin', u'Juillet', u'Août', u'Septembre', u'Octobre', u'Novembre', u'Décembre'] ),
            #'fur':      lambda v: slh( v, [u'Zenâr', u'Fevrâr', u'Març', u'Avrîl', u'Mai', u'Zugn', u'Lui', u'Avost', u'Setembar', u'Otubar', u'Novembar', u'Dicembar'] ),
            #'fy' :      lambda v: slh( v, [u'Jannewaris', u'Febrewaris', u'Maart', u'April', u'Maaie', u'Juny', u'July', u'Augustus', u'Septimber', u'Oktober', u'Novimber', u'Desimber'] ),
            #'ga' :      lambda v: slh( v, [u'Eanáir', u'Feabhra', u'Márta', u'Aibreán', u'Bealtaine', u'Meitheamh', u'Iúil', u'Lúnasa', u'Meán Fómhair', u'Deireadh Fómhair', u'Samhain', u'Nollaig'] ),
            #'gl' :      lambda v: slh( v, [u'Xaneiro', u'Febreiro', u'Marzo', u'Abril', u'Maio', u'Xuño', u'Xullo', u'Agosto', u'Setembro', u'Outubro', u'Novembro', u'Decembro'] ),
            #'he' :      lambda v: slh( v, [u'ינואר', u'פברואר', u'מרץ', u'אפריל', u'מאי', u'יוני', u'יולי', u'אוגוסט', u'ספטמבר', u'אוקטובר', u'נובמבר', u'דצמבר'] ),
            #'hi' :      lambda v: slh( v, [u'जनवरी', u'फ़रवरी', u'मार्च', u'अप्रैल', u'मई', u'जून', u'जुलाई', u'अगस्त', u'सितम्बर', u'अक्टूबर', u'नवम्बर', u'दिसम्बर'] ),
            #'hr' :      lambda v: slh( v, [u'Siječanj', u'Veljača', u'Ožujak', u'Travanj', u'Svibanj', u'Lipanj', u'Srpanj', u'Kolovoz', u'Rujan', u'Listopad', u'Studeni', u'Prosinac'] ),
            #'hu' :      lambda v: slh( v, [u'Január', u'Február', u'Március', u'Április', u'Május', u'Június', u'Július', u'Augusztus', u'Szeptember', u'Október', u'November', u'December'] ),
            #'ia' :      lambda v: slh( v, [u'Januario', u'Februario', u'Martio', u'April', u'Maio', u'Junio', u'Julio', u'Augusto', u'Septembre', u'Octobre', u'Novembre', u'Decembre'] ),
            #'id' :      lambda v: slh( v, [u'Januari', u'Februari', u'Maret', u'April', u'Mei', u'Juni', u'Juli', u'Agustus', u'September', u'Oktober', u'November', u'Desember'] ),
            #'ie' :      lambda v: slh( v, [u'Januar', u'Februar', u'Marte', u'April', u'May', u'Junio', u'Juli', u'August', u'Septembre', u'Octobre', u'Novembre', u'Decembre'] ),
            #'io' :      lambda v: slh( v, [u'Januaro', u'Februaro', u'Marto', u'Aprilo', u'Mayo', u'Junio', u'Julio', u'Agosto', u'Septembro', u'Oktobro', u'Novembro', u'Decembro'] ),
            #'is' :      lambda v: slh( v, [u'Janúar', u'Febrúar', u'Mars (mánuður)', u'Apríl', u'Maí', u'Júní', u'Júlí', u'Ágúst', u'September', u'Október', u'Nóvember', u'Desember'] ),
            #'it' :      lambda v: slh( v, [u'Gennaio', u'Febbraio', u'Marzo', u'Aprile', u'Maggio', u'Giugno', u'Luglio', u'Agosto', u'Settembre', u'Ottobre', u'Novembre', u'Dicembre'] ),
            #'ja' :      lambda v: slh( v, makeMonthList( u'%d月' )),
            #'jv' :      lambda v: slh( v, [u'Januari', u'Februari', u'Maret', u'April', u'Mei', u'Juni', u'Juli', u'Agustus', u'September', u'Oktober', u'November', u'Desember'] ),
            #'ka' :      lambda v: slh( v, [u'იანვარი', u'თებერვალი', u'მარტი', u'აპრილი', u'მაისი', u'ივნისი', u'ივლისი', u'აგვისტო', u'სექტემბერი', u'ოქტომბერი', u'ნოემბერი', u'დეკემბერი'] ),
            #'kn' :      lambda v: slh( v, [u'ಜನವರಿ', u'ಫೆಬ್ರವರಿ', u'ಮಾರ್ಚಿ', u'ಎಪ್ರಿಲ್', u'ಮೇ', u'ಜೂನ', u'ಜುಲೈ', u'ಆಗಸ್ಟ್ ', u'ಸೆಪ್ಟೆಂಬರ್', u'ಅಕ್ಟೋಬರ್', u'ನವೆಂಬರ್', u'ಡಿಸೆಂಬರ್'] ),
            #'ko' :      lambda v: slh( v, makeMonthList( u'%d월' )),
            #'ku' :      lambda v: slh( v, [u'Rêbendan', u'Reşemî', u'Adar', u'Avrêl', u'Gulan', u'Pûşper', u'Tîrmeh', u'Gelawêj (meh)', u'Rezber', u'Kewçêr', u'Sermawez', u'Berfanbar'] ),
            #'kw' :      lambda v: slh( v, [u'Mys Genver', u'Mys Whevrer', u'Mys Merth', u'Mys Ebrel', u'Mys Me', u'Mys Metheven', u'Mys Gortheren', u'Mys Est', u'Mys Gwyngala', u'Mys Hedra', u'Mys Du', u'Mys Kevardhu'] ),
            #'la' :      lambda v: slh( v, [u'Ianuarius', u'Februarius', u'Martius', u'Aprilis', u'Maius', u'Iunius', u'Iulius', u'Augustus (mensis)', u'September', u'October', u'November', u'December'] ),
            #'lb' :      lambda v: slh( v, [u'Januar', u'Februar', u'Mäerz', u'Abrëll', u'Mee', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            #'li' :      lambda v: slh( v, [u'Jannewarie', u'Fibberwarie', u'Miert', u'April', u'Mei', u'Juni', u'Juli', u'Augustus (maond)', u'September', u'Oktober', u'November', u'December'] ),
            #'lt' :      lambda v: slh( v, [u'Sausis', u'Vasaris', u'Kovas', u'Balandis', u'Gegužė', u'Birželis', u'Liepa', u'Rugpjūtis', u'Rugsėjis', u'Spalis', u'Lapkritis', u'Gruodis'] ),
            #'mi' :      lambda v: slh( v, [u'Kohi-tātea', u'Hui-tanguru', u'Poutū-te-rangi', u'Paenga-whāwhā', u'Haratua', u'Pipiri', u'Hōngongoi', u'Here-turi-kōkā', u'Mahuru', u'Whiringa-ā-nuku', u'Whiringa-ā-rangi', u'Hakihea'] ),
            #'ml' :      lambda v: slh( v, [u'ജനുവരി', u'ഫെബ്രുവരി', u'മാര്ച്', u'ഏപ്രില്', u'മേയ്', u'ജൂണ്‍', u'ജൂലൈ', u'ആഗസ്റ്റ്‌', u'സപ്തന്പര്', u'ഒക്ടോബര്', u'നവന്പര്', u'ഡിസന്പര്'] ),
            #'mr' :      lambda v: slh( v, [u'जानेवारी', u'फेब्रुवारी', u'मार्च', u'एप्रिल', u'मे', u'जून', u'जुलै', u'ऑगस्ट', u'सप्टेंबर', u'ऑक्टोबर', u'नोव्हेंबर', u'डिसेंबर'] ),
            #'ms' :      lambda v: slh( v, [u'Januari', u'Februari', u'Mac', u'April', u'Mei', u'Jun', u'Julai', u'Ogos', u'September', u'Oktober', u'November', u'Disember'] ),
            #'nds':      lambda v: slh( v, [u'Januar', u'Februar', u'März', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Dezember'] ),
            #'nl' :      lambda v: slh( v, [u'Januari', u'Februari', u'Maart', u'April', u'Mei', u'Juni', u'Juli', u'Augustus (maand)', u'September', u'Oktober', u'November', u'December'] ),
            #'nn' :      lambda v: slh( v, [u'Januar', u'Februar', u'Mars', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Desember'] ),
            #'no' :      lambda v: slh( v, [u'Januar', u'Februar', u'Mars', u'April', u'Mai', u'Juni', u'Juli', u'August', u'September', u'Oktober', u'November', u'Desember'] ),
            #'oc' :      lambda v: slh( v, [u'Genièr', u'Febrièr', u'Març', u'Abril', u'Mai', u'Junh', u'Julhet', u'Agost', u'Setembre', u'Octobre', u'Novembre', u'Decembre'] ),
            #'pl' :      lambda v: slh( v, [u'Styczeń', u'Luty', u'Marzec', u'Kwiecień', u'Maj', u'Czerwiec', u'Lipiec', u'Sierpień', u'Wrzesień', u'Październik', u'Listopad', u'Grudzień'] ),
            #'pt' :      lambda v: slh( v, [u'Janeiro', u'Fevereiro', u'Março', u'Abril', u'Maio', u'Junho', u'Julho', u'Agosto', u'Setembro', u'Outubro', u'Novembro', u'Dezembro'] ),
            #'ro' :      lambda v: slh( v, [u'Ianuarie', u'Februarie', u'Martie', u'Aprilie', u'Mai', u'Iunie', u'Iulie', u'August', u'Septembrie', u'Octombrie', u'Noiembrie', u'Decembrie'] ),
            #'ru' :      lambda v: slh( v, [u'Январь', u'Февраль', u'Март', u'Апрель', u'Май', u'Июнь', u'Июль', u'Август', u'Сентябрь', u'Октябрь', u'Ноябрь', u'Декабрь'] ),
            #'sc' :      lambda v: slh( v, [u'Ghennarzu', u'Frearzu', u'Martzu', u'Abrile', u'Maju', u'Làmpadas', u'Triulas', u'Aùstu', u'Cabudanni', u'Santugaìne', u'Santadria', u'Nadale'] ),
            #'scn':      lambda v: slh( v, [u'Jinnaru', u'Frivaru', u'Marzu', u'Aprili', u'Maiu', u'Giugnu', u'Giugnettu', u'Austu', u'Sittèmmiru', u'Uttùviru', u'Nuvèmmiru', u'Dicèmmiru'] ),
            #'sco':      lambda v: slh( v, [u'Januar', u'Februar', u'Mairch', u'Aprile', u'Mey', u'Juin', u'Julie', u'Augist', u'September', u'October', u'November', u'December'] ),
            #'se' :      lambda v: slh( v, [u'Ođđajagimánnu', u'Guovvamánnu', u'Njukčamánnu', u'Cuoŋománnu', u'Miessemánnu', u'Geassemánnu', u'Suoidnemánnu', u'Borgemánnu', u'Čakčamánnu', u'Golggotmánnu', u'Skábmamánnu', u'Juovlamánnu'] ),
            #'simple':   lambda v: slh( v, enMonthNames ),
            #'sk' :      lambda v: slh( v, [u'Január', u'Február', u'Marec', u'Apríl', u'Máj', u'Jún', u'Júl', u'August', u'September', u'Október', u'November', u'December'] ),
            #'sl' :      lambda v: slh( v, [u'Januar', u'Februar', u'Marec', u'April', u'Maj', u'Junij', u'Julij', u'Avgust', u'September', u'Oktober', u'November', u'December'] ),
            #'sq' :      lambda v: slh( v, [u'Janari', u'Shkurti', u'Marsi (muaj)', u'Prilli', u'Maji', u'Qershori', u'Korriku', u'Gushti', u'Shtatori', u'Tetori', u'Nëntori', u'Dhjetori'] ),
            #'sr' :      lambda v: slh( v, [u'Јануар', u'Фебруар', u'Март', u'Април', u'Мај', u'Јун', u'Јул', u'Август', u'Септембар', u'Октобар', u'Новембар', u'Децембар'] ),
            #'su' :      lambda v: slh( v, [u'Januari', u'Pébruari', u'Maret', u'April', u'Méi', u'Juni', u'Juli', u'Agustus', u'Séptémber', u'Oktober', u'Nopémber', u'Désémber'] ),
            #'sv' :      lambda v: slh( v, [u'Januari', u'Februari', u'Mars', u'April', u'Maj', u'Juni', u'Juli', u'Augusti', u'September', u'Oktober', u'November', u'December'] ),
            #'te' :      lambda v: slh( v, [u'జనవరి', u'ఫిబ్రవరి', u'మార్చి', u'ఏప్రిల్', u'మే', u'జూన్', u'జూలై', u'ఆగష్టు', u'సెప్టెంబర్', u'అక్టోబర్', u'నవంబర్', u'డిసెంబర్'] ),
            #'th' :      lambda v: slh( v, [u'มกราคม', u'กุมภาพันธ์', u'มีนาคม', u'เมษายน', u'พฤษภาคม', u'มิถุนายน', u'กรกฎาคม', u'สิงหาคม', u'กันยายน', u'ตุลาคม', u'พฤศจิกายน', u'ธันวาคม'] ),
            #'tl' :      lambda v: slh( v, [u'Enero', u'Pebrero', u'Marso', u'Abril', u'Mayo', u'Hunyo', u'Hulyo', u'Agosto', u'Setyembre', u'Oktubre', u'Nobyembre', u'Disyembre'] ),
            #'tpi':      lambda v: slh( v, [u'Janueri', u'Februeri', u'Mas', u'Epril', u'Me', u'Jun', u'Julai', u'Ogas', u'Septemba', u'Oktoba', u'Novemba', u'Disemba'] ),
            #'tr' :      lambda v: slh( v, [u'Ocak', u'Şubat', u'Mart', u'Nisan', u'Mayıs', u'Haziran', u'Temmuz', u'Ağustos', u'Eylül', u'Ekim', u'Kasım', u'Aralık'] ),
            #'tt' :      lambda v: slh( v, [u'Ğínwar', u'Febräl', u'Mart', u'Äpril', u'May', u'Yün', u'Yül', u'August', u'Sentäber', u'Öktäber', u'Nöyäber', u'Dekäber'] ),
            #'uk' :      lambda v: slh( v, [u'Січень', u'Лютий', u'Березень', u'Квітень', u'Травень', u'Червень', u'Липень', u'Серпень', u'Вересень', u'Жовтень', u'Листопад', u'Грудень'] ),
            #'ur' :      lambda v: slh( v, [u'جنوری', u'فروری', u'مارچ', u'اپريل', u'مئ', u'جون', u'جولائ', u'اگست', u'ستمبر', u'اکتوبر', u'نومبر', u'دسمبر'] ),
            #'vi' :      lambda v: slh( v, [u'Tháng một', u'Tháng hai', u'Tháng ba', u'Tháng tư', u'Tháng năm', u'Tháng sáu', u'Tháng bảy', u'Tháng tám', u'Tháng chín', u'Tháng mười', u'Tháng mười một', u'Tháng mười hai'] ),
            #'vo' :      lambda v: slh( v, [u'Yanul', u'Febul', u'Mäzul', u'Prilul', u'Mayul', u'Yunul', u'Yulul', u'Gustul', u'Setul', u'Tobul', u'Novul', u'Dekul'] ),
            #'wa' :      lambda v: slh( v, [u'Djanvî', u'Fevrî', u'Måss', u'Avri', u'May', u'Djun', u'Djulete', u'Awousse', u'Setimbe', u'Octôbe', u'Nôvimbe', u'Decimbe'] ),
            #'zh' :      lambda v: slh( v, makeMonthList( u'%d月' )),
    },

    'Number': {
        'da' :      lambda v: dh_noConv( v, u'%d (tal)' ),
        'en' :      lambda v: dh_noConv( v, u'%d (number)' ),
        'fr' :      lambda v: dh_noConv( v, u'%d (nombre)' ),
        'fr' :      lambda v: dh_noConv( v, u'%d (nombre)' ),
        'he' :      lambda v: dh_noConv( v, u'%d (מספר)' ),
        'ja' :      dh_simpleInt,
        'ko' :      dh_simpleInt,
        'la' :      dh_simpleInt,
        'nn' :      lambda v: dh_noConv( v, u'Talet %d' ),
        'no' :      lambda v: dh_noConv( v, u'%d (tall)' ),
        'ru' :      lambda v: dh_noConv( v, u'%d (число)' ),
        'sl' :      lambda v: dh_noConv( v, u'%d (število)' ),
        'sv' :      lambda v: dh_noConv( v, u'%d (tal)' ),
        'th' :      lambda v: dh_noConv( v, u'%d (จำนวน)' ),
        'zh' :      dh_simpleInt,
    },

    'YearAD': {
        'af' :      dh_simpleYearAD,
        'ar' :      dh_simpleYearAD,
        'ast':      dh_simpleYearAD,
        'be' :      dh_simpleYearAD,
        'bg' :      dh_simpleYearAD,
        'bs' :      dh_simpleYearAD,
        'ca' :      dh_simpleYearAD,
        'cs' :      dh_simpleYearAD,
        'csb':      dh_simpleYearAD,
        'cv' :      dh_simpleYearAD,
        'cy' :      dh_simpleYearAD,
        'da' :      dh_simpleYearAD,
        'de' :      dh_simpleYearAD,
        'el' :      dh_simpleYearAD,
        'en' :      dh_simpleYearAD,
        'eo' :      dh_simpleYearAD,
        'es' :      dh_simpleYearAD,
        'et' :      dh_simpleYearAD,
        'eu' :      dh_simpleYearAD,
        'fi' :      dh_simpleYearAD,
        'fo' :      dh_simpleYearAD,
        'fr' :      dh_simpleYearAD,
        'fy' :      dh_simpleYearAD,
        'gl' :      dh_simpleYearAD,
        'he' :      dh_simpleYearAD,
        'hr' :      dh_simpleYearAD,
        'hu' :      dh_simpleYearAD,
        'ia' :      dh_simpleYearAD,
        'id' :      dh_simpleYearAD,
        'ie' :      dh_simpleYearAD,
        'io' :      dh_simpleYearAD,
        'is' :      dh_simpleYearAD,
        'it' :      dh_simpleYearAD,
        'ja' :      lambda v: dh_noConvYear( v, u'%d年' ),
        'ka' :      dh_simpleYearAD,
        'kn' :      dh_knYearConverter,
        'ko' :      lambda v: dh_noConvYear( v, u'%d년' ),
        'ku' :      dh_simpleYearAD,
        'kw' :      dh_simpleYearAD,
        'la' :      dh_simpleYearAD,
        'lb' :      dh_simpleYearAD,
        'li' :      dh_simpleYearAD,
        'lt' :      dh_simpleYearAD,
        'lv' :      dh_simpleYearAD,
        'mi' :      dh_simpleYearAD,
        'mk' :      dh_simpleYearAD,
        'ms' :      dh_simpleYearAD,
        'nap':      dh_simpleYearAD,
        'nds':      dh_simpleYearAD,
        'nl' :      dh_simpleYearAD,
        'nn' :      dh_simpleYearAD,
        'no' :      dh_simpleYearAD,
        'os' :      dh_simpleYearAD,
        'pl' :      dh_simpleYearAD,
        'pt' :      dh_simpleYearAD,
        'ro' :      dh_simpleYearAD,
        'ru' :      dh_simpleYearAD,
        'scn':      dh_simpleYearAD,
        'simple' :  dh_simpleYearAD,
        'sk' :      dh_simpleYearAD,
        'sl' :      dh_simpleYearAD,
        'sq' :      dh_simpleYearAD,
        'sr' :      dh_simpleYearAD,
        'sv' :      dh_simpleYearAD,
        'te' :      dh_simpleYearAD,

        #2005 => 'พ.ศ. 2548'
        'th' :      lambda v: dh( v, u'พ.ศ. %d',                lambda i: i + 543, lambda l: l[0] - 543 ),
        'tl' :      dh_simpleYearAD,
        'tr' :      dh_simpleYearAD,
        'tt' :      dh_simpleYearAD,
        'uk' :      dh_simpleYearAD,
        'ur' :      lambda v: dh_noConvYear( v, u'%dسبم' ),
        'vi' :      dh_simpleYearAD,
        'wa' :      dh_simpleYearAD,
        'zh' :      lambda v: dh_noConvYear( v, u'%d年' ),
        'zh-min-nan' :  lambda v: dh_noConvYear( v, u'%d nî' ),
    },

    'YearBC': {
        'af' :      lambda v: dh_noConvYear( v, u'%d v.C.' ),
        'bg' :      lambda v: dh_noConvYear( v, u'%d г. пр.н.е.' ),
        'bs' :      lambda v: dh_noConvYear( v, u'%d p.ne.' ),
        'ca' :      lambda v: dh_noConvYear( v, u'%d aC' ),
        'da' :      lambda v: dh_noConvYear( v, u'%d f.Kr.' ),
        'de' :      lambda v: dh_noConvYear( v, u'%d v. Chr.' ),
        'en' :      lambda v: dh_noConvYear( v, u'%d BC' ),
        'eo' :      lambda v: dh_noConvYear( v, u'-%d' ),
        'es' :      lambda v: dh_noConvYear( v, u'%d adC' ),
        'et' :      lambda v: dh_noConvYear( v, u'%d eKr' ),
        'fi' :      lambda v: dh_noConvYear( v, u'%d eaa' ),
        'fo' :      lambda v: dh_noConvYear( v, u'%d f. Kr.' ),
        'fr' :      lambda v: dh_noConvYear( v, u'-%d' ),
        'gl' :      lambda v: dh_noConvYear( v, u'-%d' ),
        'he' :      lambda v: dh_noConvYear( v, u'%d לפנה"ס' ),
        'hr' :      lambda v: dh_noConvYear( v, u'%d p.n.e.' ),
        'id' :      lambda v: dh_noConvYear( v, u'%d SM' ),
        'io' :      lambda v: dh_noConvYear( v, u'%d aK' ),
        'is' :      lambda v: dh_noConvYear( v, u'%d f. Kr.' ),
        'it' :      lambda v: dh_noConvYear( v, u'%d AC' ),
        'ko' :      lambda v: dh_noConvYear( v, u'기원전 %d년' ),
        'la' :      lambda v: dh_noConvYear( v, u'%d a.C.n.' ),
        'lb' :      lambda v: dh_noConvYear( v, u'-%d' ),
        'ms' :      lambda v: dh_noConvYear( v, u'%d SM' ),
        'nap':      lambda v: dh_noConvYear( v, u'%d AC' ),
        'nds':      lambda v: dh_noConvYear( v, u'%d v. Chr.' ),
        'nl' :      lambda v: dh_noConvYear( v, u'%d v. Chr.' ),
        'nn' :      lambda v: dh_noConvYear( v, u'-%d' ),
        'no' :      lambda v: dh_noConvYear( v, u'%d f.Kr.' ),
        'pl' :      lambda v: dh_noConvYear( v, u'%d p.n.e.' ),
        'pt' :      lambda v: dh_noConvYear( v, u'%d a.C.' ),
        'ro' :      lambda v: dh_noConvYear( v, u'%d î.Hr.' ),
        'ru' :      lambda v: dh_noConvYear( v, u'%d до н. э.' ),
        'scn':      lambda v: dh_noConvYear( v, u'%d a.C.' ),
        'sl' :      lambda v: dh_noConvYear( v, u'%d pr. n. št.' ),
        'sr' :      lambda v: dh_noConvYear( v, u'%d. пне.' ),
        'sv' :      lambda v: dh_noConvYear( v, u'%d f.Kr.' ),
        'tt' :      lambda v: dh_noConvYear( v, u'MA %d' ),
        'uk' :      lambda v: dh_noConvYear( v, u'%d до Р.Х.' ),
        'zh' :      lambda v: dh_noConvYear( v, u'前%d年' ),
    },

    'DecadeAD': {
        'bg' :      lambda v: dh_dec( v, u'%d-те' ),
        'bs' :      lambda v: dh_dec( v, u'%dte' ),
        'ca' :      lambda v: dh_dec( v, u'Dècada del %d' ),
        'cy' :      lambda v: dh_dec( v, u'%dau' ),
        'da' :      lambda v: dh_dec( v, u"%d'erne" ),
        'de' :      lambda v: dh_dec( v, u'%der' ),
        'el' :      lambda v: dh_dec( v, u'Δεκαετία %d' ),
        'en' :      lambda v: dh_dec( v, u'%ds' ),
        'eo' :      lambda v: dh_dec( v, u'%d-aj jaroj' ),
        'es' :      lambda v: dh_dec( v, u'Años %d' ),
        'et' :      lambda v: dh_dec( v, u'%d. aastad' ),
        'fi' :      lambda v: dh_dec( v, u'%d-luku' ),
        'fo' :      lambda v: dh_dec( v, u'%d-árini' ),
        'fr' :      lambda v: dh_dec( v, u'Années %d' ),

        #1970s => 1970-1979
        'hr' :      lambda v: dh( v, u'%d-%d',                   lambda i: (encDec0(i),encDec0(i)+9), lambda v: v[0] ),
        'io' :      lambda v: dh_dec( v, u'%da yari' ),

        #1970s => '1971–1980'
        'is' :      lambda v: dh( v, u'%d–%d',                   lambda i: (encDec1(i),encDec1(i)+9), lambda v: v[0]-1 ),
        'it' :      lambda v: dh_dec( v, u'Anni %d' ),
        'ja' :      lambda v: dh_dec( v, u'%d年代' ),
        'ko' :      lambda v: dh_dec( v, u'%d년대' ),

        #1970s => 'Decennium 198' (1971-1980)
        'la' :      lambda v: dh( v, u'Decennium %d',            lambda i: encDec1(i)/10+1, lambda v: (v[0]-1)*10 ),

        #1970s => 'XX amžiaus 8-as dešimtmetis' (1971-1980)
        'lt' :      lambda v: dh( v, u'%s amžiaus %d-as dešimtmetis',
                        lambda i: (romanNums[encDec1(i)/100+1], encDec1(i)%100/10+1),
                        lambda v: (v[0]-1)*100 + (v[1]-1)*10 ),

        #1970s => 'Ngahurutanga 198' (1971-1980)
        'mi' :      lambda v: dh( v, u'Ngahurutanga %d',         lambda i: encDec0(i)/10+1, lambda v: (v[0]-1)*10 ),

        #1970s => '1970-1979'
        'nl' :      lambda v: dh( v, u'%d-%d',                   lambda i: (encDec0(i),encDec0(i)+9), decSinglVal ),
        'no' :      lambda v: dh_dec( v, u'%d-årene' ),

        #1970s => 'Lata 70. XX wieku'
        'pl' :      lambda v: dh( v, u'Lata %d. %s wieku',
                    lambda i: (encDec0(i)%100, romanNums[ encDec0(i)/100+1 ]),
                    lambda v: (v[1]-1)*100 + v[0] ),

        'pt' :      lambda v: dh_dec( v, u'Década de %d' ),
        'ro' :      lambda v: dh_dec( v, u'Anii %d' ),
        'ru' :      lambda v: dh_dec( v, u'%d-е' ),
        'scn':      lambda v: dh_dec( v, u'%dini' ),
        'simple' :  lambda v: dh_dec( v, u'%ds' ),

        # 1970 => '70. roky 20. storočia'
        'sk' :      lambda v: dh( v, u'%d. roky %d. storočia',
                    lambda i: (encDec0(i)%100, encDec0(i)/100+1),
                    lambda v: (v[1]-1)*100 + v[0] ),

        'sl' :      lambda v: dh_dec( v, u'%d.' ),
        'sv' :      lambda v: dh_dec( v, u'%d-talet' ),
        'tt' :      lambda v: dh_dec( v, u'%d. yıllar' ),
        'uk' :  lambda v: multi( v, [
            (lambda x: dh_dec( x, u'%d-ві' ), lambda x: x == 0 or (x % 100 == 40)),
            (lambda x: dh_dec( x, u'%d-ні' ), lambda x: x % 1000 == 0),
            (lambda x: dh_dec( x, u'%d-ті' ), lambda x: True)]),
        'wa' :      lambda v: dh_dec( v, u'Anêyes %d' ),
        'zh' :      lambda v: dh_dec( v, u'%d年代' ),
        'zh-min-nan' : lambda v: dh_dec( v, u'%d nî-tāi' ),
    },

    'DecadeBC': {
        'de' :      lambda v: dh_dec( v, u'%der v. Chr.' ),
        'en' :      lambda v: dh_dec( v, u'%ds BC' ),
        'es' :      lambda v: dh_dec( v, u'Años %d adC' ),
        'fr' :      lambda v: dh_dec( v, u'Années -%d' ),
        'hr' :      lambda v: dh_dec( v, u'%dih p.n.e.' ),
        'it' :      lambda v: dh_dec( v, u'Anni %d AC' ),
        'pt' :      lambda v: dh_dec( v, u'Década de %d a.C.' ),
        'ru' :      lambda v: dh_dec( v, u'%d-е до н. э.' ),
        'sl' :      lambda v: dh_dec( v, u'%d. pr. n. št.' ),
        'tt' :      lambda v: dh_dec( v, u'MA %d. yıllar' ),
        'uk' :  lambda v: multi( v, [
            (lambda x: dh_dec( x, u'%d-ві до Р.Х.' ), lambda x: x == 0 or (x % 100 == 40)),
            (lambda x: dh_dec( x, u'%d-ті до Р.Х.' ), lambda x: True)]),
        'zh' :      lambda v: dh_dec( v, u'前%d年代' ),
    },

    'CenturyAD': {
        'af' :      lambda v: dh_noConv( v, u'%dste eeu' ),
        'ang':      lambda v: dh_noConv( v, u'%de géarhundred' ),
        'ast':      lambda v: dh_roman( v, u'Sieglu %s' ),
        'be' :      lambda v: dh_noConv( v, u'%d стагодзьдзе' ),
        'bg' :      lambda v: dh_noConv( v, u'%d век' ),
        'bs' :      lambda v: dh_noConv( v, u'%d. vijek' ),
        'ca' :      lambda v: dh_roman( v, u'Segle %s' ),
        'cs' :      lambda v: dh_noConv( v, u'%d. století' ),
        'cy' :      lambda v: dh_noConv( v, u'%dfed ganrif' ),
        'da' :      lambda v: dh_noConv( v, u'%d. århundrede' ),
        'de' :      lambda v: dh_noConv( v, u'%d. Jahrhundert' ),
        'el' :      lambda v: dh_noConv( v, u'%dος αιώνας' ),
        'en' :      lambda v: multi( v, [
            (lambda x: dh_noConv( x, u'%dst century' ), lambda x: x == 1 or (x > 20 and x%10 == 1)),
            (lambda x: dh_noConv( x, u'%dnd century' ), lambda x: x == 2 or (x > 20 and x%10 == 2)),
            (lambda x: dh_noConv( x, u'%drd century' ), lambda x: x == 3 or (x > 20 and x%10 == 3)),
            (lambda x: dh_noConv( x, u'%dth century' ), lambda x: True)]),
        'eo' :      lambda v: dh_noConv( v, u'%d-a jarcento' ),
        'es' :      lambda v: dh_roman( v, u'Siglo %s' ),
        'et' :      lambda v: dh_noConv( v, u'%d. sajand' ),
        'fi' :      lambda v: dh( v, u'%d00-luku',                   lambda i: i-1, lambda v: v[0]+1 ),
        'fo' :      lambda v: dh_noConv( v, u'%d. øld' ),
        'fr' :      lambda v: dh_roman( v, u'%se siècle' ),
        'fy' :      lambda v: dh_noConv( v, u'%de ieu' ),
        'he' :      lambda v: dh_noConv( v, u'המאה ה-%d' ),
        #'hi' : u'बीसवी शताब्दी'
        'hr' :      lambda v: dh_noConv( v, u'%d. stoljeće' ),
        'id' :      lambda v: dh_noConv( v, u'Abad ke-%d' ),
        'io' :      lambda v: dh_noConv( v, u'%dma yar-cento' ),
        'it' :      lambda v: dh_roman( v, u'%s secolo' ),
        'is' :      lambda v: dh_noConv( v, u'%d. öldin' ),
        'ja' :      lambda v: dh_noConv( v, u'%d世紀' ),
        'ka' :      lambda v: dh_roman( v, u'%s საუკუნე' ),
        'ko' :      lambda v: dh_noConv( v, u'%d세기' ),
        'la' :      lambda v: dh_noConv( v, u'Saeculum %d' ),
        'lb' :      lambda v: dh_noConv( v, u'%d. Joerhonnert' ),
        #'li': u'Twintegste ieuw'
        'lt' :      lambda v: dh_roman( v, u'%s amžius' ),
        'lv' :      lambda v: dh_noConv( v, u'%d. gadsimts' ),
        'mi' :      lambda v: dh_noConv( v, u'Tua %d rau tau' ),
        'mk' :      lambda v: dh_noConv( v, u'%d век' ),
        'nl' :      lambda v: dh_noConv( v, u'%de eeuw' ),
        'nn' :      lambda v: dh( v, u'%d00-talet',                   lambda i: i-1, lambda v: v[0]+1 ),
        'no' :      lambda v: dh_noConv( v, u'%d. århundre' ),
        'pl' :      lambda v: dh_roman( v, u'%s wiek' ),
        'pt' :      lambda v: dh_roman( v, u'Século %s' ),
        'ro' :      lambda v: dh_roman( v, u'Secolul al %s-lea' ),
        'ru' :      lambda v: dh_roman( v, u'%s век' ),
        'scn':      lambda v: dh_roman( v, u'Seculu %s' ),
        'simple' :  lambda v: multi( v, [
            (lambda x: dh_noConv( x, u'%dst century' ), lambda x: x == 1 or (x > 20 and x%10 == 1)),
            (lambda x: dh_noConv( x, u'%dnd century' ), lambda x: x == 2 or (x > 20 and x%10 == 2)),
            (lambda x: dh_noConv( x, u'%drd century' ), lambda x: x == 3 or (x > 20 and x%10 == 3)),
            (lambda x: dh_noConv( x, u'%dth century' ), lambda x: True)]),
        'sk' :      lambda v: dh_noConv( v, u'%d. storočie' ),
        'sl' :      lambda v: dh_noConv( v, u'%d. stoletje' ),
        'sv' :      lambda v: dh( v, u'%d00-talet',                   lambda i: i-1, lambda v: v[0]+1 ),
        'th' :      lambda v: dh_noConv( v, u'คริสต์ศตวรรษที่ %d' ),
        'tr' :      lambda v: dh_noConv( v, u'%d. yüzyıl' ),
        'tt' :      lambda v: dh_noConv( v, u'%d. yöz' ),
        'uk' :      lambda v: dh_noConv( v, u'%d століття' ),
        'wa' :      lambda v: dh_noConv( v, u'%dinme sieke' ),
        'zh' :      lambda v: dh_noConv( v, u'%d世纪' ),
        'zh-min-nan' : lambda v: dh_noConv( v, u'%d sè-kí' ),
    },

    'CenturyBC': {
        'af' :      lambda v: dh_noConv( v, u'%de eeu v. C.' ),
        'ca' :      lambda v: dh_roman( v, u'Segle %s aC' ),
        'da' :      lambda v: dh_noConv( v, u'%d. århundrede f.Kr.' ),
        'de' :      lambda v: dh_noConv( v, u'%d. Jahrhundert v. Chr.' ),
        'en' :      lambda v: dh_noConv( v, u'%dth century BC' ),
        'eo' :      lambda v: dh_noConv( v, u'%d-a jarcento a.K.' ),
        'es' :      lambda v: dh_roman( v, u'Siglo %s adC' ),
        'et' :      lambda v: dh_noConv( v, u'%d. aastatuhat eKr' ),
        'fr' :      lambda v: dh_roman( v, u'%se siècle av. J.-C.' ),
        'he' :      lambda v: dh_noConv( v, u'המאה ה-%d לפנה"ס' ),
        'hr' :      lambda v: dh_noConv( v, u'%d. stoljeće p.n.e.' ),
        'id' :      lambda v: dh_noConv( v, u'Abad ke-%d SM' ),
        'io' :      lambda v: dh_noConv( v, u'%dma yar-cento aK' ),
        'it' :      lambda v: dh_roman( v, u'%s secolo AC' ),
        'ja' :      lambda v: dh_noConv( v, u'紀元前%d世紀' ),
        'la' :      lambda v: dh_noConv( v, u'Saeculum %d a.C.n.' ),
        'lb' :      lambda v: dh_noConv( v, u'%d. Joerhonnert v. Chr.' ),
        'nl' :      lambda v: dh_noConv( v, u'%de eeuw v. Chr.' ),
        'pl' :      lambda v: dh_roman( v, u'%s wiek p.n.e.' ),
        'ru' :      lambda v: dh_roman( v, u'%s век до н. э.' ),
        'scn':      lambda v: dh_roman( v, u'Seculu %s a. C.' ),
        'sl' :      lambda v: dh_noConv( v, u'%d. stoletje pr. n. št.' ),
        'tt' :      lambda v: dh_noConv( v, u'MA %d. yöz' ),
        'uk' :      lambda v: dh_noConv( v, u'%d століття до Р.Х.' ),
        'zh' :      lambda v: dh_noConv( v, u'前%d世纪' ),
    },

    'MillenniumAD': {
        'bg' :      lambda v: dh_noConv( v, u'%d хилядолетие' ),
        'de' :      lambda v: dh_noConv( v, u'%d. Jahrtausend' ),
        'el' :      lambda v: dh_noConv( v, u'%dη χιλιετία' ),
        'en' :      lambda v: dh_noConv( v, u'%dnd millennium' ),
        'es' :      lambda v: dh_roman( v, u'%s milenio' ),
        'fr' :      lambda v: dh_roman( v, u'%se millénaire' ),
        'it' :      lambda v: dh_roman( v, u'%s millennio' ),
        'ja' :      lambda v: dh_noConv( v, u'%d千年紀' ),
        'lb' :      lambda v: dh_noConv( v, u'%d. Joerdausend' ),
        'lt' :      lambda v: dh_noConv( v, u'%d tūkstantmetis' ),
        #'pt' : u'Segundo milénio d.C.'
        'ro' :      lambda v: dh_roman( v, u'Mileniul %s' ),
        'ru' :      lambda v: dh_noConv( v, u'%d тысячелетие' ),
        'sk' :      lambda v: dh_noConv( v, u'%d. tisícročie' ),
        'sl' :      lambda v: dh_noConv( v, u'%d. tisočletje' ),
        'tt' :      lambda v: dh_noConv( v, u'%d. meñyıllıq' ),
        #'sv' : u'1000-talet (millennium)'
        #'ur' : u'1000مبم'
    },

    'MillenniumBC': {
        'bg' :      lambda v: dh_noConv( v, u'%d хилядолетие пр.н.е.' ),
        'da' :      lambda v: dh_noConv( v, u'%d. årtusinde f.Kr.' ),
        'de' :      lambda v: dh_noConv( v, u'%d. Jahrtausend v. Chr.' ),
        'el' :      lambda v: dh_noConv( v, u'%dη χιλιετία π.Χ.' ),
        'en' :      lambda v: dh_noConv( v, u'%dst millennium BC' ),
        'es' :      lambda v: dh_roman( v, u'%s milenio adC' ),
        'fr' :      lambda v: dh_roman( v, u'%ser millénaire av. J.-C.' ),
        'he' :      lambda v: dh_noConv( v, u'המילניום ה-%d לפנה"ס' ),
        'it' :      lambda v: dh_roman( v, u'%s millennio AC' ),
        'ja' :      lambda v: dh_noConv( v, u'紀元前%d千年紀' ),
        'lb' :      lambda v: dh_noConv( v, u'%d. Joerdausend v. Chr.' ),
        #'pt' : u'Primeiro milénio a.C.'
        'ro' :      lambda v: dh_roman( v, u'Mileniul %s î.Hr.' ),
        'ru' :      lambda v: dh_noConv( v, u'%d тысячелетие до н. э.' ),
        'tt' :      lambda v: dh_noConv( v, u'MA %d. meñyıllıq' ),
        'zh' :      lambda v: dh_noConv( v, u'前%d千年' ),
    },

    'Cat_Year_MusicAlbums': {
        'en' :      lambda v: dh_noConv( v, u'Category:%d albums' ),
        'fr' :      lambda v: dh_noConv( v, u'Catégorie:Album musical sorti en %d' ),
        'pl' :      lambda v: dh_noConv( v, u'Kategoria:Albumy muzyczne wydane w roku %d' ),
        'sv' :      lambda v: dh_noConv( v, u'Kategori:%d års musikalbum' ),
    },

    'CurrEvents': {
        'ang':      lambda v: dh_singVal( v, u'Efenealde belimpas' ),
        'ar' :      lambda v: dh_singVal( v, u'الأحداث الجارية' ),
        'bg' :      lambda v: dh_singVal( v, u'Текущи събития' ),
        'ca' :      lambda v: dh_singVal( v, u'Viquipèdia:Actualitat' ),
        'cs' :      lambda v: dh_singVal( v, u'Aktuality' ),
        'da' :      lambda v: dh_singVal( v, u'Aktuelle begivenheder' ),
        'de' :      lambda v: dh_singVal( v, u'Aktuelle Ereignisse' ),
        'en' :      lambda v: dh_singVal( v, u'Current events' ),
        'eo' :      lambda v: dh_singVal( v, u'Aktualaĵoj' ),
        'es' :      lambda v: dh_singVal( v, u'Actualidad' ),
        'et' :      lambda v: dh_singVal( v, u'Current events' ),
        'fa' :      lambda v: dh_singVal( v, u'وقایع کنونی' ),
        'fi' :      lambda v: dh_singVal( v, u'Ajankohtaista' ),
        'fr' :      lambda v: dh_singVal( v, u'Actualités' ),
        'gl' :      lambda v: dh_singVal( v, u'Novas' ),
        'he' :      lambda v: dh_singVal( v, u'ויקיפדיה:אקטואליה' ),
        'hu' :      lambda v: dh_singVal( v, u'Friss események' ),
        'id' :      lambda v: dh_singVal( v, u'Wikipedia:Peristiwa terkini' ),
        'io' :      lambda v: dh_singVal( v, u'Current events' ),
        'it' :      lambda v: dh_singVal( v, u'Attualità' ),
        'ja' :      lambda v: dh_singVal( v, u'最近の出来事' ),
        'ka' :      lambda v: dh_singVal( v, u'ახალი ამბები' ),
        'ko' :      lambda v: dh_singVal( v, u'요즘 화제' ),
        'ku' :      lambda v: dh_singVal( v, u'Bûyerên rojane' ),
        'la' :      lambda v: dh_singVal( v, u'Novissima' ),
        'lb' :      lambda v: dh_singVal( v, u'Aktualitéit' ),
        'li' :      lambda v: dh_singVal( v, u"In 't nuuis" ),
        'mn' :      lambda v: dh_singVal( v, u'Мэдээ' ),
        'nl' :      lambda v: dh_singVal( v, u'In het nieuws' ),
        'os' :      lambda v: dh_singVal( v, u'Xabar' ),
        'pl' :      lambda v: dh_singVal( v, u'Bieżące wydarzenia' ),
        'pt' :      lambda v: dh_singVal( v, u'Eventos atuais' ),
        'ro' :      lambda v: dh_singVal( v, u'Actualităţi' ),
        'ru' :      lambda v: dh_singVal( v, u'Текущие события' ),
        'simple':   lambda v: dh_singVal( v, u'World news' ),
        'sl' :      lambda v: dh_singVal( v, u'Trenutni dogodki' ),
        'sr' :      lambda v: dh_singVal( v, u'Тренутни догађаји' ),
        'sv' :      lambda v: dh_singVal( v, u'Aktuella händelser' ),
        'th' :      lambda v: dh_singVal( v, u'เหตุการณ์ปัจจุบัน' ),
        'tl' :      lambda v: dh_singVal( v, u'Kasalukuyang pangyayari' ),
        'tr' :      lambda v: dh_singVal( v, u'Güncel olaylar' ),
        'uk' :      lambda v: dh_singVal( v, u'Поточні події' ),
        'ur' :      lambda v: dh_singVal( v, u'حالات حاضرہ' ),
        'vi' :      lambda v: dh_singVal( v, u'Thời sự' ),
        'wa' :      lambda v: dh_singVal( v, u'Wikinoveles' ),
        'yo' :      lambda v: dh_singVal( v, u'Current events' ),
        'zh' :      lambda v: dh_singVal( v, u'新闻动态' ),
        'zh-min-nan': lambda v: dh_singVal( v, u'Sin-bûn sū-kiāⁿ' ),
    },
}

formatLimits = {
    'January'			: (1, days_in_month[1], 1),
    'February'			: (1, days_in_month[2], 1),
    'March'				: (1, days_in_month[3], 1),
    'April'				: (1, days_in_month[4], 1),
    'May'				: (1, days_in_month[5], 1),
    'June'				: (1, days_in_month[6], 1),
    'July'				: (1, days_in_month[7], 1),
    'August'			: (1, days_in_month[8], 1),
    'September'			: (1, days_in_month[9], 1),
    'October'			: (1, days_in_month[10], 1),
    'November'			: (1, days_in_month[11], 1),
    'December'			: (1, days_in_month[12], 1),

    'Year_January'		: (1900, 2050, 1),
    'Year_February'		: (1900, 2050, 1),
    'Year_March'		: (1900, 2050, 1),
    'Year_April'		: (1900, 2050, 1),
    'Year_May'			: (1900, 2050, 1),
    'Year_June'			: (1900, 2050, 1),
    'Year_July'			: (1900, 2050, 1),
    'Year_August'		: (1900, 2050, 1),
    'Year_September'	: (1900, 2050, 1),
    'Year_October'		: (1900, 2050, 1),
    'Year_November'		: (1900, 2050, 1),
    'Year_December'		: (1900, 2050, 1),

    'MonthName'			: (1,12,1),
    'Number'			: (1,10,1),

    'YearAD'			: (0,2050,1),
    'YearBC'			: (0,500,1),
    'DecadeAD'			: (0,2050,10),
    'DecadeBC'			: (0,500,10),
    'CenturyAD'			: (1,25,1),
    'CenturyBC'			: (1,25,1),
    'MillenniumAD'		: (1,5,1),
    'MillenniumBC'		: (1,5,1),

    'Cat_Year_MusicAlbums'	: (1950, 2020, 1),
    'CurrEvents'			: (0,0,1),
}

def addFmt( type, lang, isMnthOfYear, patterns ):
    """Add 12 month formats for a specific type ('January','Feb..), for a given language.
    The function must accept one parameter for the ->int or ->string conversions, just like
    everywhere else in the formats map.
    The patterns parameter is a list of 12 elements to be used for each month.
    """
    if len(patterns) != 12:
        raise ValueError(u'pattern %s does not have 12 elements' % lang )
    if len(type) != 12:
        raise ValueError(u'type %s does not have 12 elements' % lang )

    for i in range(12):
        if patterns[i] != None:
            if isMnthOfYear:
                formats[type[i]][lang] = eval(u'lambda v: dh_MnthOfYear( v, u"%s" )' % patterns[i])
            else:
                formats[type[i]][lang] = eval(u'lambda v: dh_dayOfMnth( v, u"%s" )' % patterns[i])

def makeMonthList( pattern ):
    return [ pattern % m for m in range(1,13) ]

def makeMonthNamedList( lang, pattern, makeUpperCase = None ):
    """Creates a list of 12 elements based on the name of the month.
    The language-dependent month name is used as a formating argument to the pattern.
    The pattern must be have one %s that will be replaced by the localized month name.
    Use %%d for any other parameters that should be preserved.
    """
    if makeUpperCase == None:
        f = lambda s: s
    elif makeUpperCase == True:
        f = lambda s: s[0].upper() + s[1:]
    elif makeUpperCase == False:
        f = lambda s: s[0].lower() + s[1:]

    return [ pattern % f(monthName(lang, m)) for m in range(1,13) ]


#
# Add day of the month formats to the formatting table:   "en:May 15"
#
addFmt( dayMnthFmts, 'af', False,       makeMonthNamedList( 'af', u"%%d %s", True ))
addFmt( dayMnthFmts, 'an', False,       [ u"%d de chinero", u"%d de frebero", u"%d de marzo", u"%d d'abril", u"%d de mayo", u"%d de chunio", u"%d de chulio", u"%d d'agosto", u"%d de setiembre", u"%d d'otubre", u"%d de nobiembre", u"%d d'abiento" ])
addFmt( dayMnthFmts, 'ang',False,       [ u"%d Æfterra Géola", u"%d Solmónaþ", u"%d Hréþmónaþ", u"%d Éastermónaþ", u"%d Þrimilcemónaþ", u"%d Séremónaþ", u"%d Mǽdmónaþ", u"%d Wéodmónaþ", u"%d Háligmónaþ", u"%d Winterfylleþ", u"%d Blótmónaþ", u"%d Géolmónaþ" ])
addFmt( dayMnthFmts, 'ar', False,       [ u"%d يناير", u"%d فبراير", u"%d مارس", u"%d إبريل", u"%d مايو", u"%d يونيو", u"%d يوليو", u"%d أغسطس", u"%d سبتمبر", u"%d اكتوبر", u"%d نوفمبر", u"%d ديسمبر" ])
addFmt( dayMnthFmts, 'ast',False,       [ u"%d de xineru", u"%d de febreru", u"%d de marzu", u"%d d'abril", u"%d de mayu", u"%d de xunu", u"%d de xunetu", u"%d d'agostu", u"%d de setiembre", u"%d d'ochobre", u"%d de payares", u"%d d'avientu" ])
addFmt( dayMnthFmts, 'be', False,       [ u"%d студзеня", u"%d лютага", u"%d сакавіка", u"%d красавіка", u"%d траўня", u"%d чэрвеня", u"%d ліпеня", u"%d жніўня", u"%d верасьня", u"%d кастрычніка", u"%d лістапада", u"%d сьнежня" ])
addFmt( dayMnthFmts, 'bg', False,       makeMonthNamedList( 'bg', u"%%d %s", False ))
addFmt( dayMnthFmts, 'bs', False,       makeMonthNamedList( 'bs', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'ca', False,       [ u"%d de gener", u"%d de febrer", u"%d de març", u"%d d'abril", u"%d de maig", u"%d de juny", u"%d de juliol", u"%d d'agost", u"%d de setembre", u"%d d'octubre", u"%d de novembre", u"%d de desembre" ])
addFmt( dayMnthFmts, 'co', False,       [ u"%d di ghjennaghju", u"%d di frivaghju", u"%d di marzu", u"%d d'aprile", u"%d di maghju", u"%d di ghjugnu", u"%d di lugliu", u"%d d'aostu", u"%d di settembre", u"%d d'uttrovi", u"%d di nuvembri", u"%d di decembre" ])
addFmt( dayMnthFmts, 'cs', False,       makeMonthNamedList( 'cs', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'csb',False,       makeMonthNamedList( 'csb', u"%%d %sa", False ))
addFmt( dayMnthFmts, 'cv', False,       makeMonthNamedList( 'cv', u"%s, %%d", True ))
addFmt( dayMnthFmts, 'cy', False,       makeMonthNamedList( 'cy', u"%%d %s", True ))
addFmt( dayMnthFmts, 'da', False,       makeMonthNamedList( 'da', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'de', False,       makeMonthNamedList( 'de', u"%%d. %s", True ))
addFmt( dayMnthFmts, 'el', False,       [ u"%d Ιανουαρίου", u"%d Φεβρουαρίου", u"%d Μαρτίου", u"%d Απριλίου", u"%d Μαΐου", u"%d Ιουνίου", u"%d Ιουλίου", u"%d Αυγούστου", u"%d Σεπτεμβρίου", u"%d Οκτωβρίου", u"%d Νοεμβρίου", u"%d Δεκεμβρίου" ])
addFmt( dayMnthFmts, 'en', False,       makeMonthNamedList( 'en', u"%s %%d", True ))
addFmt( dayMnthFmts, 'eo', False,       makeMonthNamedList( 'eo', u"%%d-a de %s", False ))
addFmt( dayMnthFmts, 'es', False,       makeMonthNamedList( 'es', u"%%d de %s", False ))
addFmt( dayMnthFmts, 'et', False,       makeMonthNamedList( 'et', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'eu', False,       makeMonthNamedList( 'eu', u"%saren %%d", True ))
addFmt( dayMnthFmts, 'fi', False,       makeMonthNamedList( 'fi', u"%%d. %sta", False ))
addFmt( dayMnthFmts, 'fo', False,       makeMonthNamedList( 'fo', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'fr', False,       [ u"%d janvier", u"%d février", u"%d mars", u"%d avril", u"%d mai", u"%d juin", u"%d juillet", u"%d août", u"%d septembre", u"%d octobre", u"%d novembre", u"%d décembre" ])
addFmt( dayMnthFmts, 'fy', False,       makeMonthNamedList( 'fy', u"%%d %s", False ))
addFmt( dayMnthFmts, 'ga', False,       [ u"%d Eanáir", u"%d Feabhra", u"%d Márta", u"%d Aibreán", u"%d Bealtaine", u"%d Meitheamh", u"%d Iúil", u"%d Lúnasa", u"%d Meán Fómhair", u"%d Deireadh Fómhair", u"%d Samhain", u"%d Mí na Nollag" ])
addFmt( dayMnthFmts, 'gl', False,       makeMonthNamedList( 'gl', u"%%d de %s", False ))
addFmt( dayMnthFmts, 'he', False,       makeMonthNamedList( 'he', u"%%d ב%s"))      # [ u"%d בינואר", u"%d בפברואר", u"%d במרץ", u"%d באפריל", u"%d במאי", u"%d ביוני", u"%d ביולי", u"%d באוגוסט", u"%d בספטמבר", u"%d באוקטובר", u"%d בנובמבר", u"%d בדצמבר" ])
addFmt( dayMnthFmts, 'hr', False,       [ u"%d. siječnja", u"%d. veljače", u"%d. ožujka", u"%d. travnja", u"%d. svibnja", u"%d. lipnja", u"%d. srpnja", u"%d. kolovoza", u"%d. rujna", u"%d. listopada", u"%d. studenog", u"%d. prosinca" ])
addFmt( dayMnthFmts, 'hu', False,       makeMonthNamedList( 'hu', u"%s %%d", True ))
addFmt( dayMnthFmts, 'ia', False,       makeMonthNamedList( 'ia', u"%%d de %s", False ))
addFmt( dayMnthFmts, 'id', False,       makeMonthNamedList( 'id', u"%%d %s", True ))
addFmt( dayMnthFmts, 'ie', False,       makeMonthNamedList( 'ie', u"%%d %s", False ))
addFmt( dayMnthFmts, 'io', False,       makeMonthNamedList( 'io', u"%%d di %s", False ))
addFmt( dayMnthFmts, 'is', False,       [ u"%d. janúar", u"%d. febrúar", u"%d. mars", u"%d. apríl", u"%d. maí", u"%d. júní", u"%d. júlí", u"%d. ágúst", u"%d. september", u"%d. október", u"%d. nóvember", u"%d. desember" ])
addFmt( dayMnthFmts, 'it', False,       makeMonthNamedList( 'it', u"%%d %s", False ))
addFmt( dayMnthFmts, 'ja', False,       makeMonthList( u"%d月%%d日" ))
addFmt( dayMnthFmts, 'jv', False,       makeMonthNamedList( 'jv', u"%%d %s", True ))
addFmt( dayMnthFmts, 'ka', False,       makeMonthNamedList( 'ka', u"%%d %s" ))
addFmt( dayMnthFmts, 'ko', False,       makeMonthList( u"%d월 %%d일" ))
addFmt( dayMnthFmts, 'ku', False,       [ u"%d'ê rêbendanê", u"%d'ê reşemiyê", u"%d'ê adarê", u"%d'ê avrêlê", u"%d'ê gulanê", u"%d'ê pûşperê", u"%d'ê tîrmehê", u"%d'ê gelawêjê", u"%d'ê rezberê", u"%d'ê kewçêrê", u"%d'ê sermawezê", u"%d'ê berfanbarê" ])
addFmt( dayMnthFmts, 'la', False,       [ u"%d Ianuarii", u"%d Februarii", u"%d Martii", u"%d Aprilis", u"%d Maii", u"%d Iunii", u"%d Iulii", u"%d Augusti", u"%d Septembris", u"%d Octobris", u"%d Novembris", u"%d Decembris" ])
addFmt( dayMnthFmts, 'lb', False,       makeMonthNamedList( 'lb', u"%%d. %s", True ))
addFmt( dayMnthFmts, 'li', False,       [ u"%d januari", u"%d februari", u"%d miert", u"%d april", u"%d mei", u"%d juni", u"%d juli", u"%d augustus", u"%d september", u"%d oktober", u"%d november", u"%d december" ])
addFmt( dayMnthFmts, 'lt', False,       [ u"Sausio %d", u"Vasario %d", u"Kovo %d", u"Balandžio %d", u"Gegužės %d", u"Birželio %d", u"Liepos %d", u"Rugpjūčio %d", u"Rugsėjo %d", u"Spalio %d", u"Lapkričio %d", u"Gruodžio %d" ])
addFmt( dayMnthFmts, 'mk', False,       [ u"%d јануари", u"%d февруари", u"%d март", u"%d април", u"%d мај", u"%d јуни", u"%d јули", u"%d август", u"%d септември", u"%d октомври", u"%d ноември", u"%d декември" ])
addFmt( dayMnthFmts, 'ml', False,       makeMonthNamedList( 'ml', u"%s %%d" ))
addFmt( dayMnthFmts, 'ms', False,       makeMonthNamedList( 'ms', u"%%d %s", True ))
addFmt( dayMnthFmts, 'nap',False,       makeMonthNamedList( 'nap', u"%%d 'e %s", False ))
addFmt( dayMnthFmts, 'nds',False,       [ u"%d Januar", u"%d Februar", u"%d März", u"%d April", u"%d Mai", u"%d Juni", u"%d Juli", u"%d August", u"%d September", u"%d Oktober", u"%d November", u"%d Dezember" ])
addFmt( dayMnthFmts, 'nl', False,       [ u"%d januari", u"%d februari", u"%d maart", u"%d april", u"%d mei", u"%d juni", u"%d juli", u"%d augustus", u"%d september", u"%d oktober", u"%d november", u"%d december" ])
addFmt( dayMnthFmts, 'nn', False,       makeMonthNamedList( 'nn', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'no', False,       makeMonthNamedList( 'no', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'oc', False,       [ u"%d de genièr", u"%d de febrièr", u"%d de març", u"%d d'abril", u"%d de mai", u"%d de junh", u"%d de julhet", u"%d d'agost", u"%d de setembre", u"%d d'octobre", u"%d de novembre", u"%d de decembre" ])
addFmt( dayMnthFmts, 'os', False,       [ None, None, u"%d мартъийы", None, None, None, u"%d июлы", None, None, None, None, None ])
addFmt( dayMnthFmts, 'pl', False,       [ u"%d stycznia", u"%d lutego", u"%d marca", u"%d kwietnia", u"%d maja", u"%d czerwca", u"%d lipca", u"%d sierpnia", u"%d września", u"%d października", u"%d listopada", u"%d grudnia" ])
addFmt( dayMnthFmts, 'pt', False,       makeMonthNamedList( 'pt', u"%%d de %s", True ))
addFmt( dayMnthFmts, 'ro', False,       makeMonthNamedList( 'ro', u"%%d %s", False ))
addFmt( dayMnthFmts, 'ru', False,       [ u"%d января", u"%d февраля", u"%d марта", u"%d апреля", u"%d мая", u"%d июня", u"%d июля", u"%d августа", u"%d сентября", u"%d октября", u"%d ноября", u"%d декабря" ])
addFmt( dayMnthFmts, 'scn',False,       makeMonthNamedList( 'scn', u"%%d di %s", False ))
addFmt( dayMnthFmts, 'se', False,       [ u"ođđajagimánu %d.", u"guovvamánu %d.", u"njukčamánu %d.", u"cuoŋománu %d.", u"miessemánu %d.", u"geassemánu %d.", u"suoidnemánu %d.", u"borgemánu %d.", u"čakčamánu %d.", u"golggotmánu %d.", u"skábmamánu %d.", u"juovlamánu %d." ])
addFmt( dayMnthFmts, 'simple',False,        makeMonthNamedList( 'simple', u"%s %%d", True ))
addFmt( dayMnthFmts, 'sk', False,       makeMonthNamedList( 'sk', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'sl', False,       makeMonthNamedList( 'sl', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'sq', False,       [ u"%d Janar", u"%d Shkurt", u"%d Mars", u"%d Prill", u"%d Maj", u"%d Qershor", u"%d Korrik", u"%d Gusht", u"%d Shtator", u"%d Tetor", u"%d Nëntor", u"%d Dhjetor" ])
addFmt( dayMnthFmts, 'sr', False,       makeMonthNamedList( 'sr', u"%%d. %s", False ))
addFmt( dayMnthFmts, 'sv', False,       makeMonthNamedList( 'sv', u"%%d %s", False ))
addFmt( dayMnthFmts, 'te', False,       makeMonthNamedList( 'te', u"%s %%d" ))
addFmt( dayMnthFmts, 'th', False,       makeMonthNamedList( 'th', u"%%d %s" ))
addFmt( dayMnthFmts, 'tl', False,       [ u"Enero %d", u"Pebrero %d", u"Marso %d", u"Abríl %d", u"Mayo %d", u"Hunyo %d", u"Hulyo %d", u"Agosto %d", u"Setyembre %d", u"Oktubre %d", u"Nobyembre %d", u"Disyembre %d" ])
addFmt( dayMnthFmts, 'tr', False,       makeMonthNamedList( 'tr', u"%%d %s", True ))
addFmt( dayMnthFmts, 'tt', False,       makeMonthNamedList( 'tt', u"%%d. %s", True ))
addFmt( dayMnthFmts, 'uk', False,       [ u"%d січня", u"%d лютого", u"%d березня", u"%d квітня", u"%d травня", u"%d червня", u"%d липня", u"%d серпня", u"%d вересня", u"%d жовтня", u"%d листопада", u"%d грудня" ])
addFmt( dayMnthFmts, 'ur', False,       [ u"%d جنوری", u"%d فروری", u"%d مارچ", u"%d اپریل", u"%d مئ", u"%d جون", u"%d جلائ", u"%d اگست", u"%d ستمب", u"%d اکتوبر", u"%d نومب", u"%d دسمب" ])
addFmt( dayMnthFmts, 'vi', False,       makeMonthList( u"%%d tháng %d" ))
addFmt( dayMnthFmts, 'zh', False,       makeMonthList( u"%d月%%d日" ))

# Walloon names depend on the day number, thus we must generate various different patterns
waMonthNames = [ u"djanvî", u"fevrî", u"måss", u"avri", u"may", u"djun", u"djulete", u"awousse", u"setimbe", u"octôbe", u"nôvimbe", u"decimbe" ]

# For month names begining with a consonant...
for i in [0,1,2,4,5,6,8,10,11]:
    formats[dayMnthFmts[i]]['wa'] = eval(
        (u'lambda v: multi( v, [' +
            u'(lambda x: dh_noConv( x, u"%%dî d\' %s" ), lambda x: x == 1),' +
            u'(lambda x: dh_noConv( x, u"%%d d\' %s" ), lambda x: x in [2,3,20,22,23]),' +
            u'(lambda x: dh_noConv( x, u"%%d di %s" ), lambda x: True)])') % (waMonthNames[i],waMonthNames[i],waMonthNames[i]))
# For month names begining with a vowel...
for i in [3,7,9]:
    formats[dayMnthFmts[i]]['wa'] = eval(
        (u'lambda v: multi( v, [' +
            u'(lambda x: dh_noConv( x, u"%%dî d\' %s" ), lambda x: x == 1),' +
            u'(lambda x: dh_noConv( x, u"%%d d\' %s" ), lambda x: True)])') % (waMonthNames[i],waMonthNames[i]))


#
# Month of the Year: "en:May 1976"
#
addFmt( yrMnthFmts, 'af', True,     makeMonthNamedList( 'af', u"%s %%d", True ))
addFmt( yrMnthFmts, 'ang',True,     [ None, None, None, None, None, None, None, None, None, None, None, u"Gēolmōnaþ %d" ])
addFmt( yrMnthFmts, 'de', True,     makeMonthNamedList( 'de', u"%s %%d", True ))
addFmt( yrMnthFmts, 'el', True,     makeMonthNamedList( 'el', u"%s %%d", True ))
addFmt( yrMnthFmts, 'en', True,     makeMonthNamedList( 'en', u"%s %%d", True ))
addFmt( yrMnthFmts, 'es', True,     makeMonthNamedList( 'es', u"%s de %%d", True ))
addFmt( yrMnthFmts, 'et', True,     makeMonthNamedList( 'et', u"%s %%d", True ))
addFmt( yrMnthFmts, 'fi', True,     [ None, None, None, None, None, u"Huhtikuu %d", None, None, None, None, None, None ])
addFmt( yrMnthFmts, 'fr', True,     [ u"Janvier %d", u"Février %d", u"Mars %d", u"Avril %d", u"Mai %d", u"Juin %d", u"Juillet %d", u"Août %d", u"Septembre %d", u"Octobre %d", u"Novembre %d", u"Décembre %d" ])
addFmt( yrMnthFmts, 'it', True,     makeMonthNamedList( 'it', u"Attualità/Anno %%d - %s", True ))
addFmt( yrMnthFmts, 'ja', True,     [ u"「最近の出来事」%%d年%d月" % mm for mm in range(1,13)])
addFmt( yrMnthFmts, 'ka', True,     makeMonthNamedList( 'ka', u"%s, %%d" ))
addFmt( yrMnthFmts, 'ko', True,     [ u"%d년 1월", u"%d년 2월", u"%d년 3월", u"%d년 4월", u"%d년 5월", u"%d년 6월", u"%d년 7월", u"%d년 8월", u"%d년 9월", u"%d년 10월", u"%d년 11월", u"%d년 12월" ])
addFmt( yrMnthFmts, 'nl', True,     [ u"Januari %d", u"Februari %d", u"Maart %d", u"April %d", u"Mei %d", u"Juni %d", u"Juli %d", u"Augustus %d", u"September %d", u"Oktober %d", u"November %d", u"December %d" ])
addFmt( yrMnthFmts, 'pl', True,     makeMonthNamedList( 'pl', u"%s %%d", True ))
addFmt( yrMnthFmts, 'scn',True,     [ None, None, u"Marzu %d", None, None, None, None, None, None, None, None, None ])
addFmt( yrMnthFmts, 'simple', True, makeMonthNamedList( 'simple', u"%s %%d", True ))
addFmt( yrMnthFmts, 'sv', True,     makeMonthNamedList( 'sv', u"%s %%d", True ))
addFmt( yrMnthFmts, 'tt', True,     makeMonthNamedList( 'tt', u"%s, %%d", True ))
addFmt( yrMnthFmts, 'ur', True,     [ u"%d01مبم", u"%d02مبم", u"%d03مبم", u"%d04مبم", u"%d05مبم", u"%d06مبم", u"%d07مبم", u"%d08مبم", u"%d09مبم", u"%d10مبم", u"%d11مبم", u"%d12مبم" ])
addFmt( yrMnthFmts, 'vi', True,     makeMonthList( u"Tháng %d năm %%d" ))
addFmt( yrMnthFmts, 'zh', True,     makeMonthList( u"%%d年%d月" ))
addFmt( yrMnthFmts, 'zh-min-nan',True,  makeMonthList( u"%%d nî %d goe̍h" ))


def getDictionaryYear( lang, title, ignoreFirstLetterCase = True ):
    """Returns (dictName,value), where value can be a year, date, etc, and dictName is 'YearBC', 'December', etc."""
    for dictName, dict in formats.iteritems():
        try:
            year = dict[ lang ]( title )
            return (dictName,year)
        except:
            pass

    # sometimes the title may begin with an upper case while its listed as lower case, or the other way around
    # change case of the first character to the opposite, and try again
    if ignoreFirstLetterCase:
        try:
            if title[0].isupper():
                title = title[0].lower() + title[1:]
            else:
                title = title[0].upper() + title[1:]

            return getDictionaryYear(lang, title, ignoreFirstLetterCase = False)
        except:
            pass

    return (None,None)

class FormatDate(object):
    def __init__(self, site):
        self.site = site

    def __call__(self, m, d):
        return formats[enMonthNames[m-1]][self.site.lang](d)


def formatYear(lang, year):
    if year < 0:
        return formats['YearBC'][lang](-year)
    else:
        return formats['YearAD'][lang](year)



#
#
#  Map testing methods
#
#

def printMonthArray( lang, pattern, capitalize ):
    """
    """
    for s in makeMonthNamedList( lang, pattern, capitalize ):
        wikipedia.output( s )


def testMapEntry( showAll, m, year, testYear ):
    """This is a test function, to be used interactivelly to test the validity of the above maps.
    To test, run this function with the map name, year to be tested, and the final year expected.
    Usage example:
        run python interpreter
        >>> import date
        >>> date.testMapEntry( 'DecadeAD', 1992, 1990 )
        >>> date.testMapEntry( 'CenturyAD', 20, 20 )
    """
    
    start,end,step = formatLimits[m]
    if showAll:
        wikipedia.output(u"Limits: from %d to %d, with step %d" % (start,stop,step))
    
    for code, value in formats[m].iteritems():
        if showAll:
            wikipedia.output(u"%s[%s](%d)" % (m, code, year))
            wikipedia.output(u"                      -> '%s' -> %d" % (value(year), value(value(year))))
        if value(value(year)) != testYear:
            raise ValueError("%s[%s](%d) != %d: assert failed, years didn't match" % (m,code,year,testYear))


def testAll(showAll = False):
    """This is a test function, to be used interactivelly to test all year maps at once
    Usage example:
        run python interpreter
        >>> import date
        >>> date.testAll()
    """
    for d in formats.keys():

        if d in yearFormats:
            testMapEntry( showAll, d, 1992, 1992 )
        elif d in decadeFormats:
            testMapEntry( showAll, d, 1990, 1990 )
            testMapEntry( showAll, d, 1991, 1990 )
            testMapEntry( showAll, d, 1992, 1990 )
            testMapEntry( showAll, d, 1998, 1990 )
            testMapEntry( showAll, d, 1999, 1990 )
        elif d in centuryFormats:
            testMapEntry( showAll, d, 20, 20 )
        elif d in millFormats:
            testMapEntry( showAll, d, 2, 2 )
        elif d in dayMnthFmts:
            testMapEntry( showAll, d, 1, 1 )
            testMapEntry( showAll, d, 29, 29 )
        elif d in yrMnthFmts:
            testMapEntry( showAll, d, 2000, 2000 )
        elif d in snglValsFormats:
            testMapEntry( showAll, d, 0, 0 )
        elif d == 'MonthName':
            for v in range(1,12):
                testMapEntry( showAll, d, v, v )
        elif d == 'Cat_Year_MusicAlbums':
            testMapEntry( showAll, d, 2001, 2001 )
        elif d == 'Number':
            testMapEntry( showAll, d, 0, 0 )
        else:
            raise ValueError("unknown format %s" % d)
