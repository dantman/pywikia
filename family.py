# -*- coding: utf-8  -*-
import config, urllib

__version__='$Id$'

# Parent class for all wiki families

class Family:
    def __init__(self):

        self.knownlanguages = [
            'aa','ab','af','ak','als','am','an','ang','ar','arc','as','ast','av',
            'ay','az','ba','be','bg','bh','bi','bm','bn','bo','br','bs','bug','ca','ce',
            'ceb','ch','cho','chr','chy','co','cr','cs','csb','cv','cy','da','de',
            'dv','dz','ee','el','en','eo','es','et','eu','fa','ff','fi','fiu-vro',
            'fj','fo','fr','fur','fy','ga','gd','gl','gn','got','gu','gv','ha',
            'haw','he','hi','ho','hr','ht','hu','hy','hz','ia','id','ie','ig',
            'ii','ik','io','is','it','iu','ja','jbo','jv','ka','kg','ki','kj',
            'kk','kl','km','kn','ko','kr','ks','ku','kv','kw','ky','la','lad','lb',
            'lg','li','lmo','ln','lo','lt','lv','mg','mh','mi','mk','ml','mn','mo',
            'mr','ms','mt','mus','my','na','nah','nap','nds','ne','ng','nl','nn',
            'no','nv','ny','oc','om','or','os','pa','pam','pi','pih','pl','ps','pt',
            'qu','rm','rn','ro','roa-rup','ru','rw','sa','sc','scn','sco','sd',
            'se','sg','sh','si','simple','sk','sl','sm','sn','so','sq','sr',
            'ss','st','su','sv','sw','ta','te','tg','th','ti','tk','tl','tn',
            'to','tpi','tr','ts','tt','tum','tw','ty','udm','ug','uk','ur','uz','ve','vec',
            'vi','vo','wa','war','wo','xh','yi','yo','za','zh','zh-min-nan','zu']
        self.alphabetic = [
            'aa','ab','af','als','am','ang','ar','an','roa-rup','as','arc','ast','av','ay',
            'az','bg','bm','minnan','zh-min-nan','ba','be','bn','bh','bi','bo',
            'bs','br','ca','ceb','cv','ch','chr','ny','sn','cho','co','cs','cy','da','de',
            'dv','dz','et','el','en','es','eo','eu','ee','fa','fo','fj','fr',
            'fy','ff','fur','ga','gv','gd','gl','got','gn','gu','ko','ht','ha','haw',
            'hy','hi','hr','io','ik','id','ia','ie','iu','xh','zu','is','it','he',
            'jv','kl','kn','ka','kap','kk','csb','ks','kw','km','ky','rn','sw','ku',
            'lad','lo','la','lv','lt','lb','li','ln','jbo','lg','lmo','hu','mk','mg',
            'ml','mt','mi','mr','ms','mn','mo','mus','my','nah','na','nv','nap','ng',
            'nl','cr','ne','nds','ja','pih','no','nb','nn','oc','or','om','os','ug',
            'pi','ps','nds','pl','pt','pa','ro','rm','qu','ru','se','sm','sa','sg',
            'sc','sco','st','sq','sh','scn','si','simple','sd','ss','sk','sl','sr',
            'su','fi','sv','tl','tg','ta','tt','te','th','ti','tlh','vi',
            'tokipona','tpi','to','ts','tk','tum','tr','tw','udm','bug','uk','ur',
            'ug','uz','ve','vec','vo','wa','war','wo','ts','yi','yo','za','zh',
            'zh-cn','zh-tw']


        # Note that if mylang is 'commons', it is automatically added.
        self.langs = {}
        
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces = {
            -2: {
                '_default': u'Media',
            },
            -1: {
                '_default': u'Special',
                'af': u'Spesiaal',
                'als': u'Spezial',
                'ar': u'خاص',
                'be': u'Спэцыяльныя',
                'bg': u'Специални',
                'bn': u'বিশেষ',
                'ca': u'Especial',
                'cs': u'Speciální',
                'csb': u'Specjalnô',
                'cy': u'Arbennig',
                'da': u'Speciel',
                'de': u'Spezial',
                'el': u'Ειδικό',
                'eo': u'Speciala',
                'es': u'Especial',
                'et': u'Eri',
                'fa': u'ویژه',
                'fi': u'Toiminnot',
                'fo': u'Serstakur',
                'fy': u'Wiki',
                'ga': u'Speisialta',
                'he': u'מיוחד',
                'hi': u'विशेष',
                'hu': u'Speciális',
                'id': u'Istimewa',
                'is': u'Kerfissíða',
                'it': u'Speciale',
                'ja': u'特別',
                'ka': u'სპეციალური',
                'ko': u'특수기능',
                'ku': u'Taybet',
                'la': u'Specialis',
                'li': u'Speciaal',
                'ms': u'Istimewa',
                'nds': u'Spezial',
                'nl': u'Speciaal',
                'nn': u'Spesial',
                'no': u'Spesial',
                'oc': u'Especial',
                'pl': u'Specjalna',
                'pt': u'Especial',
                'ru': u'Служебная',    # u'Специальные',
                'sc': u'Speciale',
                'sk': u'Špeciálne',
                'sl': u'Posebno',
                'sq': u'Speciale',
                'sr': u'Посебно',
                'uk': u'Спеціальні',
                'ta': u'சிறப்பு',
                'th': u'พิเศษ',
                'tt': u'Maxsus',
                'uk': u'Спеціальні',
                'vi': u'Đặc biệt',
                'wa': u'Sipeciås',
            },
            0: {
                '_default': None,
            },
            1: {
                '_default': u'Talk',
                'af': u'BronnemateriaalEnBespreking',
                'als': u'Diskussion',
                'ar': u'نقاش',
                'be': u'Абмеркаваньне',
                'bg': u'Беседа',
                'bn': u'আলাপ',
                'ca': u'Discussió',
                'cs': u'Diskuse',
                'csb': u'Diskùsëjô',
                'cy': u'Sgwrs',
                'da': u'Diskussion',
                'de': u'Diskussion',
                'el': u'Συζήτηση',
                'eo': u'Diskuto',
                'es': u'Discusión',
                'et': u'Arutelu',
                'fa': u'بحث',
                'fi': u'Keskustelu',
                'fo': u'Kjak',
                'fr': u'Discuter',
                'fy': u'Oerlis',
                'ga': u'Plé',
                'he': u'שיחה',
                'hi': u'वार्ता',
                'hu': u'Vita',
                'ia': u'Discussion',
                'id': u'Bicara',
                'is': u'Spjall',
                'it': u'Discussione',
                'ja': u'ノート',
                'ka': u'განხილვა',
                'ko': u'토론',
                'ku': u'Nîqaş',
                'la': u'Disputatio',
                'li': u'Euverlik',
                'ms': u'Perbualan',
                'nds': u'Diskuschoon',
                'nl': u'Overleg',
                'nn': u'Diskusjon',
                'no': u'Diskusjon',
                'nv': u"Naaltsoos baa yinísht'į́",
                'oc': u'Discutir',
                'pl': u'Dyskusja',
                'pt': u'Discussão',
                'ro': u'Discuţie',
                'ru': u'Обсуждение',
                'sc': u'Contièndha',
                'sk': u'Komentár',
                'sl': u'Pogovor',
                'sq': u'Diskutim',
                'sr': u'Разговор',
                'sv': u'Diskussion',
                'ta': u'பேச்சு',
                'th': u'พูดคุย',
                'tt': u'Bäxäs',
                'uk': u'Обговорення',
                'vi': u'Thảo luận',
                'wa': u'Copene',
            },
            2: {
                '_default': u'User',
                'af': u'Gebruiker',
                'als': u'Benutzer',
                'ar': u'مستخدم',
                'ast': u'Usuariu',
                'be': u'Удзельнік',
                'bg': u'Потребител',
                'bn': u'ব\u09cdযবহারকারী',
                'br': u'Implijer',
                'ca': u'Usuari',
                'csb': u'Brëkòwnik',
                'cs': u'Wikipedista',
                'cy': u'Defnyddiwr',
                'da': u'Bruger',
                'de': u'Benutzer',
                'el': u'Χρήστης',
                'eo': u'Vikipediisto',
                'es': u'Usuario',
                'et': u'Kasutaja',
                'eu':  u'Lankide',
                'fa': u'کاربر',
                'fi': u'Käyttäjä',
                'fo': u'Brúkari',
                'fr': u'Utilisateur',
                'fy': u'Meidogger',
                'ga': u'Úsáideoir',
                'he': u'משתמש',
                'hi': u'सदस्य',
                'hr': u'Suradnik',
                'ia': u'Usator',
                'id': u'Pengguna',
                'is': u'Notandi',
                'it': u'Utente',
                'ja': u'利用者',
                'ka': u'მომხმარებელი',
                'ko': u'사용자',
                'ku': u'Bikarhêner',
                'la': u'Usor',
                'li': u'Gebroeker',
                'mk': u'Корисник',
                'ms': u'Pengguna',
                'nds': u'Bruker',
                'nl': u'Gebruiker',
                'nn': u'Brukar',
                'no': u'Bruker',
                'nv': u"Choinish'įįhí",
                'oc': u'Utilisator',
                'os': u'Архайæг',
                'pl': u'Wikipedysta',
                'pt': u'Usuário',
                'ro': u'Utilizator',
                'ru': u'Участник',
                'sc': u'Utente',
                'sk': u'Redaktor',
                'sl': u'Uporabnik',
                'sq': u'Përdoruesi',
                'sr': u'Корисник',
                'sv': u'Användare',
                'ta': u'பயனர்',
                'th': u'ผู้ใช' + u'\u0e49',
                'tr': u'Kullanıcı',
                'tt': u'Äğzä',
                'uk': u'Користувач',
                'vi': u'Thành viên',
                'wa': u'Uzeu',
            },
            3: {
                '_default': u'User talk',
                'af': u'GebruikerBespreking',
                'als': u'Benutzer Diskussion',
                'bg': u'Потребител беседа',
                'ca': u'Usuari Discussió',
                'cs': u'Wikipedista diskuse',
                'da': u'Bruger diskussion',
                'de': u'Benutzer Diskussion',
                'es': u'Usuario Discusión',
                'hu': u'User vita',
                'ka': u'მომხმარებელი განხილვა',
                'li': u'Euverlik gebroeker',
                'nl': u'Overleg gebruiker',
                'pl': u'Dyskusja Wikipedysty',
                'pt': u'Usuário Discussão',
                'sk': u'Diskusia s redaktorom',
            },
            4: {
                '_default': u'Project',
            },
            5: {
                '_default': u'Project talk',
            },
            6: {
                '_default': u'Image',
                'af': u'Beeld',
                'als': u'Bild',
                'ar': u'صورة',
                'be': u'Выява',
                'bg': u'Картинка',
                'ca': u'Imatge',
                'cbs': u'Òbrôzk',
                'cs': u'Soubor',
                'cy': u'Delwedd',
                'da': u'Billede',
                'de': u'Bild',
                'el': u'Εικόνα',
                'eo': u'Dosiero',
                'es': u'Imagen',
                'et': u'Pilt',
                'fa': u'تصویر',
                'fi': u'Kuva',
                'fo': u'Mynd',
                'fy': u'Ofbyld',
                'ga': u'Íomhá',
                'he': u'תמונה',
                'hi': u'चित्र',
                'hu': u'Kép',
                'ia': u'Imagine',
                'id': u'Gambar',
                'is': u'Mynd',
                'it': u'Immagine',
                'ja': u'画像',
                'ka': u'სურათი',
                'ko': u'그림',
                'ku': u'Wêne',
                'la': u'Imago',
                'li': u'Aafbeilding',
                'ms': u'Imej',
                'nds': u'Bild',
                'nl': u'Afbeelding',
                'nn': u'Fil',
                'no': u'Bilde',
                'nv': u"E'elyaaígíí",
                'pl': u'Grafika',
                'pt': u'Imagem',
                'ro': u'Imagine',
                'ru': u'Изображение',
                'sc': u'Immàgini',
                'sk': u'Obrázok',
                'sl': u'Slika',
                'sq': u'Figura',
                'sr': u'Слика',
                'sv': u'Bild',
                'ta': u'படிமம்',
                'th': u'ภาพ',
                'tt': u'Räsem',
                'uk': u'Зображення',
                'vi': u'Hình',
                'wa': u'Imådje',
            },
            7: {
                '_default': u'Image talk',
                'als': u'Bild Diskussion',
                'ca': u'Imatge Discussió',
                'da': u'Billede diskussion',
                'de': u'Bild Diskussion',
                'es': u'Imagen Discusión',
                'hu': u'Kép vita',
                'ka': u'სურათი განხილვა',
                'nl': u'Overleg afbeelding',
                'pt': u'Imagem Discussão',
            },
            8: {
                '_default': u'MediaWiki',
                'bg': u'МедияУики',
                'ka': u'მედიავიკი',
            },
            9: {
                '_default': u'MediaWiki talk',
                'als': u'MediaWiki Diskussion',
                'ca': u'MediaWiki Discussió',
                'da': u'MediaWiki diskussion',
                'de': u'MediaWiki Diskussion',
                'es': u'MediaWiki Discusión',
                'hu': u'MediaWiki vita',
                'ka': u'მედიავიკი განხილვა',
                'nl': u'Overleg MediaWiki',
                'pt': u'MediaWiki Discussão',
            },
            10: {
                '_default':u'Template',
                'af': u'Sjabloon',
                'als':u'Vorlage',
                'be': u'Шаблён',
                'bg': u'Шаблон',
                'cbs':u'Szablóna',
                'cs': u'Šablona',
                'cy': u'Nodyn',
                'da': u'Skabelon',
                'de': u'Vorlage',
                'el': u'Φόρμα',
                'eo': u'Ŝablono',
                'es': u'Plantilla',
                'et': u'Mall',
                'fi': u'Malline',
                'fo': u'Fyrimynd',
                'fy': u'Berjocht',
                'ga': u'Múnla',
                'he': u'תבנית',
                'hu': u'Sablon',
                'id': u'Templat',
                'is': u'Snið',
                'ka': u'თარგი',
                'ku': u'Şablon',
                'la': u'Formula',
                'li': u'Sjabloon',
                'nds':u'Vörlaag',
                'nl': u'Sjabloon',
                'nn': u'Mal',
                'no': u'Mal',
                'pl': u'Szablon',
                'pt': u'Predefinição',
                'ro': u'Format',
                'ru': u'Шаблон',
                'sk': u'Šablóna',
                'sq': u'Stampa',
                'sr': u'Шаблон',
                'sv': u'Mall',
                'tt': u'Ürnäk',
                'uk': u'Шаблон',
                'vi': u'Tiêu bản',
                'wa': u'Modele',
            },
            11: {
                '_default': u'Template talk',
                'als': u'Vorlage Diskussion',
                'ca': u'Template Discussió',
                'da': u'Skabelon diskussion',
                'de': u'Vorlage Diskussion',
                'es': u'Plantilla Discusión',
                'hu': u'Sablon vita',
                'ka': u'თარგი განხილვა',
                'li': u'Euverlik sjabloon',
                'nl': u'Overleg sjabloon',
                'pt': u'Predefinição Discussão',
            },
            12: {
                '_default': u'Help',
                'be': u'Дапамога',
                'ca': u'Ajuda',
                'cbs': u'Pòmòc',
                'da': u'Hjælp',
                'de': u'Hilfe',
                'el': u'Βοήθεια',
                'es': u'Ayuda',
                'hu': u'Segítség',
                'lb': u'Hëllef',
                'ka': u'დახმარება',
                'nds': u'Hülp',
                'pt': u'Ajuda',
                'uk': u'Довідка',
                'vi': u'Trợ giúp',
            },
            13: {
                '_default': u'Help talk',
                'ca': u'Ajuda Discussió',
                'da': u'Hjælp diskussion',
                'de': u'Hilfe Diskussion',
                'es': u'Ayuda Discusión',
                'ka': u'დახმარება განხილვა',
                'nl': u'Overleg help',
                'pt': u'Ajuda Discussão',
            },
            14: {
                '_default': u'Category',
                'af': u'Kategorie',
                'als': u'Kategorie',
                'ar': u'تصنيف',
                'ay': u'Categoría',
                'ast': u'Categoría',
                'be': u'Катэгорыя',
                'bg': u'Категория',
                'bm': u'Catégorie',
                'br': u'Rummad',
                'ca': u'Categoria',
                'csb': u'Kategòrëjô',
                'cs': u'Kategorie',
                'cv': u'Категори',
                'da': u'Kategori',
                'de': u'Kategorie',
                'el': u'Κατηγορία',
                'eo': u'Kategorio',
                'es': u'Categoría',
                'et': u'Kategooria',
                'fi': u'Luokka',
                'fo': u'Bólkur',
                'fr': u'Catégorie',
                'fur': u'Categorie',
                'fy': u'Kategory',
                'ga': u'Rang',
                'he': u'קטגוריה',
                'hi': u'श्रेणी',
                'hr': u'Kategorija',
                'hu': u'Kategória',
                'id': u'Kategori',
                'is': u'Flokkur',
                'it': u'Categoria',
                'ka': u'კატეგორია',
                'ko': u'분류',
                'ku': u'Kategorî',
                'la': u'Categoria',
                'li': u'Kategorie',
                'lt': u'Kategorija',
                'mk': u'Категорија',
                'nap': u'Categoria',
                'nds': u'Kategorie',
                'nl': u'Categorie',
                'nn': u'Kategori',
                'no': u'Kategori',
                'nv': u"T'ááłáhági át'éego",
                'os': u'Категори',
                'pa': u'ਸ਼੍ਰੇਣੀ',
                'pl': u'Kategoria',
                'pt': u'Categoria',
                'ro': u'Categorie',
                'ru': u'Категория',
                'sk': u'Kategória',
                'sr': u'Категорија',
                'sv': u'Kategori',
                'tr': u'Kategori',
                'tt': u'Törkem',
                'uk': u'Категорія',
                'vi': u'Thể loại',
                'wa': u'Categoreye',
                },

            
            15: {
                '_default': u'Category talk',
                'als':    u'Kategorie Diskussion',
                'bg'  :     u'Категория беседа',
                'ca'  :     u'Categoria Discussió',
                'cs'  :     u'Kategorie diskuse',
                'da'  :     u'Kategori diskussion',
                'de'  :     u'Kategorie Diskussion',
                'eo'  :     u'Kategoria diskuto',
                'es'  :     u'Categoría Discusión',
                'fr'  :     u'Discussion Catégorie',
                'hu'  :     u'Kategória vita',
                'is'  :     u'Flokkaspjall',
                'it'  :     u'Discussioni categoria',
                'ka'  :     u'კატეგორია განხილვა',
                'li':       u'Euverlik kategorie',
                'nl'  :     u'Overleg categorie',
                'no'  :     u'Kategoridiskusjon',
                'pl'  :     u'Dyskusja kategorii',
                'pt'  :     u'Categoria Discussão',
                'sv'  :     u'Kategoridiskussion',
                'tlh' :     u"Segh ja'chuq",
                'tt'  :     u'Törkem bäxäse',
                'wa'  :     u'Categoreye copene',
            },
        }
        
        # A list of disambiguation template names in different languages
        # First character must be lower case!
        self.disambigs = {
            '_default':   [u'disambig'],
            'af'  :       [u'dubbelsinnig'],
            'als' :       [u'begriffsklärung'],
            'ang' :       [u'disambig'],
            'ar'  :       [u'disambig',u'توضيح'],
            'be'  :       [u'неадназначнасьць'],
            'bg'  :       [u'пояснение'],
            'ca'  :       [u'desambiguació'],
            'cs'  :       [u'rozcestník'],
            'cy'  :       [u'anamrwysedd'],
            'da'  :       [u'flertydig'],
            'de'  :       [u'begriffsklärung'],
            'el'  :       [u'disambig'],
            'en'  :       [u'disambig', u'lND', u'2LA', u'tLAdisambig', u'disambiguation', u'2LCdisambig',
                           u'4LA', u'acrocandis', u'hndis', u'numberdis', u'roadis', u'geodis',
                           u'listdis', u'interstatedis', u'dab',u'disambig-cleanup', u'disamb'],
            'eo'  :       [u'apartigilo'],
            'es'  :       [u'desambiguacion', u'desambiguación', u'desambig'],
            'et'  :       [u'täpsustuslehekülg'],
            'eu'  :       [u'argipen'],
            'fa'  :       [u'ابهام‌زدایی'],
            'fi'  :       [u'täsmennyssivu'],
            'fr'  :       [u'homonymie'],
            'fy'  :       [u'tfs'],
            'ga'  :       [u'idirdhealú'],
            'gl'  :       [u'homónimos'],
            'he'  :       [u'disambiguationAfter', u'פירושונים'],
            'hr'  :       [u'disambig'],
            'hu'  :       [u'egyert'],
            'ia'  :       [u'disambiguation'],
            'id'  :       [u'disambig'],
            'io'  :       [u'homonimo'],
            'is'  :       [u'aðgreining'],
            'it'  :       [u'disambigua'],
            'ja'  :       [u'aimai'],
            'ka'  :       [u'არაორაზროვნება'],
            'ko'  :       [u'disambig'],
            'ku'  :       [u'cudakirin'],
            'la'  :       [u'discretiva'],
            'lb'  :       [u'homonymie'],
            'li'  :       [u'verdudeliking'],
            'ln'  :       [u'bokokani'],
            'lt'  :       [u'disambig'],
            'mt'  :       [u'diżambigwazzjoni'],
            'no'  :       [u'peker', u'etternavn'],
            'nds' :       [u'begreepkloren'],
            'nl'  :       [u'dp','dP','dp2','dpintro'],
            'nn'  :       [u'fleirtyding'],
            'pl'  :       [u'disambig',u'disambRulers',u'disambigC'],
            'pt'  :       [u'desambiguação'],
            'ro'  :       [u'dezambiguizare'],
            'ru'  :       [u'disambig',u'значения'],
            'scn' :       [u'disambigua'],
            'simple':     [u'disambig', u'disambiguation'],
            'sk'  :       [u'disambiguation'],
            'sl'  :       [u'disambig'],
            'sq'  :       [u'kthjellim'],
            'sr'  :       [u'вишезначна одредница'],
            'su'  :       [u'disambig'],
            'sv'  :       [u'betydelselista', u'disambig', u'gaffel', u'efternamn'],
            'th'  :       [u'แก้กำกวม'],
            'tl'  :       [u'paglilinaw'],
            'tr'  :       [u'anlam ayrım'],
            'vi'  :       [u'trang định hướng'],
            'wa'  :       [u'omonimeye'],
            'zh'  :       [u'disambig', u'消歧义', u'消歧义页'],
            'zh-min-nan': [u'khu-pia̍t-ia̍h','khPI'],
        }

        # On most wikis page names must start with a capital letter, but some
        # languages don't use this.
    
        self.nocapitalize = []
    
        # attop is a list of languages that prefer to have the interwiki
        # links at the top of the page.
        self.interwiki_attop = []
        # on_one_line is a list of languages that want the interwiki links
        # one-after-another on a single line
        self.interwiki_on_one_line = []
        
        # String used as separator between interwiki links and the text
        self.interwiki_text_separator = '\r\n'
        
        # Similar for category
        self.category_attop = []
        # on_one_line is a list of languages that want the category links
        # one-after-another on a single line
        self.category_on_one_line = []
        
        # String used as separator between category links and the text
        self.category_text_separator = '\r\n'
        
        # When both at the bottom should categories come after interwikilinks?
        self.categories_last = []

        # Which languages have a special order for putting interlanguage links,
        # and what order is it? If a language is not in interwiki_putfirst,
        # alphabetical order on language code is used. For languages that are in
        # interwiki_putfirst, interwiki_putfirst is checked first, and
        # languages are put in the order given there. All other languages are put
        # after those, in code-alphabetical order.
    
        self.interwiki_putfirst = {}

        # Languages in interwiki_putfirst_doubled should have a number plus a list
        # of languages. If there are at least the number of interwiki links, all
        # languages in the list should be placed at the front as well as in the
        # normal list.

        self.interwiki_putfirst_doubled = {}

        # Which language codes do no longer exist and by which language code should
        # they be replaced. If for example the language with code xx: now should get
        # code yy:, add {'xx':'yy'} to obsolete.
    
        self.obsolete = {}
        
        # Language codes of the largest wikis. They should be roughly sorted
        # by size.
        
        self.languages_by_size = []

        # languages in Cyrillic
        self.cyrilliclangs = []
        
        # Main page names for all languages
        self.mainpages = {}

    def _addlang(self, code, location, namespaces = {}):
        """Add a new language to the langs and namespaces of the family.
           This is supposed to be called in the constructor of the family."""
        self.langs[code] = location
        
        for num, val in namespaces.items():
            self.namespaces[num][code]=val
        
    def namespace(self, code, namespace_number, fallback = '_default'):
        if self.namespaces[namespace_number].has_key(code):
            return self.namespaces[namespace_number][code]
        elif fallback:
            return self.namespaces[namespace_number][fallback]
        else:
            raise KeyError('ERROR: title for namespace %d in language %s unknown' % (namespace_number, code))  
    
    def disambig(self, code, fallback = '_default'):
        if self.disambigs.has_key(code):
            return self.disambigs[code]
        elif fallback:
            return self.disambigs[fallback]
        else:
            raise KeyError('ERROR: title for disambig template in language %s unknown' % code)  

    # Returns the title of the special namespace in language 'code', taken from
    # dictionary above.
    # If the dictionary doesn't contain a translation, it will use language
    # 'fallback' (or, if fallback isn't given, MediaWiki default).
    # If you want the bot to crash in case of an unknown namespace name, use
    # fallback = None.
    def special_namespace(self, code, fallback = '_default'):
        return self.namespace(code, -1, fallback)
    
    def special_namespace_url(self, code, fallback = '_default'):
        encoded_title = self.namespace(code, -1, fallback).encode(self.code2encoding(code))
        return urllib.quote(encoded_title)
    
    def image_namespace(self, code, fallback = '_default'):
        return self.namespace(code, 6, fallback)
    
    def image_namespace_url(self, code, fallback = '_default'):
        encoded_title = self.namespace(code, 6, fallback).encode(self.code2encoding(code))
        return urllib.quote(encoded_title)
    
    def mediawiki_namespace(self, code, fallback = '_default'):
        return self.namespace(code, 8, fallback)
    
    def template_namespace(self, code, fallback = '_default'):
        return self.namespace(code, 10, fallback)
     
    def category_namespace(self, code, fallback = '_default'):
        return self.namespace(code, 14, fallback)
    
    def category_namespaces(self, code):
        namespaces = []
        namespace_title = self.namespace(code, 14)
        namespaces.append(namespace_title)
        if namespace_title != namespace_title.lower():
            namespaces.append(namespace_title.lower())
        default_namespace_title = self.namespace('_default', 14)
        if namespace_title != default_namespace_title:
            namespaces.append(default_namespace_title)
            if default_namespace_title != default_namespace_title.lower():
                namespaces.append(default_namespace_title.lower())
        return namespaces

    # Redirect code can be translated.

    redirect = {
        'bg': [u'виж'],
        'cs': [u'přesměruj'],
        'cy': [u'ail-cyfeirio'],
        'et': [u'suuna'],
        'eu': [u'bidali'],
        'ga': [u'athsheoladh'],
        'id': [u'redirected'],
        'is': [u'tilvísun'],
        'nn': [u'omdiriger'],
        'ru': [u'перенаправление', u'перенапр'],
        'sr': [u'преусмери'],
        'tt': [u'yünältü']
    }

    # So can be pagename code
    pagename = {
        'bg': [u'СТРАНИЦА'],
        'nn': ['SIDENAMN','SIDENAVN'],
        'ru': [u'НАЗВАНИЕСТРАНИЦЫ'],
        'tt': [u'BİTİSEME']
    }

    pagenamee = {
        'nn': ['SIDENAMNE','SIDENAVNE'],
        'ru': [u'НАЗВАНИЕСТРАНИЦЫ2']
    }

    def pagenamecodes(self,code):
        pos = ['PAGENAME']
        pos2 = []
        if code in self.pagename.keys():
            pos = pos + self.pagename[code]
        elif code == 'als':
            return self.pagenamecodes('de')
        elif code == 'bm':
            return self.pagenamecodes('fr')
        for p in pos:
            pos2 += [p,p.lower()]
        return pos2

    def pagename2codes(self,code):
        pos = ['PAGENAME']
        pos2 = []
        if code in self.pagenamee.keys():
            pos = pos + self.pagenamee[code]
        elif code == 'als':
            return self.pagename2codes('de')
        elif code == 'bm':
            return self.pagename2codes('fr')
        for p in pos:
            pos2 += [p,p.lower()]
        return pos2


        
    # Methods
    
    def hostname(self, code):
        return self.langs[code]
    
    def path(self, code):
        return '/w/index.php'

    # Which version of MediaWiki is used?

    def version(self, code):
        return "1.5"

    def put_address(self, code, name):
        return '%s?title=%s&action=submit' % (self.path(code), name)

    def get_address(self, code, name):
        return '%s?title=%s&redirect=no' % (self.path(code), name)

    def edit_address(self, code, name):
        return '%s?title=%s&action=edit' % (self.path(code), name)

    def purge_address(self, code, name):
        return '%s?title=%s&redirect=no&action=purge' % (self.path(code), name)

    def references_address(self, code, name):
        return '%s?title=%s:Whatlinkshere&target=%s&limit=%d' % (self.path(code), self.special_namespace_url(code), name, config.special_page_limit)

    def upload_address(self, code):
        return '%s?title=%s:Upload' % (self.path(code), self.special_namespace_url(code))

    def maintenance_address(self, code, maintenance_page, default_limit = True):
        if default_limit:
            return '%s?title=%s:Maintenance&subfunction=%s' % (self.path(code), self.special_namespace_url(code), maintenance_page)
        else:
            return '%s?title=%s:Maintenance&subfunction=%s&limit=%d' % (self.path(code), self.special_namespace_url(code), maintenance_page, config.special_page_limit)

    def double_redirects_address(self, code, default_limit = True):
        if default_limit:
            return '%s?title=%s:DoubleRedirects' % (self.path(code), self.special_namespace_url(code))
        else:
            return '%s?title=%s:DoubleRedirects&limit=%d' % (self.path(code), self.special_namespace_url(code), config.special_page_limit)

    def broken_redirects_address(self, code, default_limit = True):
        if default_limit:
            return '%s?title=%s:BrokenRedirects' % (self.path(code), self.special_namespace_url(code))
        else:
            return '%s?title=%s:BrokenRedirects&limit=%d' % (self.path(code), self.special_namespace_url(code), config.special_page_limit)

    def allmessages_address(self, code):
        return "%s?title=%s:Allmessages&ot=html" % (self.path(code), self.special_namespace_url(code))

    def login_address(self, code):
        return '%s?title=%s:Userlogin&action=submit' % (self.path(code), self.special_namespace_url(code))

    def watchlist_address(self, code):
        return '%s?title=%s:Watchlist&magic=yes' % (self.path(code), self.special_namespace_url(code))
    
    def move_address(self, code):
        return '%s?title=%s:Movepage&action=submit' % (self.path(code), self.special_namespace_url(code))

    def delete_address(self, code, name):
        return '%s?title=%s&action=delete' % (self.path(code), name)

    def version_history_address(self, code, name):
        return '%s?title=%s&action=history&limit=%d' % (self.path(code), name, config.special_page_limit)

    def export_address(self, code):
        return '%s?title=%s:Export' % (self.path(code), self.special_namespace_url(code))

    def allpages_address(self, code, start, namespace = 0):
        if self.version(code)=="1.2":
            return '%s?title=%s:Allpages&printable=yes&from=%s' % (
                self.path(code), self.special_namespace_url(code), start)
        else:
            return '%s?title=%s:Allpages&from=%s&namespace=%s' % (
                self.path(code), self.special_namespace_url(code), start, namespace)

    def newpages_address(self, code, limit=50):
        return "%s?title=%s:Newpages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def longpages_address(self, code, limit=500):
        return "%s?title=%s:Longpages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def shortpages_address(self, code, limit=500):
        return "%s?title=%s:Shortpages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def categories_address(self, code, limit=500):
        return "%s?title=%s:Categories&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def deadendpages_address(self, code, limit=500):
        return "%s?title=%s:Deadendpages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def ancientpages_address(self, code, limit=500):
        return "%s?title=%s:Ancientpages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def lonelypages_address(self, code, limit=500):
        return "%s?title=%s:Lonelypages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def uncategorizedcategories_address(self, code, limit=500):
        return "%s?title=%s:Uncategorizedcategories&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)
    
    def uncategorizedpages_address(self, code, limit=500):
        return "%s?title=%s:Uncategorizedpages&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)
    
    def unusedcategories_address(self, code, limit=500):
        return "%s?title=%s:Unusedcategories&limit=%d" % (self.path(code), self.special_namespace_url(code), limit)

    def code2encoding(self, code):
        """Return the encoding for a specific language wiki"""
        return 'utf-8'

    def code2encodings(self, code):
        """Return a list of historical encodings for a specific language
           wiki"""
        return self.code2encoding(code),

    def __cmp__(self, otherfamily):
        try:
            return cmp(self.name, otherfamily.name)
        except AttributeError:
            return cmp(id(self), id(otherfamily))

