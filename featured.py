#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script understands various command-line arguments:

* -interactive       : ask before changing page

* -nocache           : doesn't include /cache/featured file to remember if the
                       article already was verified.

* -fromlang:xx[,yy[,...]]] : xx,.. are the languages to be verified. Another
                             possible with range the languages -fromlang:ar--fi

* -fromall           : to verify all languages.

* -after:zzzz        : process pages after and including page zzzz

* -top               : using -top if you want moving {{Link FA|lang}} to top of interwiki.
                       DEFAULT: placing {{Link FA|lang}} right next to corresponding interwiki.

usage: featured.py [-interactive] [-nocache] [-top] [-after:zzzz] [-fromlang:xx,yy,zz|-fromall]

"""
__version__ = '$Id$'

#
# (C) Maxim Razin, 2005
# (C) Leonardo Gregianin, 2006-2007
#
# Distributed under the terms of the MIT license.
#

import sys, re, pickle, os.path
import wikipedia, catlib, config

def CAT(site,name):
    cat=catlib.Category(site, name)
    return cat.articles()

def BACK(site,name):
    p=wikipedia.Page(site, name)
    return [page for page in p.getReferences(follow_redirects = False)]

def LINKS(site,name, ignore=[]):
    p=wikipedia.Page(site, name)
    links=p.linkedPages()
    for n in links[:]:
        t=n.titleWithoutNamespace()
        if t[0] in u"/#" or t in ignore:
            links.remove(n)
    links.sort()
    return links

msg = {
    'als': u'Bötli: [[%s:%s]] isch en bsunders glungener Artikel',
    'ar': u'بوت: وصلة مقالة مختارة ل [[%s:%s]]',
    'bat-smg': u'robots: Pavīzdėnė straipsnė nūruoda [[%s:%s]]',
    'bs': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'cs': u'Bot: Nejlepší článek: [[%s:%s]]',
    'de': u'Bot: [[%s:%s]] ist ein ausgezeichneter Artikel',
    'en': u'Bot: [[%s:%s]] is a featured article',
    'eo': u'roboto: [[%s:%s]] estas artikolo elstara',
    'es': u'Bot: Enlace a artículo destacado para: [[%s:%s]]',
    'fa': u' ربات: [[%s:%s]] یک مقاله برگزیده‌است',
    'fi': u'Bot: Suositeltu artikkeli -tähti: [[%s:%s]]',
    'fr': u'Bot: Lien AdQ pour [[%s:%s]]',
    'he': u'בוט: קישור לערך מומלץ עבור [[%s:%s]]',
    'hr': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'it': u'Bot: collegamento articolo in vetrina [[%s:%s]]',
    'ja': u'ロボットによる: 秀逸な項目へのリンク [[%s:%s]]',
    'ka': u'ბოტი: რჩეული სტატიის ბმული გვერდისათვის [[%s:%s]]',
    'ko': u'로봇: 알찬 글 [[%s:%s]] 를 가리키는 링크',#로봇이：?
    'ksh': u'bot: [[%s:%s]] ess_enen ußjezëijshneten Atikkel',
    'lb': u'Bot: Exzellenten Arikel Link op [[%s:%s]]',
    'lt': u'Bot: Pavyzdinis straipsnis [[%s:%s]]',
    'nl': u'Bot: Etalage-artikel link voor [[%s:%s]]',
    'no': u'bot: [[%s:%s]] er en utmerka artikkel',
    'nn': u'bot: [[%s:%s]] er ein god artikkel',
    'mk': u'Бот: Интервики за избрани статии за [[%s:%s]]',
    'pl': u'Bot: Link do artykułu wyróżnionego [[%s:%s]]',
    'pt': u'Bot: Ligando artigos destacados para [[%s:%s]]',
    'ru': u'Робот: робот: избранная статья [[%s:%s]]',
    'sr': u'Bot: Међувики за изабране чланке за [[%s:%s]]',
    'sv': u'Bot: [[%s:%s]] är en utmärkt artikel',
    'th': u'บอต: ลิงก์บทความคัดสรร [[%s:%s]]',
    'tr': u'Bot değişikliği: [[%s:%s]] madde bağlantısı eklendi',
    'vo': u'Bot: Yüm yegeda gudik tefü [[%s:%s]]',
    'zh': u'機器人: 連結特色條目 [[%s:%s]]',
}

template = {
    'af': ['Link FA'],
    'als': ['LinkFA', 'Link FA'],
    'am': ['Link FA'],
    'an': ['Destacato', 'Destacau', 'Link FA'],
    'ang': ['Link FA'],
    'ar': [u'وصلة مقالة مختارة', 'Link FA'],
    'ast': ['Enllaz AD', 'Link FA'],
    'ay': ['Link FA'],
    'az': ['Link FM', 'Link FA'],
    'bar': ['Link FA'],
    'bat-smg': ['Link FA'],
    'be': ['Link FA'],
    'be-x-old': ['Link FA'],
    'bg': ['Link FA'],
    'bn': ['Link FA'],
    'bo': ['Link FA'],
    'bpy': ['Link FA'],
    'br': ['Liamm PuB', 'Link FA', 'Lien AdQ'],
    'bs': ['Link FA'],
    'ca': [u'Enllaç AD', 'Destacat', 'Link FA'],
    'cdo': ['Link FA'],
    'ceb': ['Link FA'],
    'co': ['Link FA'],
    'crh': ['Link FA'],
    'cs': ['Link FA'],
    'cu': ['Link FA'],
    'cv': ['Link FA'],
    'cy': ['Cyswllt erthygl ddethol', 'Dolen ED', 'Link FA'],
    'da': ['Link FA'],
    'de': ['Link FA'],
    'dsb': ['Link FA'],
    'dv': ['Link FA'],
    'el': ['Link FA'],
    'en': ['Link FA'],
    'eo': ['LigoElstara', 'Link FA'],
    'es': ['Destacado', 'Link FA'],
    'et': ['Link FA'],
    'eu': ['NA lotura', 'Link FA'],
    'fa': ['Link FA'],
    'fi': ['Link FA'],
    'fo': ['Link FA'],
    'fr': ['Lien AdQ', 'Link FA'],
    'frp': ['Link FA'],
    'ga': ['Nasc AR', 'Link FA'],
    'gan': ['Link FA'],
    'gd': ['Link FA'],
    'gl': ['Link FA'],
    'gn': ['Link FA'],
    'gu': ['Link FA'],
    'hak': ['Link FA'],
    'he': ['Link FA'],
    'hi': ['Link FA', 'Lien AdQ'],
    'hr': ['Link FA'],
    'hsb': ['Link FA'],
    'hu': ['Link FA'],
    'hy': ['Link FA'],
    'ia': ['Link FA'],
    'id': ['Link FA'],
    'ilo': ['Link FA'],
    'io': ['Link FA'],
    'is': [u'Tengill ÚG', 'Link FA'],
    'it': ['Link AdQ', 'Link FA'],
    'ja': ['Link FA'],
    'jbo': ['Link FA'],
    'jv': ['Link FA'],
    'ka': ['Link FA'],
    'kaa': ['Link FA'],
    'kab': ['Link FA'],
    'kk': ['Link FA'],
    'kl': ['Link FA'],
    'km': ['Link FA'],
    'kn': ['Link FA'],
    'ko': ['Link FA'],
    'ksh': ['Link FA'],
    'ku': ['Link FA'],
    'kw': ['Link FA'],
    'la': ['Link FA'],
    'lad': ['Link FA'],
    'lb': ['Link FA'],
    'li': ['Link FA'],
    'lo': ['Link FA'],
    'lt': ['Link FA'],
    'lv': ['Link FA'],
    'mi': ['Link FA'],
    'mk': ['Link FA'],
    'ml': ['Link FA'],
    'mn': ['Link FA'],
    'mr': ['Link FA'],
    'ms': ['Link FA'],
    'mt': ['Link FA'],
    'nah': ['Link FA'],
    'new': ['Link FA'],
    'nl': ['Link FA'],
    'nn': ['Link FA'],
    'no': ['Link UA', 'Link FA'],
    'oc': ['Ligam AdQ', 'Lien AdQ', 'Link FA'],
    'os': ['Link FA'],
    'pam': ['Link FA'],
    'pap': ['Link FA'],
    'pih': ['Link FA'],
    'pl': ['Link FA'],
    'ps': ['Link FA'],
    'pt': ['Link FA'],
    'qu': ['Link FA'],
    'rmy': ['Link FA'],
    'ro': [u'Legătură AF', 'Link FA'],
    'ru': ['Link FA'],
    'scn': ['Link FA'],
    'sco': ['Link FA'],
    'sd': ['Link FA'],
    'se': ['Link FA'],
    'sh': ['Link FA'],
    'si': ['Link FA'],
    'simple': ['Link FA'],
    'sk': ['Link FA'],
    'sl': ['Link FA'],
    'sq': ['Link FA'],
    'sr': ['Link FA'],
    'su': ['Link FA'],
    'sv': ['UA', 'Link UA', 'Link FA'],
    'sw': ['Link FA'],
    'szl': ['Link FA'],
    'ta': ['Link FA'],
    'te': ['Link FA'],
    'tg': ['Link FA'],
    'th': ['Link FA'],
    'tl': ['Link FA'],
    'tpi': ['Link FA'],
    'tr': ['Link SM', 'Link FA'],
    'ug': ['Link FA'],
    'uk': ['Link FA'],
    'ur': ['Link FA'],
    'uz': ['Link FA'],
    'vec': ['Link FA'],
    'vi': [u'Liên kết chọn lọc', 'Link FA'],
    'vo': [u'Yüm YG', 'Link FA'],
    'wa': ['Link FA'],
    'war': ['Link FA'],
    'wuu': ['Link FA'],
    'yi': ['Link FA', u'רא'],
    'yo': ['Link FA'],
    'zh': ['Link FA'],
    'zh-classical': ['Link FA'],
    'zh-min-nan': ['Link FA'],
    'zh-yue': ['Link FA'],
    'zu': ['Link FA'],
}

featured_name = {
    'af': (BACK, u"Sjabloon:Voorbladster"),
    'als': (CAT, u"Kategorie:Wikipedia:Bsunders glungener Artikel"),
    'am': (CAT, u"Category:Wikipedia:Featured article"),
    'an': (CAT, u"Categoría:Articlos destacatos"),
    'ar': (CAT, u"تصنيف:مقالات مختارة"),
    'ast': (CAT, u"Categoría:Uiquipedia:Artículos destacaos"),
    'az': (BACK, u"Şablon:Seçkin məqalə"),
    'bar': (CAT, u"Kategorie:Berig"),
    'bat-smg': (CAT, u"Kategorija:Vikipedėjės pavīzdėnē straipsnē"),
    'be-x-old': (CAT, u"Катэгорыя:Вікіпэдыя:Выбраныя артыкулы"),
    'bg': (CAT, u"Категория:Избрани статии"),
    'bn': (BACK, u"Template:নির্বাচিত নিবন্ধ"),
    'br': (CAT, u"Rummad:Pennadoù eus an dibab"),
    'bs': (CAT, u"Kategorija:Odabrani članci"),
    'ca': (CAT, u"Categoria:Viquipèdia:Articles de qualitat"),
    'ceb': (CAT, u"Category:Mga napiling artikulo"),
    'cs': (CAT, u"Kategorie:Nejlepší články"),
   #'cy': (CAT, u"Categori:Erthyglau dethol"),
    'da': (CAT, u"Kategori:Fremragende artikler"),
    'de': (CAT, u"Kategorie:Wikipedia:Exzellent"),
    'dsb': (CAT, u"Kategorija:Ekscelentny"),
    'dv': (BACK, u"Template:Featured article"),
   #'dv': (CAT, u"Category:Featured Articles"),
    'el': (BACK, u"Πρότυπο:Αξιόλογο άρθρο"),
    'eo': (CAT, u"Kategorio:Elstaraj artikoloj"),
    'en': (CAT, u"Category:Featured articles"),
    'es': (CAT, u"Categoría:Wikipedia:Artículos destacados"),
    'et': (CAT, u"Kategooria:Eeskujulikud artiklid"),
    'eu': (CAT, u"Kategoria:Nabarmendutako artikuluak"),
    'fa': (BACK, u"الگو:نوشتار برگزیده"),
    'fi': (CAT, u"Luokka:Suositellut sivut"),
    'fo': (CAT, u"Bólkur:Mánaðargrein"),
    'fr': (CAT, u"Catégorie:Article de qualité"),
    'he': (CAT, u"קטגוריה:ערכים מומלצים"),
    'hi': (BACK, u"Template:निर्वाचित लेख"),
    'hr': (CAT, u"Kategorija:Izabrani članci"),
    'hsb': (CAT, u"Kategorija:Ekscelentny"),
    'hu': (CAT, u"Kategória:Kiemelt cikkek"),
    'hy': (BACK, u"Կաղապար:Ընտրված հոդված"),
    'ia': (CAT, u"Categoria:Articulos eminente"),
    'id': (BACK, u"Templat:Featured article"),
   #'id': (CAT, u"Kategori:Artikel bagus utama"),
    'is': (CAT, u"Flokkur:Wikipedia:Úrvalsgreinar"),
    'it': (CAT, u"Categoria:Voci in vetrina"),
    'ja': (BACK, u"Template:Featured article"),
    'ka': (CAT, u"კატეგორია:რჩეული სტატიები"),
    'km': (BACK, u"ទំព័រគំរូ:អត្ថបទពិសេស"),
    'kn': (BACK, u"ಟೆಂಪ್ಲೇಟು:ವಿಶೇಷ ಲೇಖನ"),
    'ko': (BACK, u"틀:알찬 글 딱지"),
    'ksh': (CAT, u"Saachjrupp:Exzälenter Aatikkel"),
    'la': (CAT, u"Categoria:Paginae mensis"),
    'lmo': (CAT, u"Categoria:Articol ben faa"),
    'lo': (CAT, u"ໝວດ:ບົດຄວາມດີເດັ່ນ"),
    'lt': (CAT, u"Kategorija:Vikipedijos pavyzdiniai straipsniai"),
    'lv': (CAT, u"Kategorija:Vērtīgi raksti"),
   #'lv': (CAT, u"Kategorija:Nedēļas raksti"),
    'mk': (CAT, u"Категорија:Избрани статии"),
    'ml': (BACK, u"Template:Featured"),
    'mr': (CAT, u"वर्ग:मुखपृष्ठ सदर लेख"),
    'ms': (BACK, u"Templat:Rencana pilihan"),
    'nah': (BACK, u"Plantilla:Featured article"),
    'nds-nl': (BACK, u"Sjabloon:Etelazie"),
    'nl': (CAT, u"Categorie:Wikipedia:Etalage-artikelen"),
    'nn': (BACK, u"Mal:God artikkel"),
    'no': (CAT, u"Kategori:Utmerkede artikler"),
    'oc': (CAT, u"Categoria:Article de qualitat"),
    'pl': (CAT, u"Kategoria:Artykuły na medal"),
    'pt': (CAT, u"Categoria:!Artigos destacados"),
    'ro': (CAT, u"Categorie:Articole de calitate"),
    'ru': (CAT, u"Категория:Википедия:Избранные статьи"),
    'sco': (CAT, u"Category:Featurt"),
    'sh': (CAT, u"Category:Izabrani članci"),
    'simple': (CAT, u"Category:Very good articles"),
    'sk': (BACK, u"Šablóna:Perfektný článok"),
    'sl': (CAT, u"Kategorija:Vsi izbrani članki"),
    'sq': (BACK, u"Stampa:Artikulli perfekt"),
    'sr': (CAT, u"Категорија:Изабрани"),
    'sv': (CAT, u"Kategori:Wikipedia:Utmärkta artiklar"),
    'ta': (CAT, u"பகுப்பு:சிறப்புக் கட்டுரைகள்"),
    'te': (CAT, u"వర్గం:విశేషవ్యాసాలు"),
    'th': (BACK, u"แม่แบบ:บทความคัดสรร"),
    'tl': (BACK, u"Template:Napiling artikulo"),
    'tr': (BACK, u"Şablon:Seçkin madde"),
   #'tt': (CAT, u"Törkem:Şäp mäqälä"),
    'uk': (CAT, u"Категорія:Вибрані статті"),
    'ur': (CAT, u"زمرہ:منتخب مقالے"),
    'uz': (CAT, u"Kategoriya:Vikipediya:Tanlangan maqolalar"),
    'vi': (CAT, u"Thể loại:Bài viết chọn lọc"),
    'vo': (CAT, u"Klad:Yegeds gudik"),
   #'wa': (CAT, u"Categoreye:Raspepyî årtike"),
    'yi': (CAT, u"קאַטעגאָריע:רעקאמענדירטע ארטיקלען"),
    'yo': (BACK, u"Template:Ayoka pataki"),
    'zh': (CAT, u"Category:特色条目"),
    'zh-classical': (CAT, u"Category:絕妙好文"),
    'zh-yue': (BACK, u"Template:正文"),
}
"""Templates:
    'af': (BACK, u"Sjabloon:Voorbladster"),
    'als': (BACK, u"Vorlage:Besonders gelungener Artikel"),
    'an': (BACK, u"Plantilla:Articlo destacato"),
    'ast': (BACK, u"Plantía:Destacaos"),
    'ar': (BACK, u"قالب:مقالة مختارة"),
    'az': (BACK, u"Şablon:Seçkin məqalə"),
    'bar': (BACK, u"Vorlage:Berig"),
    'bat-smg': (BACK, u"Šabluons:Featured"),
   #'be': (BACK, u"Шаблон:Выбраны артыкул"),
    'be-x-old': (BACK, u"Шаблён:Выбраны артыкул"),
    'bg': (BACK, u"Шаблон:Избрана статия"),
    'bn': (BACK, u"Template:নির্বাচিত নিবন্ধ"),
    'br': (BACK, u"Patrom:Steredenn pennad eus an dibab"),
   #'br': (BACK, u"Patrom:Pennad eus an dibab"),
    'bs': (BACK, u"Šablon:Wiki članak"),
    'ca': (BACK, u"Plantilla:Article de qualitat"),
   #'ca': (BACK, u"Plantilla:100+AdQ"),
    'ceb': (BACK, u"Template:Napiling artikulo"),
    'cs': (BACK, u"Šablona:Nejlepší článek"),
   #'cy': (BACK, u"Nodyn:Erthygl ddethol"),
    'da': (BACK, u"Skabelon:Fremragende"),
    'de': (BACK, u"Vorlage:Exzellent"),
    'dsb': (BACK, u"Pśedłoga:Ekscelentny"),
    'dv': (BACK, u"Template:Featured article"),
    'el': (BACK, u"Πρότυπο:Αξιόλογο άρθρο"),
    'eo': (BACK, u"Ŝablono:Elstara"),
    'en': (BACK, u"Template:Featured article"),
    'es': (BACK, u"Plantilla:Artículo destacado"),
    'et': (BACK, u"Mall:Eeskujulik artikkel"),
    'eu': (BACK, u"Txantiloi:Nabarmendutako artikulua"),
    'fa': (BACK, u"الگو:نوشتار برگزیده"),
    'fi': (BACK, u"Malline:Suositeltu"),
    'fo': (BACK, u"Fyrimynd:Mánaðargrein"),
    'fr': (BACK, u"Modèle:Article de qualité"),
    'he': (BACK, u"תבנית:ערך מומלץ"),
    'hi': (BACK, u"Template:निर्वाचित लेख"),
    'hr': (BACK, u"Predložak:Izdvojeni članak"),
    'hsb': (BACK, u"Předłoha:Ekscelentny"),
    'hu': (BACK, u"Sablon:Kiemelt"),
    'hy': (BACK, u"Կաղապար:Ընտրված հոդված"),
    'ia': (BACK, u"Patrono:Eminente"),
    'id': (BACK, u"Templat:Featured article"),
   #'id': (BACK, u"Templat:Artikel bagus utama"),
    'is': (BACK, u"Snið:Úrvalsgrein"),
    'it': (BACK, u"Template:Vetrina"),
    'ja': (BACK, u"Template:Featured article"),
    'ka': (BACK, u"თარგი:რჩეული"),
    'km': (BACK, u"ទំព័រគំរូ:អត្ថបទពិសេស"),
    'kn': (BACK, u"ಟೆಂಪ್ಲೇಟು:ವಿಶೇಷ ಲೇಖನ"),
    'ko': (BACK, u"틀:알찬 글 딱지"),
    'ksh': (BACK, u'Schablon:Exzälenter Aatikkel'),
    'la': (BACK, u"Formula:FA stella"),
    'lmo': (BACK, u"Template:Varda che bél"),
    'lo': (BACK, u"ແມ່ແບບ:ປ້າຍບົດຄວາມດີເດັ່ນ"),
    'lt': (BACK, u"Šablonas:Featured"),
    'lv': (BACK, u"Veidne:Vērtīgs raksts"),
    'mk': (BACK, u"Шаблон:СликаАгол"),
    'ml': (BACK, u"Template:Featured"),
    'mr': (BACK, u"साचा:मुखपृष्ठ सदर टीप"),
    'ms': (BACK, u"Templat:Rencana pilihan"),
    'nah': (BACK, u"Plantilla:Featured article"),
    'nds-nl': (BACK, u"Sjabloon:Etelazie"),
    'nl': (BACK, u"Sjabloon:Etalage"),
    'nn': (BACK, u"Mal:God artikkel"),
    'no': (BACK, u"Mal:Utmerket"),
    'oc': (BACK, u"Modèl:Article de qualitat"),
    'pl': (BACK, u"Szablon:Medal"),
    'pt': (BACK, u"Predefinição:Artigo destacado"),
    'ro': (BACK, u"Format:Articol de calitate"),
    'ru': (BACK, u"Шаблон:Избранная статья"),
    'sco': (BACK, u"Template:FA"),
    'simple': (BACK, u"Template:Vgood"),
    'sk': (BACK, u"Šablóna:Perfektný článok"),
    'sl': (BACK, u"Predloga:Zvezdica"),
    'sq': (BACK, u"Stampa:Artikulli perfekt"),
    'sr': (BACK, u"Шаблон:Изабрани"),
    'sv': (BACK, u"Mall:Utmärkt"),
    'ta': (BACK, u"வார்ப்புரு:சிறப்புக் கட்டுரை"),
    'te': (BACK, u"మూస:విశేషవ్యాసం"),
    'th': (BACK, u"แม่แบบ:บทความคัดสรร"),
    'tl': (BACK, u"Template:Napiling artikulo"),
    'tr': (BACK, u"Şablon:Seçkin madde"),
    'uk': (BACK, u"Шаблон:Медаль"),
    'ur': (BACK, u"سانچہ:منتخب مقالہ"),
    'uz': (BACK, u"Shablon:Bu tanlangan maqola"),
    'vi': (BACK, u"Tiêu bản:Sao chọn lọc"),
    'vo': (BACK, u"Samafomot:Yeged gudik"),
    'yi': (BACK, u"מוסטער:רעקאמענדירטער ארטיקל"),
    'yo': (BACK, u"Template:Ayoka pataki"),
    'zh': (BACK, u"Template:Featured article"),
    'zh-classical': (BACK, u"Template:絕妙好文"),
    'zh-yue': (BACK, u"Template:正文"),
"""

# globals
interactive=0
nocache=0
afterpage=u"!"

try:
    cache=pickle.load(file("cache/featured","rb"))
except:
    cache={}

def featuredArticles(site):
    try:
        method=featured_name[site.lang][0]
    except KeyError, ex:
        print 'Error: language %s doesn\'t have feature category source.' % ex
        sys.exit()
    name=featured_name[site.lang][1]
    args=featured_name[site.lang][2:]
    raw=method(site, name, *args)
    arts=[]
    for p in raw:
        if p.namespace()==0: # Article
            arts.append(p)
        elif p.namespace()==1: # Article talk (like in English)
            arts.append(wikipedia.Page(p.site(), p.titleWithoutNamespace()))
    wikipedia.output('\03{lightred}** wikipedia:%s has %i featured articles\03{default}' % (site.lang, len(arts)))
    return arts

def findTranslated(page, oursite=None):
    if not oursite:
        oursite=wikipedia.getSite()
    if page.isRedirectPage():
        page = page.getRedirectTarget()
    try:
        iw=page.interwiki()
    except:
        wikipedia.output(u"%s -> no interwiki, giving up" % page.title())
        return None
    ourpage=None
    for p in iw:
        if p.site()==oursite:
            ourpage=p
            break
    if not ourpage:
        wikipedia.output(u"%s -> no corresponding page in %s" % (page.title(), oursite))
        return None
    if not ourpage.exists():
        wikipedia.output(u"%s -> our page doesn't exist: %s" % (page.title(), ourpage.title()))
        return None
    if ourpage.isRedirectPage():
        ourpage = ourpage.getRedirectTarget()
    wikipedia.output(u"%s -> corresponding page is %s" % (page.title(), ourpage.title()))
    if ourpage.namespace() != 0:
        wikipedia.output(u"%s -> not in the main namespace, skipping" % page.title())
        return None
    if ourpage.isRedirectPage():
        wikipedia.output(u"%s -> double redirect, skipping" % page.title())
        return None
    if not ourpage.exists():
        wikipedia.output(u"%s -> page doesn't exist, skipping" % ourpage.title())
        return None
    try:
        iw=ourpage.interwiki()
    except:
        return None
    backpage=None
    for p in iw:
        if p.site()==page.site():
            backpage=p
            break
    if not backpage:
        wikipedia.output(u"%s -> no back interwiki ref" % page.title())
        return None
    if backpage==page:
        # everything is ok
        return ourpage
    if backpage.isRedirectPage():
        backpage = backpage.getRedirectTarget()
    if backpage==page:
        # everything is ok
        return ourpage
    wikipedia.output(u"%s -> back interwiki ref target is %s" % (page.title(), backpage.title()))
    return None

def featuredWithInterwiki(fromsite, tosite, template_on_top):
    if not fromsite.lang in cache:
        cache[fromsite.lang]={}
    if not tosite.lang in cache[fromsite.lang]:
        cache[fromsite.lang][tosite.lang]={}
    cc=cache[fromsite.lang][tosite.lang]
    if nocache:
        cc={}

    templatelist = wikipedia.translate(wikipedia.getSite(), template)
    findtemplate = '(' + '|'.join(templatelist) + ')'
    re_Link_FA=re.compile(ur"\{\{%s\|%s\}\}" % (findtemplate.replace(u' ', u'[ _]'), fromsite.lang), re.IGNORECASE)
    re_this_iw=re.compile(ur"\[\[%s:[^]]+\]\]" % fromsite.lang)

    arts=featuredArticles(fromsite)

    pairs=[]
    for a in arts:
        if a.title()<afterpage:
            continue
        if u"/" in a.title() and a.namespace() != 0:
            wikipedia.output(u"%s is a subpage" % a.title())
            continue
        if a.title() in cc:
            wikipedia.output(u"(cached) %s -> %s"%(a.title(), cc[a.title()]))
            continue
        if a.isRedirectPage():
            a=a.getRedirectTarget()
        try:
            if not a.exists():
                wikipedia.output(u"source page doesn't exist: %s" % a.title())
                continue
            atrans=findTranslated(a,tosite)
            if atrans:
                text=atrans.get()
                m=re_Link_FA.search(text)
                if m:
                    wikipedia.output(u"(already done)")
                else:
                    # insert just before interwiki
                    if (not interactive or
                        wikipedia.input(u'Connecting %s -> %s. Proceed? [Y/N]'%(a.title(), atrans.title())) in ['Y','y']
                        ):
                        m=re_this_iw.search(text)
                        if not m:
                            wikipedia.output(u"no interwiki record, very strange")
                            continue
                        comment = wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg) % (fromsite.lang, a.title()))

                        ### Moving {{Link FA|xx}} to top of interwikis ###
                        if template_on_top == True:
                            text=wikipedia.replaceCategoryLinks(text+(u"{{%s|%s}}"%(templatelist[0], fromsite.lang)), atrans.categories())

                        ### Placing {{Link FA|xx}} right next to corresponding interwiki ###
                        else:
                            text=(text[:m.end()]
                                  + (u" {{%s|%s}}" % (templatelist[0], fromsite.lang))
                                  + text[m.end():])

                        try:
                            atrans.put(text, comment)
                        except wikipedia.LockedPage:
                            wikipedia.output(u'Page %s is locked!' % atrans.title())

                cc[a.title()]=atrans.title()
        except wikipedia.PageNotSaved, e:
            wikipedia.output(u"Page not saved")

if __name__=="__main__":
    template_on_top = False
    fromlang=[]
    for arg in wikipedia.handleArgs():
        if arg == '-interactive':
            interactive=1
        elif arg == '-nocache':
            nocache=1
        elif arg.startswith('-fromlang:'):
            fromlang=arg[10:].split(",")
            try:
                # BUG: range with zh-min-nan (3 "-")
                if len(fromlang)==1 and fromlang[0].index("-")>=0:
                    ll1,ll2=fromlang[0].split("--",1)
                    if not ll1: ll1=""
                    if not ll2: ll2="zzzzzzz"
                    fromlang=[ll for ll in featured_name.keys() if ll>=ll1 and ll<=ll2]
            except:
                pass
        elif arg == '-fromall':
            fromlang=featured_name.keys()
        elif arg.startswith('-after:'):
            afterpage=arg[7:]
        elif arg == '-top':
            template_on_top = True

    if not fromlang:
        wikipedia.showHelp('featured')
        sys.exit(1)

    fromlang.sort()
    try:
        for ll in fromlang:
            fromsite = wikipedia.getSite(ll)
            if  fromsite != wikipedia.getSite():
                featuredWithInterwiki(fromsite, wikipedia.getSite(),
                                      template_on_top)
    finally:
        wikipedia.stopme()
        if not nocache:
            pickle.dump(cache,file("cache/featured","wb"))

