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
            'ii','ik','ilo','io','is','it','iu','ja','jbo','jv','ka','kg','ki','kj',
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
            'hy','hi','hr','io','ik','ilo','id','ia','ie','iu','xh','zu','is','it','he',
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

        self.langs = {}
        
        # Translation used on all wikis for the different namespaces.
        # (Please sort languages alphabetically)
        # You only need to enter translations that differ from _default.
        self.namespaces = {
            -2: {
                '_default': u'Media',
                'ab': u'Медиа',
                'ar': u'ملف',
                'av': u'Медиа',
                'ba': u'Медиа',
                'be': u'Мэдыя',
                'bg': u'Медия',
                'ce': u'Медиа',
                'cs': u'Média',
                'cv': u'Медиа',
                'el': u'Μέσον',
                'et': u'Meedia',
                'fa': u'مدیا',
                'fo': u'Miðil',
                'ga': u'Meán',
                'hr': u'Mediji',
                'hu': u'Média',
                'is': u'Miðill',
                'ka': u'მედია',
                'ku': u'Medya',
                'kv': u'Медиа',
                'lt': u'Medija',
                'mk': u'Медија',
                'nn': u'Filpeikar',
                'no': u'Medium',
                'pa': u'ਮੀਡੀਆ',
                'ru': u'Медиа',
                'sk': u'Médiá',
                'sr': u'Медија',
                'su': u'Média',
                'ta': u'ஊடகம்',
                'udm': u'Медиа',
                'uk': u'Медіа',
                'vi': u'Phương tiện',
                'yi': u'מעדיע',
            },
            -1: {
                '_default': u'Special',
                'ab': u'Служебная',
                'af': u'Spesiaal',
                'als': u'Spezial',
                'ar': u'خاص',
                'ast': u'Especial',
                'av': u'Служебная',
                'ay': u'Especial',
                'ba': u'Служебная',
                'be': u'Спэцыяльныя',
                'bg': u'Специални',
                'bn': u'বিশেষ',
                'br': u'Dibar',
                'ca': u'Especial',
                'ce': u'Служебная',
                'cs': u'Speciální',
                'csb': u'Specjalnô',
                'cv': u'Ятарлă',
                'cy': u'Arbennig',
                'da': u'Speciel',
                'de': u'Spezial',
                'el': u'Ειδικό',
                'eo': u'Speciala',
                'es': u'Especial',
                'et': u'Eri',
                'eu': u'Aparteko',
                'fa': u'ویژه',
                'fi': u'Toiminnot',
                'fo': u'Serstakur',
                'fur': u'Speciâl',
                'fy': u'Wiki',
                'ga': u'Speisialta',
                'gn': u'Especial',
                'he': u'מיוחד',
                'hi': u'विशेष',
                'hr': u'Posebno',
                'hu': u'Speciális',
                'id': u'Istimewa',
                'is': u'Kerfissíða',
                'it': u'Speciale',
                'ja': u'特別',
                'ka': u'სპეციალური',
                'ko': u'특수기능',
                'ku': u'Taybet',
                'kv': u'Служебная',
                'la': u'Specialis',
                'li': u'Speciaal',
                'lt': u'Specialus',
                'mk': u'Специјални',
                'ms': u'Istimewa',
                'nah': u'Especial',
                'nap': u'Speciale',
                'nds': u'Spezial',
                'nl': u'Speciaal',
                'nn': u'Spesial',
                'no': u'Spesial',
                'oc': u'Especial',
                'os': u'Сæрмагонд',
                'pa': u'ਖਾਸ',
                'pl': u'Specjalna',
                'pt': u'Especial',
                'qu': u'Especial',
                'ru': u'Служебная',
                'sc': u'Speciale',
                'sk': u'Špeciálne',
                'sl': u'Posebno',
                'sq': u'Speciale',
                'sr': u'Посебно',
                'su': u'Husus',
                'ta': u'சிறப்பு',
                'th': u'พิเศษ',
                'tr': u'Özel',
                'tt': u'Maxsus',
                'udm': u'Панель',
                'uk': u'Спеціальні',
                'vec':u'Speciale',
                'vi': u'Đặc biệt',
                'wa': u'Sipeciås',
                'yi': u'באַזונדער',
            },
            0: {
                '_default': None,
            },
            1: {
                '_default': u'Talk',
                'ab': u'Обсуждение',
                'af': u'Bespreking',
                'als': u'Diskussion',
                'ar': u'نقاش',
                'ast': u'Discusión',
                'av': u'Обсуждение',
                'ay': u'Discusión',
                'ba': u'Обсуждение',
                'be': u'Абмеркаваньне',
                'bg': u'Беседа',
                'bm': u'Discuter',
                'bn': u'আলাপ',
                'br': u'Kaozeal',
                'ca': u'Discussió',
                'ce': u'Обсуждение',
                'cs': u'Diskuse',
                'csb': u'Diskùsëjô',
                'cv': u'Сӳтсе явасси',
                'cy': u'Sgwrs',
                'da': u'Diskussion',
                'de': u'Diskussion',
                'el': u'Συζήτηση',
                'eo': u'Diskuto',
                'es': u'Discusión',
                'et': u'Arutelu',
                'eu': u'Eztabaida',
                'fa': u'بحث',
                'fi': u'Keskustelu',
                'fo': u'Kjak',
                'fr': u'Discuter',
                'fur': u'Discussion',
                'fy': u'Oerlis',
                'ga': u'Plé',
                'gn': u'Discusión',
                'he': u'שיחה',
                'hi': u'वार्ता',
                'hr': u'Razgovor',
                'hu': u'Vita',
                'ia': u'Discussion',
                'id': u'Bicara',
                'is': u'Spjall',
                'it': u'Discussione',
                'ja': u'ノート',
                'ka': u'განხილვა',
                'ko': u'토론',
                'ku': u'Nîqaş',
                'kv': u'Обсуждение',
                'la': u'Disputatio',
                'li': u'Euverlik',
                'lt': u'Aptarimas',
                'mk': u'Разговор',
                'ms': u'Perbualan',
                'nah': u'Discusión',
                'nap': u'Discussione',
                'nds': u'Diskuschoon',
                'nl': u'Overleg',
                'nn': u'Diskusjon',
                'no': u'Diskusjon',
                'nv': u"Naaltsoos baa yinísht'į́",
                'oc': u'Discutir',
                'os': u'Дискусси',
                'pa': u'ਚਰਚਾ',
                'pl': u'Dyskusja',
                'pt': u'Discussão',
                'qu': u'Discusión',
                'ro': u'Discuţie',
                'ru': u'Обсуждение',
                'sc': u'Contièndha',
                'sk': u'Diskusia',
                'sl': u'Pogovor',
                'sq': u'Diskutim',
                'sr': u'Разговор',
                'su': u'Obrolan',
                'sv': u'Diskussion',
                'ta': u'பேச்சு',
                'th': u'พูดคุย',
                'tr': u'Tartışma',
                'tt': u'Bäxäs',
                'ty': u'Discuter',
                'udm': u'Вераськон',
                'uk': u'Обговорення',
                'vec':u'Discussion',
                'vi': u'Thảo luận',
                'wa': u'Copene',
                'yi': u'רעדן',
            },
            2: {
                '_default': u'User',
                'ab': u'Участник',
                'af': u'Gebruiker',
                'als': u'Benutzer',
                'ar': u'مستخدم',
                'ast': u'Usuariu',
                'av': u'Участник',
                'ay': u'Usuario',
                'ba': u'Участник',
                'be': u'Удзельнік',
                'bg': u'Потребител',
                'bm': u'Utilisateur',
                'bn': u'ব\u09cdযবহারকারী',
                'br': u'Implijer',
                'ca': u'Usuari',
                'ce': u'Участник',
                'cs': u'Uživatel',
                'csb': u'Brëkòwnik',
                'cv': u'Хутшăнакан',
                'cy': u'Defnyddiwr',
                'da': u'Bruger',
                'de': u'Benutzer',
                'el': u'Χρήστης',
                'eo': u'Vikipediisto',
                'es': u'Usuario',
                'et': u'Kasutaja',
                'eu': u'Lankide',
                'fa': u'کاربر',
                'fi': u'Käyttäjä',
                'fo': u'Brúkari',
                'fr': u'Utilisateur',
                'fur': u'Utent',
                'fy': u'Meidogger',
                'ga': u'Úsáideoir',
                'gn': u'Usuario',
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
                'kv': u'Участник',
                'la': u'Usor',
                'li': u'Gebroeker',
                'lt': u'Naudotojas',
                'mk': u'Корисник',
                'ms': u'Pengguna',
                'nah': u'Usuario',
                'nap': u'Utente',
                'nds': u'Bruker',
                'nl': u'Gebruiker',
                'nn': u'Brukar',
                'no': u'Bruker',
                'nv': u"Choinish'įįhí",
                'oc': u'Utilisator',
                'os': u'Архайæг',
                'pa': u'ਮੈਂਬਰ',
                'pl': u'Wikipedysta',
                'pt': u'Usuário',
                'qu': u'Usuario',
                'ro': u'Utilizator',
                'ru': u'Участник',
                'sc': u'Utente',
                'sk': u'Redaktor',
                'sl': u'Uporabnik',
                'sq': u'Përdoruesi',
                'sr': u'Корисник',
                'su': u'Pamaké',
                'sv': u'Användare',
                'ta': u'பயனர்',
                'th': u'ผู้ใช' + u'\u0e49',
                'tr': u'Kullanıcı',
                'tt': u'Äğzä',
                'ty': u'Utilisateur',
                'udm': u'Викиавтор',
                'uk': u'Користувач',
                'vec':u'Utente',
                'vi': u'Thành viên',
                'wa': u'Uzeu',
                'yi': u'באַניצער',
            },
            3: {
                '_default': u'User talk',
                'ab': u'Обсуждение участника',
                'af': u'Gebruikerbespreking',
                'als': u'Benutzer Diskussion',
                'ar': u'نقاش المستخدم',
                'ast': u'Usuariu discusión',
                'av': u'Обсуждение участника',
                'ay': u'Usuario Discusión',
                'ba': u'Обсуждение участника',
                'be': u'Гутаркі ўдзельніка',
                'bg': u'Потребител беседа',
                'bm': u'Discussion Utilisateur',
                'bn': u'ব্যবহারকারী আলাপ',
                'br': u'Kaozeadenn Implijer',
                'ca': u'Usuari Discussió',
                'ce': u'Обсуждение участника',
                'cs': u'Uživatel diskuse',
                'csb': u'Diskùsëjô brëkòwnika',
                'cv': u'Хутшăнаканăн канашлу страници',
                'cy': u'Sgwrs Defnyddiwr',
                'da': u'Bruger diskussion',
                'de': u'Benutzer Diskussion',
                'el': u'Συζήτηση χρήστη',
                'eo': u'Vikipediista diskuto',
                'es': u'Usuario Discusión',
                'et': u'Kasutaja arutelu',
                'eu': u'Lankide eztabaida',
                'fa': u'بحث کاربر',
                'fi': u'Keskustelu käyttäjästä',
                'fo': u'Brúkari kjak',
                'fr': u'Discussion Utilisateur',
                'fur': u'Discussion utent',
                'fy': u'Meidogger oerlis',
                'ga': u'Plé úsáideora',
                'gn': u'Usuario Discusión',
                'he': u'שיחת משתמש',
                'hi': u'सदस्य वार्ता',
                'hr': u'Razgovor sa suradnikom',
                'hu': u'User vita',
                'ia': u'Discussion Usator',
                'id': u'Bicara Pengguna',
                'is': u'Notandaspjall',
                'it': u'Discussioni utente',
                'ja': u'利用者‐会話',
                'ka': u'მომხმარებელი განხილვა',
                'ko': u'사용자토론',
                'ku': u'Bikarhêner nîqaş',
                'kv': u'Обсуждение участника',
                'la': u'Disputatio Usoris',
                'li': u'Euverlik gebroeker',
                'lt': u'Naudotojo aptarimas',
                'mk': u'Корисник разговор',
                'ms': u'Perbualan Pengguna',
                'nah': u'Usuario Discusión',
                'nap': u'Discussioni utente',
                'nds': u'Bruker Diskuschoon',
                'nl': u'Overleg gebruiker',
                'nn': u'Brukardiskusjon',
                'no': u'Brukerdiskusjon',
                'nv': u"Choinish'įįhí baa yinísht'į́",
                'oc': u'Discutida Utilisator',
                'os': u'Архайæджы дискусси',
                'pa': u'ਮੈਂਬਰ ਚਰਚਾ',
                'pl': u'Dyskusja Wikipedysty',
                'pt': u'Usuário Discussão',
                'qu': u'Usuario Discusión',
                'ro': u'Discuţie Utilizator',
                'ru': u'Обсуждение участника',
                'sc': u'Utente discussioni',
                'sk': u'Diskusia s redaktorom',
                'sl': u'Uporabniški pogovor',
                'sq': u'Përdoruesi diskutim',
                'sr': u'Разговор са корисником',
                'su': u'Obrolan pamaké',
                'sv': u'Användardiskussion',
                'ta': u'பயனர் பேச்சு',
                'th': u'คุยเกี่ยวกับผู้ใช้',
                'tr': u'Kullanıcı mesaj',
                'tt': u'Äğzä bäxäse',
                'ty': u'Discussion Utilisateur',
                'udm': u'Викиавтор сярысь вераськон',
                'uk': u'Обговорення користувача',
                'vec':u'Discussion utente',
                'vi': u'Thảo luận Thành viên',
                'wa': u'Uzeu copene',
                'yi': u'באַניצער רעדן',
            },
            4: {
                '_default': u'Project',
            },
            5: {
                '_default': u'Project talk',
            },
            6: {
                '_default': u'Image',
                'ab': u'Изображение',
                'af': u'Beeld',
                'als': u'Bild',
                'ar': u'صورة',
                'ast': u'Imaxen',
                'av': u'Изображение',
                'ay': u'Imagen',
                'ba': u'Изображение',
                'be': u'Выява',
                'bg': u'Картинка',
                'bn': u'চিত্র',
                'br': u'Skeudenn',
                'ca': u'Imatge',
                'cbs': u'Òbrôzk',
                'ce': u'Изображение',
                'cs': u'Soubor',
                'csb': u'Òbrôzk',
                'cv': u'Ӳкерчĕк',
                'cy': u'Delwedd',
                'da': u'Billede',
                'de': u'Bild',
                'el': u'Εικόνα',
                'eo': u'Dosiero',
                'es': u'Imagen',
                'et': u'Pilt',
                'eu': u'Irudi',
                'fa': u'تصویر',
                'fi': u'Kuva',
                'fo': u'Mynd',
                'fur': u'Figure',
                'fy': u'Ofbyld',
                'ga': u'Íomhá',
                'gn': u'Imagen',
                'he': u'תמונה',
                'hi': u'चित्र',
                'hr': u'Slika',
                'hu': u'Kép',
                'ia': u'Imagine',
                'id': u'Gambar',
                'is': u'Mynd',
                'it': u'Immagine',
                'ja': u'画像',
                'ka': u'სურათი',
                'ko': u'그림',
                'ku': u'Wêne',
                'kv': u'Изображение',
                'la': u'Imago',
                'li': u'Aafbeilding',
                'lt': u'Vaizdas',
                'mk': u'Слика',
                'ms': u'Imej',
                'nah': u'Imagen',
                'nap': u'Immagine',
                'nds': u'Bild',
                'nl': u'Afbeelding',
                'nn': u'Fil',
                'no': u'Bilde',
                'nv': u"E'elyaaígíí",
                'oc': u'Imatge',
                'os': u'Ныв',
                'pa': u'ਤਸਵੀਰ',
                'pl': u'Grafika',
                'pt': u'Imagem',
                'qu': u'Imagen',
                'ro': u'Imagine',
                'ru': u'Изображение',
                'sc': u'Immàgini',
                'sk': u'Obrázok',
                'sl': u'Slika',
                'sq': u'Figura',
                'sr': u'Слика',
                'su': u'Gambar',
                'sv': u'Bild',
                'ta': u'படிமம்',
                'th': u'ภาพ',
                'tr': u'Resim',
                'tt': u'Räsem',
                'udm': u'Суред',
                'uk': u'Зображення',
                'vec':u'Imagine',
                'vi': u'Hình',
                'wa': u'Imådje',
                'yi': u'בילד',
            },
            7: {
                '_default': u'Image talk',
                'ab': u'Обсуждение изображения',
                'af': u'Beeldbespreking',
                'als': u'Bild Diskussion',
                'ar': u'نقاش الصورة',
                'ast': u'Imaxen discusión',
                'av': u'Обсуждение изображения',
                'ay': u'Imagen Discusión',
                'ba': u'Обсуждение изображения',
                'be': u'Абмеркаваньне выявы',
                'bg': u'Картинка беседа',
                'bm': u'Discussion Image',
                'bn': u'চিত্র আলাপ',
                'br': u'Kaozeadenn Skeudenn',
                'ca': u'Imatge Discussió',
                'ce': u'Обсуждение изображения',
                'cs': u'Soubor diskuse',
                'csb': u'Diskùsëjô òbrôzków',
                'cv': u'Ӳкерчĕке сӳтсе явмалли',
                'cy': u'Sgwrs Delwedd',
                'da': u'Billede diskussion',
                'de': u'Bild Diskussion',
                'el': u'Συζήτηση εικόνας',
                'eo': u'Dosiera diskuto',
                'es': u'Imagen Discusión',
                'et': u'Pildi arutelu',
                'eu': u'Irudi eztabaida',
                'fa': u'بحث تصویر',
                'fi': u'Keskustelu kuvasta',
                'fo': u'Mynd kjak',
                'fr': u'Discussion Image',
                'fur': u'Discussion figure',
                'fy': u'Ofbyld oerlis',
                'ga': u'Plé íomhá',
                'gn': u'Imagen Discusión',
                'he': u'שיחת תמונה',
                'hi': u'चित्र वार्ता',
                'hr': u'Razgovor o slici',
                'hu': u'Kép vita',
                'ia': u'Discussion Imagine',
                'id': u'Pembicaraan Gambar',
                'is': u'Myndaspjall',
                'it': u'Discussioni immagine',
                'ja': u'画像‐ノート',
                'ka': u'სურათი განხილვა',
                'ko': u'그림토론',
                'ku': u'Wêne nîqaş',
                'kv': u'Обсуждение изображения',
                'la': u'Disputatio Imaginis',
                'li': u'Euverlik afbeelding',
                'lt': u'Vaizdo aptarimas',
                'mk': u'Слика разговор',
                'ms': u'Imej Perbualan',
                'nah': u'Imagen Discusión',
                'nap': u'Discussioni immagine',
                'nds': u'Bild Diskuschoon',
                'nl': u'Overleg afbeelding',
                'nn': u'Fildiskusjon',
                'no': u'Bildediskusjon',
                'nv': u"E'elyaaígíí baa yinísht'į́",
                'oc': u'Discutida Imatge',
                'os': u'Нывы тыххæй дискусси',
                'pa': u'ਤਸਵੀਰ ਚਰਚਾ',
                'pl': u'Dyskusja grafiki',
                'pt': u'Imagem Discussão',
                'qu': u'Imagen Discusión',
                'ro': u'Discuţie Imagine',
                'ru': u'Обсуждение изображения',
                'sc': u'Immàgini contièndha',
                'sk': u'Diskusia k obrázku',
                'sl': u'Pogovor k sliki',
                'sq': u'Figura diskutim',
                'sr': u'Разговор о слици',
                'su': u'Obrolan gambar',
                'sv': u'Bilddiskussion',
                'ta': u'படிமப் பேச்சு',
                'th': u'คุยเกี่ยวกับภาพ',
                'tr': u'Resim tartışma',
                'tt': u'Räsem bäxäse',
                'ty': u'Discussion Image',
                'udm': u'Суред сярысь вераськон',
                'uk': u'Обговорення зображення',
                'vec':u'Discussion imagine',
                'vi': u'Thảo luận Hình',
                'wa': u'Imådje copene',
                'yi': u'בילד רעדן',
            },
            8: {
                '_default': u'MediaWiki',
                'ar': u'ميدياويكي',
                'bg': u'МедияУики',
                'fa': u'مدیاویکی',
                'fo': u'MidiaWiki',
                'is': u'Melding',
                'ka': u'მედიავიკი',
                'mk': u'МедијаВики',
                'oc': u'Mediaòiqui',
                'pa': u'ਮੀਡੀਆਵਿਕਿ',
                'sr': u'МедијаВики',
                'ta': u'மீடியாவிக்கி',
                'tr': u'MedyaViki',
                'yi': u'מעדיעװיקי',
            },
            9: {
                '_default': u'MediaWiki talk',
                'ab': u'Обсуждение MediaWiki',
                'af': u'MediaWikibespreking',
                'als': u'MediaWiki Diskussion',
                'ar': u'نقاش ميدياويكي',
                'ast': u'MediaWiki discusión',
                'av': u'Обсуждение MediaWiki',
                'ay': u'MediaWiki Discusión',
                'ba': u'Обсуждение MediaWiki',
                'be': u'Абмеркаваньне MediaWiki',
                'bg': u'МедияУики беседа',
                'bm': u'Discussion MediaWiki',
                'bn': u'MediaWik i আলাপ',
                'br': u'Kaozeadenn MediaWiki',
                'ca': u'MediaWiki Discussió',
                'ce': u'Обсуждение MediaWiki',
                'cs': u'MediaWiki diskuse',
                'csb': u'Diskùsëjô MediaWiki',
                'cv': u'MediaWiki сӳтсе явмалли',
                'cy': u'Sgwrs MediaWiki',
                'da': u'MediaWiki diskussion',
                'de': u'MediaWiki Diskussion',
                'eo': u'MediaWiki diskuto',
                'es': u'MediaWiki Discusión',
                'et': u'MediaWiki arutelu',
                'eu': u'MediaWiki eztabaida',
                'fa': u'بحث مدیاویکی',
                'fo': u'MidiaWiki kjak',
                'fr': u'Discussion MediaWiki',
                'fur': u'Discussion MediaWiki',
                'fy': u'MediaWiki oerlis',
                'ga': u'Plé MediaWiki',
                'gn': u'MediaWiki Discusión',
                'he': u'שיחת MediaWiki',
                'hr': u'MediaWiki razgovor',
                'hu': u'MediaWiki vita',
                'ia': u'Discussion MediaWiki',
                'id': u'Pembicaraan MediaWiki',
                'is': u'Meldingarspjall',
                'it': u'Discussioni MediaWiki',
                'ja': u'MediaWiki‐ノート',
                'ka': u'მედიავიკი განხილვა',
                'ku': u'MediaWiki nîqaş',
                'kv': u'Обсуждение MediaWiki',
                'la': u'Disputatio MediaWiki',
                'li': u'Euverlik MediaWiki',
                'lt': u'MediaWiki aptarimas',
                'mk': u'МедијаВики разговор',
                'ms': u'MediaWiki Perbualan',
                'nah': u'MediaWiki Discusión',
                'nap': u'Discussioni MediaWiki',
                'nds': u'MediaWiki Diskuschoon',
                'nl': u'Overleg MediaWiki',
                'nn': u'MediaWiki-diskusjon',
                'no': u'MediaWiki-diskusjon',
                'nv': u"MediaWiki baa yinísht'į́",
                'oc': u'Discutida Mediaòiqui',
                'os': u'Дискусси MediaWiki',
                'pa': u'ਮੀਡੀਆਵਿਕਿ ਚਰਚਾ',
                'pl': u'Dyskusja MediaWiki',
                'pt': u'MediaWiki Discussão',
                'qu': u'MediaWiki Discusión',
                'ro': u'Discuţie MediaWiki',
                'ru': u'Обсуждение MediaWiki',
                'sk': u'Diskusia k MediaWiki',
                'sq': u'MediaWiki diskutim',
                'sr': u'Разговор о МедијаВикију',
                'su': u'Obrolan MediaWiki',
                'sv': u'MediaWiki diskussion',
                'ta': u'மீடியாவிக்கி பேச்சு',
                'th': u'คุยเกี่ยวกับ MediaWiki',
                'tr': u'MedyaViki tartışma',
                'tt': u'MediaWiki bäxäse',
                'ty': u'Discussion MediaWiki',
                'udm': u'MediaWiki сярысь вераськон',
                'uk': u'Обговорення MediaWiki',
                'vec':u'Discussion MediaWiki',
                'vi': u'Thảo luận MediaWiki',
                'wa': u'MediaWiki copene',
                'yi': u'מעדיעװיקי רעדן',
            },
            10: {
                '_default':u'Template',
                'ab': u'Шаблон',
                'af': u'Sjabloon',
                'als': u'Vorlage',
                'ar': u'قالب',
                'ast': u'Plantilla',
                'av': u'Шаблон',
                'ay': u'Plantilla',
                'ba': u'Шаблон',
                'be': u'Шаблён',
                'bg': u'Шаблон',
                'bm': u'Modèle',
                'br': u'Patrom',
                'cbs': u'Szablóna',
                'ce': u'Шаблон',
                'cs': u'Šablona',
                'csb': u'Szablóna',
                'cv': u'Шаблон',
                'cy': u'Nodyn',
                'da': u'Skabelon',
                'de': u'Vorlage',
                'el': u'Πρότυπο',
                'eo': u'Ŝablono',
                'es': u'Plantilla',
                'et': u'Mall',
                'eu': u'Txantiloi',
                'fa': u'الگو',
                'fi': u'Malline',
                'fo': u'Fyrimynd',
                'fr': u'Modèle',
                'fur': u'Model',
                'fy': u'Berjocht',
                'ga': u'Teimpléad',
                'gn': u'Plantilla',
                'he': u'תבנית',
                'hr': u'Predložak',
                'hu': u'Sablon',
                'id': u'Templat',
                'is': u'Snið',
                'ka': u'თარგი',
                'ku': u'Şablon',
                'kv': u'Шаблон',
                'la': u'Formula',
                'li': u'Sjabloon',
                'lt': u'Šablonas',
                'mk': u'Шаблон',
                'ms': u'Templat',
                'nah': u'Plantilla',
                'nds': u'Vörlaag',
                'nl': u'Sjabloon',
                'nn': u'Mal',
                'no': u'Mal',
                'oc': u'Modèl',
                'os': u'Шаблон',
                'pa': u'ਨਮੂਨਾ',
                'pl': u'Szablon',
                'pt': u'Predefinição',
                'qu': u'Plantilla',
                'ro': u'Format',
                'ru': u'Шаблон',
                'sk': u'Šablóna',
                'sl': u'Predloga',
                'sq': u'Stampa',
                'sr': u'Шаблон',
                'su': u'Citakan',
                'sv': u'Mall',
                'ta': u'வார்ப்புரு',
                'tr': u'Şablon',
                'tt': u'Ürnäk',
                'ty': u'Modèle',
                'udm': u'Шаблон',
                'uk': u'Шаблон',
                'vi': u'Tiêu bản',
                'wa': u'Modele',
                'yi': u'מוסטער',
            },
            11: {
                '_default': u'Template talk',
                'ab': u'Обсуждение шаблона',
                'af': u'Sjabloonbespreking',
                'als': u'Vorlage Diskussion',
                'ar': u'نقاش قالب',
                'ast': u'Plantilla discusión',
                'av': u'Обсуждение шаблона',
                'ay': u'Plantilla Discusión',
                'ba': u'Обсуждение шаблона',
                'be': u'Абмеркаваньне шаблёну',
                'bg': u'Шаблон беседа',
                'bm': u'Discussion Modèle',
                'br': u'Kaozeadenn Patrom',
                'ca': u'Template Discussió',
                'ce': u'Обсуждение шаблона',
                'cs': u'Šablona diskuse',
                'csb': u'Diskùsëjô Szablónë',
                'cv': u'Шаблона сӳтсе явмалли',
                'cy': u'Sgwrs Nodyn',
                'da': u'Skabelon diskussion',
                'de': u'Vorlage Diskussion',
                'el': u'Συζήτηση προτύπου',
                'eo': u'Ŝablona diskuto',
                'es': u'Plantilla Discusión',
                'et': u'Malli arutelu',
                'eu': u'Txantiloi eztabaida',
                'fa': u'بحث الگو',
                'fi': u'Keskustelu mallineesta',
                'fo': u'Fyrimynd kjak',
                'fr': u'Discussion Modèle',
                'fur': u'Discussion model',
                'fy': u'Berjocht oerlis',
                'ga': u'Plé teimpléid',
                'gn': u'Plantilla Discusión',
                'he': u'שיחת תבנית',
                'hr': u'Razgovor o predlošku',
                'hu': u'Sablon vita',
                'id': u'Pembicaraan Templat',
                'is': u'Sniðaspjall',
                'it': u'Discussioni template',
                'ja': u'Template‐ノート',
                'ka': u'თარგი განხილვა',
                'ku': u'Şablon nîqaş',
                'kv': u'Обсуждение шаблона',
                'la': u'Disputatio Formulae',
                'li': u'Euverlik sjabloon',
                'lt': u'Šablono aptarimas',
                'mk': u'Шаблон разговор',
                'ms': u'Perbualan Templat',
                'nah': u'Plantilla Discusión',
                'nap': u'Discussioni template',
                'nds': u'Vörlaag Diskuschoon',
                'nl': u'Overleg sjabloon',
                'nn': u'Maldiskusjon',
                'no': u'Maldiskusjon',
                'oc': u'Discutida Modèl',
                'os': u'Шаблоны тыххæй дискусси',
                'pa': u'ਨਮੂਨਾ ਚਰਚਾ',
                'pl': u'Dyskusja szablonu',
                'pt': u'Predefinição Discussão',
                'qu': u'Plantilla Discusión',
                'ro': u'Discuţie Format',
                'ru': u'Обсуждение шаблона',
                'sk': u'Diskusia k šablóne',
                'sl': u'Pogovor k predlogi',
                'sq': u'Stampa diskutim',
                'sr': u'Разговор о шаблону',
                'su': u'Obrolan citakan',
                'sv': u'Malldiskussion',
                'ta': u'வார்ப்புரு பேச்சு',
                'tr': u'Şablon tartışma',
                'tt': u'Ürnäk bäxäse',
                'ty': u'Discussion Modèle',
                'udm': u'Шаблон сярысь вераськон',
                'uk': u'Обговорення шаблону',
                'vec':u'Discussion template',
                'vi': u'Thảo luận Tiêu bản',
                'wa': u'Modele copene',
                'yi': u'מוסטער רעדן',
            },
            12: {
                '_default': u'Help',
                'ab': u'Справка',
                'af': u'Hulp',
                'als': u'Hilfe',
                'ar': u'مساعدة',
                'ast': u'Ayuda',
                'av': u'Справка',
                'ay': u'Ayuda',
                'ba': u'Справка',
                'be': u'Дапамога',
                'bg': u'Помощ',
                'bm': u'Aide',
                'br': u'Skoazell',
                'ca': u'Ajuda',
                'cbs': u'Pòmòc',
                'ce': u'Справка',
                'cs': u'Nápověda',
                'csb': u'Pòmòc',
                'cv': u'Пулăшу',
                'da': u'Hjælp',
                'de': u'Hilfe',
                'el': u'Βοήθεια',
                'eo': u'Helpo',
                'es': u'Ayuda',
                'et': u'Juhend',
                'fa': u'راهنما',
                'fi': u'Ohje',
                'fo': u'Hjálp',
                'fr': u'Aide',
                'fur': u'Jutori',
                'fy': u'Hulp',
                'ga': u'Cabhair',
                'gn': u'Ayuda',
                'he': u'עזרה',
                'hr': u'Pomoć',
                'hu': u'Segítség',
                'id': u'Bantuan',
                'is': u'Hjálp',
                'it': u'Aiuto',
                'ka': u'დახმარება',
                'ko': u'도움말',
                'ku': u'Alîkarî',
                'kv': u'Справка',
                'la': u'Auxilium',
                'lt': u'Pagalba',
                'mk': u'Помош',
                'ms': u'Bantuan',
                'nah': u'Ayuda',
                'nap': u'Aiuto',
                'nds': u'Hülp',
                'nn': u'Hjelp',
                'no': u'Hjelp',
                'nv': u"Aná'álwo'",
                'oc': u'Ajuda',
                'os': u'Æххуыс',
                'pa': u'ਮਦਦ',
                'pl': u'Pomoc',
                'pt': u'Ajuda',
                'qu': u'Ayuda',
                'ro': u'Ajutor',
                'ru': u'Справка',
                'sk': u'Pomoc',
                'sq': u'Ndihmë',
                'sr': u'Помоћ',
                'su': u'Pitulung',
                'sv': u'Hjälp',
                'ta': u'உதவி',
                'tr': u'Yardım',
                'tt': u'Yärdäm',
                'ty': u'Aide',
                'udm': u'Валэктон',
                'uk': u'Довідка',
                'vec':u'Aiuto',
                'vi': u'Trợ giúp',
                'wa': u'Aidance',
                'yi': u'הילף',
            },
            13: {
                '_default': u'Help talk',
                'ab': u'Обсуждение справки',
                'af': u'Hulpbespreking',
                'als': u'Hilfe Diskussion',
                'ar': u'نقاش المساعدة',
                'ast': u'Ayuda discusión',
                'av': u'Обсуждение справки',
                'ay': u'Ayuda Discusión',
                'ba': u'Обсуждение справки',
                'be': u'Абмеркаваньне дапамогі',
                'bg': u'Помощ беседа',
                'bm': u'Discussion Aide',
                'br': u'Kaozeadenn Skoazell',
                'ca': u'Ajuda Discussió',
                'ce': u'Обсуждение справки',
                'cs': u'Nápověda diskuse',
                'csb': u'Diskùsëjô Pòmòcë',
                'cv': u'Пулăшăва сӳтсе явмалли',
                'da': u'Hjælp diskussion',
                'de': u'Hilfe Diskussion',
                'el': u'Συζήτηση βοήθειας',
                'eo': u'Helpa diskuto',
                'es': u'Ayuda Discusión',
                'et': u'Juhendi arutelu',
                'fa': u'بحث راهنما',
                'fi': u'Keskustelu ohjeesta',
                'fo': u'Hjálp kjak',
                'fr': u'Discussion Aide',
                'fur': u'Discussion jutori',
                'fy': u'Hulp oerlis',
                'ga': u'Plé cabhrach',
                'gn': u'Ayuda Discusión',
                'he': u'שיחת עזרה',
                'hr': u'Razgovor o pomoći',
                'hu': u'Segítség vita',
                'id': u'Pembicaraan Bantuan',
                'is': u'Hjálparspjall',
                'it': u'Discussioni aiuto',
                'ja': u'Help‐ノート',
                'ka': u'დახმარება განხილვა',
                'ko': u'도움말토론',
                'ku': u'Alîkarî nîqaş',
                'kv': u'Обсуждение справки',
                'la': u'Disputatio Auxilii',
                'li': u'Euverlik help',
                'lt': u'Pagalbos aptarimas',
                'mk': u'Помош разговор',
                'ms': u'Perbualan Bantuan',
                'nah': u'Ayuda Discusión',
                'nap': u'Discussioni aiuto',
                'nds': u'Hülp Diskuschoon',
                'nl': u'Overleg help',
                'nn': u'Hjelpdiskusjon',
                'no': u'Hjelpdiskusjon',
                'nv': u"Aná'álwo' baa yinísht'į́",
                'oc': u'Discutida Ajuda',
                'os': u'Æххуысы тыххæй дискусси',
                'pa': u'ਮਦਦ ਚਰਚਾ',
                'pl': u'Dyskusja pomocy',
                'pt': u'Ajuda Discussão',
                'qu': u'Ayuda Discusión',
                'ro': u'Discuţie Ajutor',
                'ru': u'Обсуждение справки',
                'sk': u'Diskusia k pomoci',
                'sq': u'Ndihmë diskutim',
                'sr': u'Разговор о помоћи',
                'su': u'Obrolan pitulung',
                'sv': u'Hjälp diskussion',
                'ta': u'உதவி பேச்சு',
                'tr': u'Yardım tartışma',
                'tt': u'Yärdäm bäxäse',
                'ty': u'Discussion Aide',
                'udm': u'Валэктон сярысь вераськон',
                'uk': u'Обговорення довідки',
                'vec':u'Discussion aiuto',
                'vi': u'Thảo luận Trợ giúp',
                'wa': u'Aidance copene',
                'yi': u'הילף רעדן',
            },
            14: {
                '_default': u'Category',
                'ab': u'Категория',
                'af': u'Kategorie',
                'als': u'Kategorie',
                'ar': u'تصنيف',
                'ast': u'Categoría',
                'av': u'Категория',
                'ay': u'Categoría',
                'ba': u'Категория',
                'be': u'Катэгорыя',
                'bg': u'Категория',
                'bm': u'Catégorie',
                'br': u'Rummad',
                'ca': u'Categoria',
                'ce': u'Категория',
                'cs': u'Kategorie',
                'csb': u'Kategòrëjô',
                'cv': u'Категори',
                'da': u'Kategori',
                'de': u'Kategorie',
                'el': u'Κατηγορία',
                'eo': u'Kategorio',
                'es': u'Categoría',
                'et': u'Kategooria',
                'eu': u'Kategoria',
                'fa': u'رده',
                'fi': u'Luokka',
                'fo': u'Bólkur',
                'fr': u'Catégorie',
                'fur': u'Categorie',
                'fy': u'Kategory',
                'ga': u'Catagóir',
                'gn': u'Categoría',
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
                'kv': u'Категория',
                'la': u'Categoria',
                'li': u'Kategorie',
                'lt': u'Kategorija',
                'mk': u'Категорија',
                'ms': u'Kategori',
                'nah': u'Categoría',
                'nap': u'Categoria',
                'nds': u'Kategorie',
                'nl': u'Categorie',
                'nn': u'Kategori',
                'no': u'Kategori',
                'nv': u"T'ááłáhági át'éego",
                'oc': u'Categoria',
                'os': u'Категори',
                'pa': u'ਸ਼੍ਰੇਣੀ',
                'pl': u'Kategoria',
                'pt': u'Categoria',
                'qu': u'Categoría',
                'ro': u'Categorie',
                'ru': u'Категория',
                'sk': u'Kategória',
                'sl': u'Kategorija',
                'sr': u'Категорија',
                'su': u'Kategori',
                'sv': u'Kategori',
                'ta': u'பகுப்பு',
                'tr': u'Kategori',
                'tt': u'Törkem',
                'ty': u'Catégorie',
                'udm': u'Категория',
                'uk': u'Категорія',
                'vec':u'Categoria',
                'vi': u'Thể loại',
                'wa': u'Categoreye',
                'yi': u'קאַטעגאָריע',
                },

            15: {
                '_default': u'Category talk',
                'ab': u'Обсуждение категории',
                'af': u'Kategoriebespreking',
                'als': u'Kategorie Diskussion',
                'ar': u'نقاش التصنيف',
                'ast': u'Categoría discusión',
                'av': u'Обсуждение категории',
                'ay': u'Categoría Discusión',
                'ba': u'Обсуждение категории',
                'be': u'Абмеркаваньне катэгорыі',
                'bg': u'Категория беседа',
                'bm': u'Discussion Catégorie',
                'br': u'Kaozeadenn Rummad',
                'ca': u'Categoria Discussió',
                'ce': u'Обсуждение категории',
                'cs': u'Kategorie diskuse',
                'csb': u'Diskùsëjô Kategòrëji',
                'cv': u'Категорине сӳтсе явмалли',
                'da': u'Kategori diskussion',
                'de': u'Kategorie Diskussion',
                'el': u'Συζήτηση κατηγορίας',
                'eo': u'Kategoria diskuto',
                'es': u'Categoría Discusión',
                'et': u'Kategooria arutelu',
                'eu': u'Kategoria eztabaida',
                'fa': u'بحث رده',
                'fi': u'Keskustelu luokasta',
                'fo': u'Bólkur kjak',
                'fr': u'Discussion Catégorie',
                'fur': u'Discussion categorie',
                'fy': u'Kategory oerlis',
                'ga': u'Plé catagóire',
                'gn': u'Categoría Discusión',
                'he': u'שיחת קטגוריה',
                'hi': u'श्रेणी वार्ता',
                'hr': u'Razgovor o kategoriji',
                'hu': u'Kategória vita',
                'id': u'Pembicaraan Kategori',
                'is': u'Flokkaspjall',
                'it': u'Discussioni categoria',
                'ja': u'Category‐ノート',
                'ka': u'კატეგორია განხილვა',
                'ko': u'분류토론',
                'ku': u'Kategorî nîqaş',
                'kv': u'Обсуждение категории',
                'la': u'Disputatio Categoriae',
                'li': u'Euverlik kategorie',
                'lt': u'Kategorijos aptarimas',
                'mk': u'Категорија разговор',
                'ms': u'Perbualan Kategori',
                'nah': u'Categoría Discusión',
                'nap': u'Discussioni categoria',
                'nds': u'Kategorie Diskuschoon',
                'nl': u'Overleg categorie',
                'nn': u'Kategoridiskusjon',
                'no': u'Kategoridiskusjon',
                'nv': u"T'ááłáhági át'éego baa yinísht'į́",
                'oc': u'Discutida Categoria',
                'os': u'Категорийы тыххæй дискусси',
                'pa': u'ਸ਼੍ਰੇਣੀ ਚਰਚਾ',
                'pl': u'Dyskusja kategorii',
                'pt': u'Categoria Discussão',
                'qu': u'Categoría Discusión',
                'ro': u'Discuţie Categorie',
                'ru': u'Обсуждение категории',
                'sk': u'Diskusia ku kategórii',
                'sl': u'Pogovor k kategoriji',
                'sr': u'Разговор о категорији',
                'su': u'Obrolan kategori',
                'sv': u'Kategoridiskussion',
                'ta': u'பகுப்பு பேச்சு',
                'tlh': u"Segh ja'chuq",
                'tr': u'Kategori tartışma',
                'tt': u'Törkem bäxäse',
                'ty': u'Discussion Catégorie',
                'udm': u'Категория сярысь вераськон',
                'uk': u'Обговорення категорії',
                'vec':u'Discussion categoria',
                'vi': u'Thảo luận Thể loại',
                'wa': u'Categoreye copene',
                'yi': u'קאַטעגאָריע רעדן',
                },
        }
        
        # A list of disambiguation template names in different languages
        self.disambiguationTemplates = {
            '_default': []
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
        if self.disambiguationTemplates.has_key(code):
            return self.disambiguationTemplates[code]
        elif fallback:
            return self.disambiguationTemplates[fallback]
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
