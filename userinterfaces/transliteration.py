# -*- coding: utf-8 -*-
def trans(char, default = '?'):
    # Give a transliteration for char, or default if none is known
    # Accented etc. Latin characters
    if char in u"ÀÁÂẦẤẪẨẬÃĀĂẰẮẴẶẲȦǠẠḀȂĄǍẢ":
        return "A"
    if char in u"ȀǞ":
        return "Ä"
    if char == u"Ǻ":
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

    # Greek
    if char == u"Α":
        return "A"
    if char == u"α":
        return "a"
    if char == u"Β":
        return "B"
    if char == u"β":
        return "b"
    if char == u"Γ":
        return "G"
    if char == u"γ":
        return "g"
    if char == u"Δ":
        return "D"
    if char == u"δ":
        return "d"
    if char == u"Ε":
        return "E"
    if char == u"ε":
        return "e"
    if char == u"Ζ":
        return "Z"
    if char == u"ζ":
        return "z"
    if char == u"Η":
        return "I"
    if char == u"η":
        return "i"
    if char == u"Θ":
        return "Th"
    if char == u"θ":
        return "th"
    if char == u"Ι":
        return "I"
    if char == u"ι":
        return "i"
    if char == u"Κ":
        return "K"
    if char == u"κ":
        return "k"
    if char == u"Λ":
        return "L"
    if char == u"λ":
        return "l"
    if char == u"Μ":
        return "M"
    if char == u"μ":
        return "m"
    if char == u"Ν":
        return "N"
    if char == u"ν":
        return "n"
    if char == u"Ξ":
        return "X"
    if char == u"ξ":
        return "x"
    if char == u"Ο":
        return "O"
    if char == u"ο":
        return "o"
    if char == u"Π":
        return "P"
    if char == u"π":
        return "p"
    if char == u"Ρ":
        return "R"
    if char == u"ρ":
        return "r"
    if char == u"Σ":
        return "S"
    if char in u"σς":
        return "s"
    if char == u"Τ":
        return "T"
    if char == u"τ":
        return "t"
    if char == u"Υ":
        return "Y"
    if char == u"υ":
        return "y"
    if char == u"Φ":
        return "F"
    if char == u"φ":
        return "f"
    if char == u"Ψ":
        return "Ps"
    if char == u"ψ":
        return "ps"
    if char == u"Ω":
        return "O"
    if char == u"ω":
        return "o"
    if char == u"ϗ":
        return "&"
    if char == u"Ϛ":
        return "St"
    if char == u"ϛ":
        return "st"
    if char in u"ϘϞ":
        return "Q"
    if char in u"ϙϟ":
        return "q"
    if char == u"Ϻ":
        return "S"
    if char == u"ϻ":
        return "s"
    if char == u"Ϡ":
        return "Ss"
    if char == u"ϡ":
        return "ss"
    if char == u"Ϸ":
        return "Sh"
    if char == u"ϸ":
        return "sh"

    # Japanese (katakana and hiragana)
    if char in u"アあ":
        return "a"
    if char in u"イい":
        return "i"
    if char in u"ウう":
        return "u"
    if char in u"エえ":
        return "e"
    if char in u"オお":
        return "o"
    if char in u"ャや":
        return "ya"
    if char in u"ュゆ":
        return "yu"
    if char in u"ョよ":
        return "yo"
    if char in u"カか":
        return "ka"
    if char in u"キき":
        return "ki"
    if char in u"クく":
        return "ku"
    if char in u"ケけ":
        return "ke"
    if char in u"コこ":
        return "ko"
    if char in u"サさ":
        return "sa"
    if char in u"シし":
        return "shi"
    if char in u"スす":
        return "su"
    if char in u"セせ":
        return "se"
    if char in u"ソそ":
        return "so"
    if char in u"タた":
        return "ta"
    if char in u"チち":
        return "chi"
    if char in u"ツつ":
        return "tsu"
    if char in u"テて":
        return "te"
    if char in u"トと":
        return "to"
    if char in u"ナな":
        return "na"
    if char in u"ニに":
        return "ni"
    if char in u"ヌぬ":
        return "nu"
    if char in u"ネね":
        return "ne"
    if char in u"ノの":
        return "no"
    if char in u"ハは":
        return "ha"
    if char in u"ヒひ":
        return "hi"
    if char in u"フふ":
        return "fu"
    if char in u"ヘへ":
        return "he"
    if char in u"ホほ":
        return "ho"
    if char in u"マま":
        return "ma"
    if char in u"ミみ":
        return "mi"
    if char in u"ムむ":
        return "mu"
    if char in u"メめ":
        return "me"
    if char in u"モも":
        return "mo"
    if char in u"ラら":
        return "ra"
    if char in u"リり":
        return "ri"
    if char in u"ルる":
        return "ru"
    if char in u"レれ":
        return "re"
    if char in u"ロろ":
        return "ro"
    if char in u"ワわ":
        return "wa"
    if char in u"ヰゐ":
        return "wi"
    if char in u"ヱゑ":
        return "we"
    if char in u"ヲを":
        return "wo"
    if char in u"ンん":
        return "n"
    if char in u"ガが":
        return "ga"
    if char in u"ギぎ":
        return "gi"
    if char in u"グぐ":
        return "gu"
    if char in u"ゲげ":
        return "ge"
    if char in u"ゴご":
        return "go"
    if char in u"ザざ":
        return "za"
    if char in u"ジじ":
        return "ji"
    if char in u"ズず":
        return "zu"
    if char in u"ゼぜ":
        return "ze"
    if char in u"ゾぞ":
        return "zo"
    if char in u"ダだ":
        return "da"
    if char in u"ヂぢ":
        return "dji"
    if char in u"ヅづ":
        return "dzu"
    if char in u"デで":
        return "de"
    if char in u"ドど":
        return "do"
    if char in u"ドば":
        return "ba"
    if char in u"ビび":
        return "bi"
    if char in u"ブぶ":
        return "bu"
    if char in u"ベべ":
        return "be"
    if char in u"ボぼ":
        return "bo"
    if char in u"パぱ":
        return "pa"
    if char in u"ピぴ":
        return "pi"
    if char in u"プぷ":
        return "pu"
    if char in u"ペぺ":
        return "pe"
    if char in u"ポぽ":
        return "po"
    if char == u"ヷ":
        return "va"
    if char == u"ヸ":
        return "vi"
    if char == u"ヹ":
        return "ve"
    if char == u"ヺ":
        return "vo"

    # Georgian
    if char == u"ა":
        return "a"
    if char == u"ბ":
        return "b"
    if char == u"გ":
        return "g"
    if char == u"დ":
        return "d"
    if char == u"ე":
        return "e"
    if char == u"ვ":
        return "v"
    if char == u"ზ":
        return "z"
    if char == u"თ":#
        return "th"
    if char == u"ი":
        return "i"
    if char == u"კ":#
        return "k"
    if char == u"ლ":
        return "l"
    if char == u"მ":
        return "m"
    if char == u"ნ":
        return "n"
    if char == u"ო":
        return "o"
    if char == u"პ":#
        return "p"
    if char == u"ჟ":#
        return "zh"
    if char == u"რ":
        return "r"
    if char == u"ს":
        return "s"
    if char == u"ტ":#
        return "t"
    if char == u"უ":
        return "u"
    if char == u"ფ":#
        return "ph"
    if char == u"ქ":#
        return "q"
    if char == u"ღ":#
        return "gh"
    if char == u"ყ":#
        return "q'"
    if char == u"შ":
        return "sh"
    if char == u"ჩ":
        return "ch"
    if char == u"ც":
        return "ts"
    if char == u"ძ":
        return "dz"
    if char == u"წ":#
        return "ts'"
    if char == u"ჭ":#
        return "ch'"
    if char == u"ხ":
        return "kh"
    if char == u"ჯ":#
        return "j"
    if char == u"ჰ":
        return "h"

    # Devanagari
    if char in u"पप":
        return "p"
    if char in u"अ":
        return "a"
    if char in u"आा":
        return "aa"
    if char == u"प":
        return "pa"
    if char in u"इि":
        return "i"
    if char in u"ईी":
        return "ii"
    if char in u"उु":
        return "u"
    if char in u"ऊू":
        return "uu"
    if char in u"एे":
        return "e"
    if char in u"ऐै":
        return "ai"
    if char in u"ओो":
        return "o"
    if char in u"औौ":
        return "au"
    if char in u"ऋृर":
        return "r"
    if char in u"ॠॄ":
        return "rr"
    if char in u"ऌॢल":
        return "l"
    if char in u"ॡॣ":
        return "ll"
    if char == u"क":
        return "k"
    if char == u"ख":
        return "kh"
    if char == u"ग":
        return "g"
    if char == u"घ":
        return "gh"
    if char == u"ङ":
        return "ng"
    if char == u"च":
        return "c"
    if char == u"छ":
        return "ch"
    if char == u"ज":
        return "j"
    if char == u"झ":
        return "jh"
    if char == u"ञ":
        return "ñ"
    if char in u"टत":
        return "t"
    if char in u"ठथ":
        return "th"
    if char in u"डद":
        return "d"
    if char in u"ढध":
        return "dh"
    if char in u"णन":
        return "n"
    if char == u"फ":
        return "ph"
    if char == u"ब":
        return "b"
    if char == u"भ":
        return "bh"
    if char == u"म":
        return "m"
    if char == u"य":
        return "y"
    if char == u"व":
        return "v"
    if char == u"श":
        return "sh"
    if char in u"षस":
        return "s"
    if char == u"ह":
        return "h"
    if char == u"क":
        return "x"
    if char == u"त":
        return "tr"
    if char == u"ज":
        return "gj"
    if char == u"क़":
        return "q"
    if char == u"फ":
        return "f"
    if char == u"ख":
        return "hh"
    if char == u"H":
        return "gh"
    if char == u"ज":
        return "z"
    if char in u"डढ":
        return "r"
    # Devanagari ligatures (possibly incomplete and/or incorrect)
    if char == u"ख्":
        return "khn"
    if char == u"त":
        return "tn"
    if char == u"द्":
        return "dn"
    if char == u"श":
        return "cn"
    if char == u"ह्":
        return "fn"
    if char in u"अँ":
        return "m"
    if char in u"॒॑":
        return ""
    if char == u"०":
        return "0"
    if char == u"१":
        return "1"
    if char == u"२":
        return "2"
    if char == u"३":
        return "3"
    if char == u"४":
        return "4"
    if char == u"५":
        return "5"
    if char == u"६":
        return "6"
    if char == u"७":
        return "7"
    if char == u"८":
        return "8"
    if char == u"९":
        return "9"

    
    return default
