# -*- coding: utf-8 -*-
def trans(char, default = '?'):
    # Give a transliteration for char, or default if none is known
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
    if char in u"ĆĈĊÇḈČƇ":
        return "C"
    if char in u"ćĉċçḉčƈȼ":
        return "c"
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
    if char in u"ǴĜḠĞĠĢǦǤƓ":
        return "G"
    if char in u"ǵĝḡğġģǧǥɠ":
        return "g"
    if char in u"ĤḢḤḦȞḨḪH̱ĦǶ":
        return "H"
    if char in u"ĥḣḥḧȟḩḫ̱ẖħƕ":
        return "h"
    #Iı Ìì Ȉȉ Íí Îî Ĩĩ Ḭḭ Ïï Ḯḯ Īī Ĭĭ Ȋȋ Įį Ǐǐ İi Ịị Ỉỉ Ɨɨ ɟ Ĵĵ J̌ǰ Ḱḱ Ǩǩ Ķķ Ḳḳ Ḵḵ Ƙƙ Ĺĺ Ļļ Ľľ Ḷḷ Ḹḹ Ḻḻ Ḽḽ Ƚƚ Łł ɫ Ḿḿ M̃m̃ Ṁṁ Ṃṃ Ǹǹ Ńń N̈n̈ Ññ Ņņ Ňň Ṅṅ Ṇṇ Ṉṉ Ṋṋ Ŋŋ Ɲɲ Ƞƞ Òò Ȍȍ Óó Őő Ôô Ồồ Ốố Ỗỗ Ộộ Ổổ Õõ Ṍṍ Ṏṏ Ȭȭ Öö Ȫȫ Ōō Ṑṑ Ṓṓ Ŏŏ Ȏȏ Ǒǒ Ȯȯ Ȱȱ Ọọ O̩o̩ Ǫǫ Ǭǭ Ơơ Ờờ Ớớ Ỡỡ Ợợ Ởở Ỏỏ Ɵɵ Øø Ǿǿ Ṕṕ Ṗṗ P̃p̃ Ƥƥ ᵽ Ȑȑ Ŕŕ Ŗŗ Řř Ȓȓ Ṙṙ Ṛṛ Ṝṝ Ṟṟ ɽ Śś Ṥṥ Ŝŝ Şş Șș Šš Ṧṧ Ṡṡ Ṣṣ Ṩṩ S̩s̩ ȿ T̈ẗ Ţţ Țț Ťť Ṫṫ Ṭṭ Ṯṯ Ṱṱ Ŧŧ Ⱦ Ƭƭ Ʈʈ Ùù Ȕȕ Úú Űű Ûû Ũũ Ṹṹ Ṵṵ Üü Ṳṳ Ǜǜ Ǘǘ Ǖǖ Ǚǚ Ūū Ṻṻ Ŭŭ Ụụ Ůů Ȗȗ Ųų Ǔǔ Ṷṷ Ủủ Ưư Ừừ Ứứ Ữữ Ựự Ửử ʉ Ṽṽ Ṿṿ Ẁẁ Ẃẃ Ŵŵ Ẅẅ Ẇẇ Ẉẉ W̊ẘ Ẋẋ Ẍẍ Ỳỳ Ýý Ŷŷ Ÿÿ Ỹỹ Ȳȳ Ẏẏ Y̊ẙ Ỵỵ Ỷỷ Ƴƴ Źź Ẑẑ Żż Ẓẓ Žž Ẕẕ Ƶƶ Ȥȥ ɀ

    return default
