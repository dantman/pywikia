# -*- coding: utf-8 -*-
def trans(char, default = '?'):
    # Give a transliteration for char, or default if none is known
    # Accented etc. Latin characters
    if char in u"ÀÁÂẦẤẪẨẬÃĀĂẰẮẴẶẲȦǠẠḀȂĄǍẢ":
        return "A"
    if char in u"ȀǞ":
        return "Ä"
    if char in u"Ǻ":
        return "Å"
    if char == u"Ä":
        return "Ae"
    if char == u"Å":
        return "Aa"
    if char in u"àáâầấẫẩậãāăằắẵặẳȧǡạḁȃąǎảẚ":
        return "a"
    if char in u"ȁǟ":
        return "ä"
    if char == u"ǻ":
        return "å"
    if char == u"ä":
        return "ae"
    if char == u"å":
        return "aa"
    if char in u"ḂḄḆƁƂ":
        return "B"
    if char in u"ḃḅḇƀɓƃ":
        return "b"
    if char in u"ĆĈĊÇČƇ":
        return "C"
    if char in u"ćĉċçčƈȼ":
        return "c"
    if char == u"Ḉ":
        return "Ç"
    if char == u"ḉ":
        return u"ç"
    if char == u"Ð":
        return "Dh"
    if char == u"ð":
        return "dh"    
    if char in u"ĎḊḌḎḐḒĐƉƊƋ":
        return "D"
    if char in u"ďḋḍḏḑḓđɖɗƌ":
        return "d"
    if char in u"ÈȄÉÊḚËĒḔḖĔĖẸE̩ȆȨḜĘĚẼḘẺ":
        return "E"
    if char in u"ỀẾỄỆỂ":
        return "Ê"
    if char in u"èȅéêḛëēḕḗĕėẹe̩ȇȩḝęěẽḙẻ":
        return "e"
    if char in u"ềếễệể":
        return "ê"
    if char in u"ḞƑ":
        return "F"
    if char in u"ḟƒ":
        return "f"
    if char in u"ǴḠĞĠĢǦǤƓ":
        return "G"
    if char in u"ǵḡğġģǧǥɠ":
        return "g"
    if char == u"Ĝ":
        return "Gx"
    if char == u"ĝ":
        return "gx"
    if char in u"ḢḤḦȞḨḪH̱ĦǶ":
        return "H"
    if char in u"ḣḥḧȟḩḫ̱ẖħƕ":
        return "h"
    if char == u"Ĥ":
        return "Hx"
    if char == u"ĥ":
        return "hx"
    if char in u"IÌȈÍÎĨḬÏḮĪĬȊĮǏİỊỈƗ":
        return "I"
    if char in u"ıìȉíîĩḭïḯīĭȋįǐiịỉɨ":
        return "i"
    if char in u"ĴJ":
        return "J"
    if char in u"ɟĵ̌ǰ":
        return "j"
    if char in u"ḰǨĶḲḴƘ":
        return "K"
    if char in u"ḱǩķḳḵƙ":
        return "k"
    if char in u"ĹĻĽḶḸḺḼȽŁ":
        return "L"
    if char in u"ĺļľḷḹḻḽƚłɫ":
        return "l"
    if char in u"ḾṀṂ":
        return "M"
    if char in u"ḿṁṃɱ":
        return "m"
    if char in u"ǸŃÑŅŇṄṆṈṊŊƝɲȠ":
        return "N"
    if char in u"ǹńñņňṅṇṉṋŋɲƞ":
        return "n"
    if char in u"ÒÓÔÕṌṎȬÖŌṐṒŎǑȮȰỌǪǬƠỜỚỠỢỞỎƟØǾ":
        return "O"
    if char in u"òóôõṍṏȭöōṑṓŏǒȯȱọǫǭơờớỡợởỏɵøǿ":
        return "o"
    if char in u"ȌŐȪ":
        return "Ö"
    if char in u"ȍőȫ":
        return "ö"
    if char in u"ỒỐỖỘỔȎ":
        return "Ô"
    if char in u"ồốỗộổȏ":
        return "ô"
    if char in u"ṔṖƤ":
        return "P"
    if char in u"ṕṗƥ":
        return "p"
    if char == u"ᵽ":
        return "q"
    if char in u"ȐŔŖŘȒṘṚṜṞ":
        return "R"
    if char in u"ȑŕŗřȓṙṛṝṟɽ":
        return "r"
    if char in u"ŚṤŞȘŠṦṠṢṨ":
        return "S"
    if char in u"śṥşșšṧṡṣṩȿ":
        return "s"
    if char == u"Ŝ":
        return "Sx"
    if char == u"ŝ":
        return "sx"
    if char in u"ŢȚŤṪṬṮṰŦƬƮ":
        return "T"
    if char in u"ţțťṫṭṯṱŧȾƭʈ":
        return "t"
    if char in u"ÙÚŨṸṴÜṲŪṺŬỤŮŲǓṶỦƯỮỰỬ":
        return "U"
    if char in u"ùúũṹṵüṳūṻŭụůųǔṷủưữựửʉ":
        return "u"
    if char in u"ȔŰǛǗǕǙ":
        return "Ü"
    if char in u"ȕűǜǘǖǚ":
        return "ü"
    if char == u"Û":
        return "Ux"
    if char == u"û":
        return "ux"
    if char == u"Ȗ":
        return "Û"
    if char == u"ȗ":
        return "û"
    if char == u"Ừ":
        return "Ù"
    if char == u"ừ":
        return "ù"
    if char == u"Ứ":
        return "Ú"
    if char == u"ứ":
        return "ú"
    if char in u"ṼṾ":
        return "V"
    if char in u"ṽṿ":
        return "v"
    if char in u"ẀẂŴẄẆẈ":
        return "W"
    if char in u"ẁẃŵẅẇẉ":
        return "w"
    if char in u"ẊẌ":
        return "X"
    if char in u"ẋẍ":
        return "x"
    if char in u"ỲÝŶŸỸȲẎỴỶƳ":
        return "Y"
    if char in u"ỳýŷÿỹȳẏỵỷƴ":
        return "y"
    if char in u"ŹẐŻẒŽẔƵȤ":
        return "Z"
    if char in u"źẑżẓžẕƶȥ":
        return "z"
    if char == u"ɀ":
        return "zv"
    
    # Latin: extended Latin alphabet
    if char == u"ɑ":
        return "a"
    if char in u"ÆǼǢ":
        return "AE"
    if char in u"æǽǣ":
        return "ae"
    if char == u"Ð":
        return "Dh"
    if char == u"ð":
        return "dh"
    if char in u"ƎƏƐ":
        return "E"
    if char in u"ǝəɛ":
        return "e"
    if char in u"ƔƢ":
        return "G"
    if char in u"ᵷɣƣᵹ":
        return "g"
    if char == u"Ƅ":
        return "H"
    if char == u"ƅ":
        return "h"
    if char == u"Ƕ":
        return "Wh"
    if char == u"ƕ":
        return "wh"
    if char == u"Ɩ":
        return "I"
    if char == u"ɩ":
        return "i"
    if char == u"Ŋ":
        return "Ng"
    if char == u"ŋ":
        return "ng"
    if char == u"Œ":
        return "OE"
    if char == u"œ":
        return "oe"
    if char == u"Ɔ":
        return "O"
    if char == u"ɔ":
        return "o"
    if char == u"Ȣ":
        return "Ou"
    if char == u"ȣ":
        return "ou"
    if char == u"Ƽ":
        return "Q"
    if char in u"ĸƽ":
        return "q"
    if char == u"ȹ":
        return "qp"
    if char == u"":
        return "r"
    if char == u"ſ":
        return "s"
    if char == u"ß":
        return "ss"
    if char == u"Ʃ":
        return "Sh"
    if char == u"ʃᶋ":
        return "sh"
    if char == u"Ʉ":
        return "U"
    if char == u"ʉ":
        return "u"
    if char == u"Ʌ":
        return "V"
    if char == u"ʌ":
        return "v"
    if char in u"ƜǷ":
        return "W"
    if char in u"ɯƿ":
        return "w"
    if char == u"Ȝ":
        return "Y"
    if char == u"ȝ":
        return "y"
    if char == u"Ĳ":
        return "IJ"
    if char == u"ĳ":
        return "ij"
    if char == u"Ƨ":
        return "Z"
    if char in u"ʮƨ":
        return "z"
    if char == u"Ʒ":
        return "Zh"
    if char == u"ʒ":
        return "zh"
    if char == u"Ǯ":
        return "Dzh"
    if char == u"ǯ":
        return "dzh"
    if char in u"ƸƹʔˀɁɂ":
        return "'"
    if char in u"Þ":
        return "Th"
    if char in u"þ":
        return "th"
    if char in u"Cʗǃ":
        return "!"
    
    #Cyrillic
    if char == u"А":
        return "A"
    if char == u"а":
        return "a"
    if char == u"Б":
        return "B"
    if char == u"б":
        return "b"
    if char == u"В":
        return "V"
    if char == u"в":
        return "v"
    if char == u"Г":
        return "G"
    if char == u"г":
        return "g"
    if char == u"Д":
        return "D"
    if char == u"д":
        return "d"
    if char == u"Е":
        return "E"
    if char == u"е":
        return "e"
    if char == u"Ж":
        return "Zh"
    if char == u"ж":
        return "zh"
    if char == u"З":
        return "Z"
    if char == u"з":
        return "z"
    if char == u"И":
        return "I"
    if char == u"и":
        return "i"
    if char == u"Й":
        return "J"
    if char == u"й":
        return "j"
    if char == u"К":
        return "K"
    if char == u"к":
        return "k"
    if char == u"Л":
        return "L"
    if char == u"л":
        return "l"
    if char == u"М":
        return "M"
    if char == u"м":
        return "m"
    if char == u"Н":
        return "N"
    if char == u"н":
        return "n"
    if char == u"О":
        return "O"
    if char == u"о":
        return "o"
    if char == u"П":
        return "P"
    if char == u"п":
        return "p"
    if char == u"Р":
        return "R"
    if char == u"р":
        return "r"
    if char == u"С":
        return "S"
    if char == u"с":
        return "s"
    if char == u"Т":
        return "T"
    if char == u"т":
        return "t"
    if char == u"У":
        return "U"
    if char == u"у":
        return "u"
    if char == u"Ф":
        return "F"
    if char == u"ф":
        return "f"
    if char == u"Х":
        return "Kh"
    if char == u"х":
        return "kh"
    if char == u"Ц":
        return "C"
    if char == u"ц":
        return "c"
    if char == u"Ч":
        return "Ch"
    if char == u"ч":
        return "ch"
    if char == u"Ш":
        return "Sh"
    if char == u"ш":
        return "sh"
    if char == u"Щ":
        return "Shch"
    if char == u"щ":
        return "shch"
    if char in u"Ьь":
        return "'"
    if char in u"Ъъ":
        return '"'
    if char == u"Ю":
        return "Yu"
    if char == u"ю":
        return "yu"
    if char == u"Я":
        return "Ya"
    if char == u"я":
        return "ya"
    # Additional Cyrillic letters, most occuring in only one or a few languages
    if char == u"Ы":
        return "Y"
    if char == u"ы":
        return "y"
    if char == u"Ё":
        return "Ë"
    if char == u"ё":
        return "ë"
    if char == u"Э":
        return "È"
    if char == u"э":
        return "è"
    if char == u"І":
        return "I"
    if char == u"і":
        return "i"
    if char == u"Ї":
        return "Ji"
    if char == u"ї":
        return "ji"
    if char == u"Є":
        return "Je"
    if char == u"є":
        return "je"
    if char == u"Ґ":
        return "G"
    if char == u"ґ":
        return "g"
    if char == u"Ђ":
        return "Dj"
    if char == u"ђ":
        return "dj"
    if char == u"Ј":
        return "J"
    if char == u"ј":
        return "j"
    if char == u"Љ":
        return "Lj"
    if char == u"љ":
        return "lj"
    if char == u"Њ":
        return "Nj"
    if char == u"њ":
        return "nj"
    if char == u"Ћ":
        return "Cj"
    if char == u"ћ":
        return "cj"
    if char == u"Џ":
        return "Dzh"
    if char == u"џ":
        return "dzh"
    if char == u"Ѕ":
        return "Dz"
    if char == u"ѕ":
        return "dz"
    if char == u"Ѓ":
        return "Gj"
    if char == u"ѓ":
        return "gj"
    if char == u"Ќ":
        return "Kj"
    if char == u"ќ":
        return "kj"
    if char == u"Ғ":
        return "G"
    if char == u"ғ":
        return "g"
    if char == u"Ӣ":
        return "Ii"
    if char == u"ӣ":
        return "ii"
    if char == u"Қ":
        return "Q"
    if char == u"қ":
        return "q"
    if char == u"Ӯ":
        return "U"
    if char == u"ӯ":
        return "u"
    if char == u"Ҳ":
        return "H"
    if char == u"ҳ":
        return "h"
    if char == u"Ҷ":
        return "Dz"
    if char == u"ҷ":
        return "dz"
    if char == u"Ө":
        return "Oe"
    if char == u"ө":
        return "oe"
    if char == u"Ү":
        return "Y"
    if char == u"ү":
        return "y"
    if char == u"Һ":
        return "H"
    if char == u"һ":
        return "h"
    if char == u"Ә":
        return "AE"
    if char == u"ә":
        return "ae"
    if char == u"Җ":
        return "Zhj"
    if char == u"җ":
        return "zhj"
    if char == u"Ң":
        return "Ng"
    if char == u"ң":
        return "ng"
    if char == u"Ұ":
        return "U"
    if char == u"ұ":
        return "u"

    # Hebrew alphabet
    if char in u"אע":
        return "'"
    if char == u"ב":
        return "b"
    if char == u"ג":
        return "g"
    if char == u"ד":
        return "d"
    if char == u"ה":
        return "h"
    if char == u"ו":
        return "v"
    if char == u"ז":
        return "z"
    if char == u"ח":
        return "kh"
    if char == u"ט":
        return "t"
    if char == u"י":
        return "y"
    if char in u"ךכ":
        return "k"
    if char == u"ל":
        return "l"
    if char in u"םמ":
        return "m"
    if char in u"ןנ":
        return "n"
    if char == u"ס":
        return "s"
    if char in u"ףפ":
        return "ph"
    if char in u"ץצ":
        return "ts"
    if char == u"ק":
        return "q"
    if char == u"ר":
        return "r"
    if char == u"ש":
        return "sh"
    if char == u"ת":
        return "th"
    
    # Arab alphabet
    if char in u"اﺍﺎ":
        return "a"
    if char in u"بﺏﺐﺒﺑ":
        return "b"
    if char in u"تﺕﺖﺘﺗ":
        return "t"
    if char in u"ثﺙﺚﺜﺛ":
        return "th"
    if char in u"جﺝﺞﺠﺟ":
        return "g"
    if char in u"حﺡﺢﺤﺣ":
        return "h"
    if char in u"خﺥﺦﺨﺧ":
        return "kh"
    if char in u"دﺩﺪ":
        return "d"
    if char in u"ذﺫﺬ":
        return "dh"
    if char in u"رﺭﺮ":
        return "r"
    if char in u"زﺯﺰ":
        return "z"
    if char in u"سﺱﺲﺴﺳ":
        return "s"
    if char in u"شﺵﺶﺸﺷ":
        return "sh"
    if char in u"صﺹﺺﺼﺻ":
        return "s"
    if char in u"ضﺽﺾﻀﺿ":
        return "d"
    if char in u"طﻁﻂﻄﻃ":
        return "t"
    if char in u"ظﻅﻆﻈﻇ":
        return "z"
    if char in u"عﻉﻊﻌﻋ":
        return "'"
    if char in u"غﻍﻎﻐﻏ":
        return "gh"
    if char in u"فﻑﻒﻔﻓ":
        return "f"
    if char in u"قﻕﻖﻘﻗ":
        return "q"
    if char in u"كﻙﻚﻜﻛ":
        return "k"
    if char in u"لﻝﻞﻠﻟ":
        return "l"
    if char in u"مﻡﻢﻤﻣ":
        return "m"
    if char in u"نﻥﻦﻨﻧ":
        return "n"
    if char in u"هﻩﻪﻬﻫ":
        return "h"
    if char in u"وﻭﻮ":
        return "w"
    if char in u"يﻱﻲﻴﻳ":
        return "y"
    # Arabic - additional letters, modified letters and ligatures
    if char == u"ﺀ":
        return "'"
    if char in u"آﺁﺂ":
        return "'a"
    if char in u"ةﺓﺔ":
        return "th"
    if char in u"ىﻯﻰ":
        return "á"
    if char in u"یﯼﯽﯿﯾ":
        return "y"
    # Arabic - ligatures
    if char in u"ﻻﻼ":
        return "la"
    if char == u"ﷲ":
        return "llah"
    if char in u"إأ":
        return "a'"
    if char == u"ؤ":
        return "w'"
    if char == u"ئ":
        return "y'"
    if char == u"◌":
        return "-" # consonant doubling, no good transliteration for it
    if char in u"◌◌":
        return "" # indicates absence of vowels
    # Arabic vowels
    if char == u"◌":
        return "a"
    if char == u"◌":
        return "u"
    if char == u"◌":
        return "i"
    if char == u"◌":
        return "a"
    if char == u"◌":
        return "ay"
    if char == u"◌":
        return "ay"
    if char == u"◌":
        return "u"
    if char == u"◌":
        return "iy"
    # Arab numerals
    if char in u"٠۰":
        return "0"
    if char in u"١۱":
        return "1"
    if char in u"٢۲":
        return "2"
    if char in u"٣۳":
        return "3"
    if char in u"٤۴":
        return "4"
    if char in u"٥۵":
        return "5"
    if char in u"٦۶":
        return "6"
    if char in u"٧۷":
        return "7"
    if char in u"٨۸":
        return "8"
    if char in u"٩۹":
        return "9"
    # Perso-Arabic
    if char in u"پﭙﭙپ":
        return "p"
    if char in u"چچچچ":
        return "ch"
    if char in u"ژژ":
        return "zh"
    if char in u"گﮔﮕﮓ":
        return "g"
    
    return default
