# -*- coding: utf-8  -*-
import family, config

# The wikitravel family

# Translation used on all wikitravels for the 'article' text.
# A language not mentioned here is not known by the robot

__version__ = '$Id$'

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'wikitravel'
        self.langs = {
            'ar':'ar',
            'ca':'ca',
            'de':'de',
            'en':'en',
            'eo':'eo',
            'es':'es',
            'fi':'fi',
            'fr':'fr',
            'he':'he',
            'hi':'hi',
            'hu':'hu',
            'it':'it',
            'ja':'ja',
            'nl':'nl',
            'pl':'pl',
            'pt':'pt',
            'ro':'ro',
            'ru':'ru',
            'sv':'sv',
            'zh':'zh',
            'wts':'wts',
        }
        self.namespaces[-2] = {
            '_default': [u'Media', self.namespaces[-2]['_default']],
            'ar': u'ملف',
            'ca': u'Media',
            'de': u'Media',
            'en': u'Media',
            'eo': u'Media',
            'es': u'Media',
            'fi': u'Media',
            'fr': u'Media',
            'he': u'מדיה',
            'hi': u'Media',
            'hu': u'Média',
            'it': u'Media',
            'ja': u'Media',
            'nl': u'Media',
            'pl': u'Media',
            'pt': u'Media',
            'ro': u'Media',
            'ru': u'Медиа',
            'sv': u'Media',
            'zh': u'Media',
            'wts': u'Media',
        }
        self.namespaces[-1] = {
            '_default': [u'Special', self.namespaces[-1]['_default']],
            'ar': u'خاص',
            'ca': u'Especial',
            'de': u'Spezial',
            'en': u'Special',
            'eo': u'Speciala',
            'es': u'Especial',
            'fi': u'Toiminnot',
            'fr': u'Special',
            'he': u'מיוחד',
            'hi': u'विशेष',
            'hu': u'Speciális',
            'it': u'Speciale',
            'ja': u'特別',
            'nl': u'Speciaal',
            'pl': u'Specjalna',
            'pt': u'Especial',
            'ro': u'Special',
            'ru': u'Служебная',
            'sv': u'Special',
            'zh': u'Special',
            'wts': u'Special',
        }
        self.namespaces[1] = {
            '_default': u'Talk',
            'ar': u'نقاش',
            'ca': u'Discussió',
            'de': u'Diskussion',
            'en': u'Talk',            
            'eo': u'Diskuto',
            'es': u'Discusión',
            'fi': u'Keskustelu',
            'fr': u'Discuter',
            'he': u'שיחה',
            'hi': u'वार्ता',
            'hu': u'Vita',            
            'it': u'Discussione',
            'ja': u'ノート',
            'nl': u'Overleg',
            'pl': u'Dyskusja',
            'pt': u'Discussão',
            'ro': u'Discuţie',
            'ru': u'Обсуждение',
            'sv': u'Diskussion',
            'zh': u'Talk',
            'wts': u'Talk',
        }
        self.namespaces[2] = {
            '_default': u'User',
            'ar': u'مستخدم',
            'ca': u'Usuari',
            'de': u'Benutzer',
            'en': u'User',
            'eo': u'Vikipediisto',
            'es': u'Usuario',
            'fi': u'Käyttäjä',
            'fr': u'Utilisateur',
            'he': u'משתמש',
            'hi': u'सदस्य',
            'hu': u'User',
            'it': u'Utente',
            'ja': u'利用者',
            'nl': u'Gebruiker',
            'pl': u'Użytkownik',
            'pt': u'Usuário',
            'ro': u'Utilizator',
            'ru': u'Участник',
            'sv': u'Användare',
            'zh': u'User',
            'wts': u'User',
        }
        self.namespaces[3] = {
            '_default': u'User talk',
            'ar': u'نقاش المستخدم',
            'ca': u'Usuari Discussió',
            'de': u'Benutzer Diskussion',
            'en': u'User talk',
            'eo': u'Vikipediista diskuto',
            'es': u'Usuario Discusión',
            'fi': u'Keskustelu käyttäjästä',
            'fr': u'Discussion Utilisateur',
            'he': u'שיחת משתמש',
            'hi': u'सदस्य वार्ता',
            'hu': u'User vita',
            'it': u'Discussioni utente',
            'ja': u'利用者‐会話',
            'nl': u'Overleg gebruiker',
            'pl': u'Dyskusja użytkownika',
            'pt': u'Usuário Discussão',
            'ro': u'Discuţie Utilizator',
            'ru': u'Обсуждение участника',
            'sv': u'Användardiskussion',
            'zh': u'User talk',
            'wts': u'User talk',
        }
        self.namespaces[4] = {
            '_default': [u'Wikitravel', self.namespaces[4]['_default']],
            'ar': u'Wikitravel',
            'ca': u'Wikitravel',
            'de': u'Wikitravel',
            'en': u'Wikitravel',
            'eo': u'Wikitravel',
            'es': u'Wikitravel',
            'fi': u'Wikitravel',
            'fr': u'Wikitravel',
            'he': u'ויקיטיול',
            'hi': u'विकिट्रैवल',
            'hu': u'Wikitravel',
            'it': u'Wikitravel',
            'ja': u'Wikitravel',
            'nl': u'Wikitravel',
            'pl': u'Wikitravel',
            'pt': u'Wikitravel',
            'ro': u'Wikitravel',
            'ru': u'Wikitravel',
            'sv': u'Wikitravel',
            'zh': u'Wikitravel',
            'wts': u'Wikitravel Shared',
        }
        self.namespaces[5] = {
            '_default': [u'Wikitravel talk', self.namespaces[5]['_default']],
            'ar': u'نقاش Wikitravel',
            'ca': u'Wikitravel Discussió',
            'de': u'Wikitravel Diskussion',
            'en': u'Wikitravel talk',
            'eo': u'Wikitravel diskuto',
            'es': u'Wikitravel Discusión',
            'fr': u'Discussion Wikitravel',
            'fi': u'Keskustelu Wikitravelista',
            'he': u'שיחת ויקיטיול',
            'hi': u'विकिट्रैवल वार्ता',
            'hu': u'Wikitravel vita',
            'it': u'Discussioni Wikitravel',
            'ja': u'Wikitravel‐ノート',
            'nl': u'Overleg Wikitravel',
            'pl': u'Dyskusja Wikitravel',
            'pt': u'Wikitravel Discussão',
            'ro': u'Discuţie Wikitravel',
            'ru': u'Обсуждение Wikitravel',
            'sv': u'Wikitraveldiskussion',
            'zh': u'Wikitravel talk',
            'wts': u'Wikitravel Shared talk',
        }
        self.namespaces[6] = {
            '_default': u'Image',
            'ar': u'صورة',
            'ca': u'Imatge',
            'de': u'Bild',
            'en': u'Image',            
            'eo': u'Dosiero',
            'es': u'Imagen',
            'fi': u'Kuva',
            'fr': u'Image',
            'he': u'תמונה',
            'hi': u'चित्र',
            'hu': u'Kép',
            'it': u'Immagine',
            'ja': u'画像',
            'nl': u'Afbeelding',
            'pl': u'Grafika',
            'pt': u'Imagem',
            'ro': u'Imagine',
            'ru': u'Изображение',
            'sv': u'Bild',
            'zh': u'Image',
            'wts': u'Image',
        }
        self.namespaces[7] = {
            '_default': [u'Image talk', self.namespaces[7]['_default']],
            'ar': u'نقاش الصورة',
            'ca': u'Imatge Discussió',
            'de': u'Bild Diskussion',
            'en': u'Image talk',
            'eo': u'Dosiera diskuto',
            'es': u'Imagen Discusión',
            'fi': u'Keskustelu kuvasta',
            'fr': u'Discussion Image',
            'he': u'שיחת תמונה',
            'hi': u'चित्र वार्ता',
            'hu': u'Kép vita',
            'it': u'Discussioni immagine',
            'ja': u'画像‐ノート',
            'nl': u'Overleg afbeelding',
            'pl': u'Dyskusja grafiki',
            'pt': u'Imagem Discussão',
            'ro': u'Discuţie Imagine',
            'ru': u'Обсуждение изображения',
            'sv': u'Bilddiskussion',
            'zh': u'Image talk',
            'wts': u'Image talk',
        }
        self.namespaces[8] = {
            '_default': [u'MediaWiki', self.namespaces[8]['_default']],
            'ar': u'ميدياويكي',
            'ca': u'MediaWiki',
            'de': u'MediaWiki',
            'en': u'MediaWiki',
            'eo': u'MediaWiki',
            'es': u'MediaWiki',
            'fi': u'Järjestelmäviesti',
            'fr': u'MediaWiki',
            'he': u'מדיה ויקי',
            'hi': u'MediaWiki',
            'hu': u'MediaWiki',
            'it': u'MediaWiki',
            'ja': u'MediaWiki',
            'nl': u'MediaWiki',
            'pl': u'MediaWiki',
            'pt': u'MediaWiki',
            'ro': u'MediaWiki',
            'ru': u'MediaWiki',
            'sv': u'MediaWiki',
            'zh': u'MediaWiki',
            'wts': u'MediaWiki',
        }
        self.namespaces[9] = {
            '_default': [u'MediaWiki talk', self.namespaces[9]['_default']],
            'ar': u'نقاش ميدياويكي',
            'ca': u'MediaWiki Discussió',
            'de': u'MediaWiki Diskussion',
            'en': u'MediaWiki talk',
            'eo': u'MediaWiki diskuto',
            'es': u'MediaWiki Discusión',
            'fi': u'Keskustelu järjestelmäviestistä',
            'fr': u'Discussion MediaWiki',
            'he': u'שיחת מדיה ויקי',
            'hi': u'MediaWiki talk',
            'hu': u'MediaWiki vita',
            'it': u'Discussioni MediaWiki',
            'ja': u'MediaWiki‐ノート',
            'nl': u'Overleg MediaWiki',
            'pl': u'Dyskusja MediaWiki',
            'pt': u'MediaWiki Discussão',
            'ro': u'Discuţie MediaWiki',
            'ru': u'Обсуждение MediaWiki',
            'sv': u'MediaWiki-diskussion',
            'zh': u'MediaWiki talk',
            'wts': u'MediaWiki talk',
        }
        self.namespaces[10] = {
            '_default': [u'Template', self.namespaces[10]['_default']],
            'ar': u'قالب',
            'ca': u'Plantilla',
            'de': u'Vorlage',
            'en': u'Template',
            'eo': u'Ŝablono',
            'es': u'Plantilla',
            'fi': u'Malline',
            'fr': u'Modèle',
            'he': u'תבנית',
            'hi': u'साँचा',
            'hu': u'Sablon',
            'it': u'Template',
            'ja': u'Template',
            'nl': u'Sjabloon',
            'pl': u'Szablon',
            'pt': u'Predefinição',
            'ro': u'Format',
            'ru': u'Шаблон',
            'sv': u'Mall',
            'zh': u'Template',
            'wts': u'Template',
        }
        self.namespaces[11] = {
            '_default': [u'Template talk', self.namespaces[11]['_default']],
            'ar': u'نقاش قالب',
            'ca': u'Plantilla Discussió',
            'de': u'Vorlage Diskussion',
            'en': u'Template talk',
            'eo': u'Ŝablona diskuto',
            'es': u'Plantilla Discusión',
            'fi': u'Keskustelu mallineesta',
            'fr': u'Discussion Modèle',
            'he': u'שיחת תבנית',
            'hi': u'साँचा वार्ता',
            'hu': u'Sablon vita',
            'it': u'Discussioni template',
            'ja': u'Template‐ノート',
            'nl': u'Overleg sjabloon',
            'pl': u'Dyskusja szablonu',
            'pt': u'Predefinição Discussão',
            'ro': u'Discuţie Format',
            'ru': u'Обсуждение шаблона',
            'sv': u'Malldiskussion',
            'zh': u'Template talk',
            'wts': u'Template talk',
        }
        self.namespaces[12] = {
            '_default': [u'Help', self.namespaces[12]['_default']],
            'ar': u'مساعدة',
            'ca': u'Ajuda',
            'de': u'Hilfe',
            'en': u'Help',
            'eo': u'Helpo',
            'es': u'Ayuda',
            'fi': u'Ohje',
            'fr': u'Aide',
            'he': u'עזרה',
            'hi': u'Help',
            'hu': u'Segítség',
            'it': u'Aiuto',
            'ja': u'Help',
            'nl': u'Help',
            'pl': u'Pomoc',
            'pt': u'Ajuda',
            'ro': u'Ajutor',
            'ru': u'Справка',
            'sv': u'Hjälp',
            'zh': u'Help',
            'wts': u'Help',
        }
        self.namespaces[13] = {
            '_default': [u'Help talk', self.namespaces[13]['_default']],
            'ar': u'نقاش المساعدة',
            'ca': u'Ajuda Discussió',
            'de': u'Hilfe Diskussion',
            'en': u'Help talk',
            'eo': u'Helpa diskuto',
            'es': u'Ayuda Discusión',
            'fi': u'Keskustelu ohjeesta',
            'fr': u'Discussion Aide',
            'he': u'שיחת עזרה',
            'hi': u'Help talk',
            'hu': u'Segítség vita',
            'it': u'Discussioni aiuto',
            'ja': u'Help‐ノート',
            'nl': u'Overleg help',
            'pl': u'Dyskusja pomocy',
            'pt': u'Ajuda Discussão',
            'ro': u'Discuţie Ajutor',
            'ru': u'Обсуждение справки',
            'sv': u'Hjälpdiskussion',
            'zh': u'Help talk',
            'wts': u'Help talk',
        }
        self.namespaces[14] = {
            '_default': [u'Category', self.namespaces[14]['_default']],
            'ar': u'تصنيف',
            'ca': u'Categoria',
            'de': u'Kategorie',
            'en': u'Category',
            'eo': u'Kategorio',
            'es': u'Categoría',
            'fi': u'Luokka',
            'fr': u'Catégorie',
            'he': u'קטגוריה',
            'hi': u'श्रेणी',
            'hu': u'Kategória',
            'it': u'Categoria',
            'ja': u'Category',
            'nl': u'Categorie',
            'pl': u'Kategoria',
            'pt': u'Categoria',
            'ro': u'Categorie',
            'ru': u'Категория',
            'sv': u'Kategori',
            'zh': u'Category',
            'wts': u'Category',
        }
        self.namespaces[15] = {
            '_default': [u'Category talk', self.namespaces[15]['_default']],
            'ar': u'نقاش التصنيف',
            'ca': u'Categoria Discussió',
            'de': u'Kategorie Diskussion',
            'en': u'Category talk',
            'eo': u'Kategoria diskuto',
            'es': u'Categoría Discusión',
            'fi': u'Keskustelu luokasta',
            'fr': u'Discussion Catégorie',
            'he': u'שיחת קטגוריה',
            'hi': u'श्रेणी वार्ता',
            'hu': u'Kategória vita',
            'it': u'Discussioni categoria',
            'ja': u'Category‐ノート',
            'nl': u'Overleg categorie',
            'pl': u'Dyskusja kategorii',
            'pt': u'Categoria Discussão',
            'ro': u'Discuţie Categorie',
            'ru': u'Обсуждение категории',
            'sv': u'Kategoridiskussion',
            'zh': u'Category talk',
            'wts': u'Category talk',
        }
        # Do not add '_default' key into this name space.
        # It cause weird error; Bot says "Please create a file user-config.py, and ...".
        self.namespaces[200] = {
            'wts': u'Tech',
        }
        # Do not add '_default' key into this name space.
        # It cause weird error; Bot says "Please create a file user-config.py, and ...".
        self.namespaces[201] = {
            'wts': u'Tech talk',
        }

        # A few selected big languages for things that we do not want to loop over
        # all languages. This is only needed by the titletranslate.py module, so
        # if you carefully avoid the options, you could get away without these
        # for another wikimedia family.
        self.languages_by_size = ['en','fr','ro']

        # for Wikitravel's /Run subpages check.
        self.wt_script_policy = {
            '_default': u'Script policy',
            'ar': u'Bot',
            'ca': u'Bots',
            'de': u'Regeln für Skripte',
            'en': u'Script policy',
            'eo': u'Roboto',
            'es': u'Bots',
            'fi': u'Botit',
            'fr': u'Règles concernant les scripts',
            'he': u'Bot',
            'hi': u'यंत्रमानव',
            'hu': u'Botok',
            'it': u'Politica script',
            'ja': u'スクリプトの基本方針',
            'nl': u'Richtlijnen scripting',
            'pl': u'Boty',
            'pt': u'Robôs',
            'ro': u'Bot',
            'ru': u'Боты',
            'sv': u'Robotar',
            'zh': u'機器人方針',
            'wts': u'Script policy',
        }

        # String used as separator between interwiki links and the text
        self.interwiki_text_separator = '\r\n'

        # Interwiki sorting order for Wikitravel Shared (wts:)
        self.alphabetic = [
            'ar', 'ca', 'de', 'en', 'eo', 'es', 'fi', 'fr', 'he', 'hi',
            'hu', 'it', 'ja', 'nl', 'pl', 'pt', 'ro', 'ru', 'sv', 'zh',
            'wts'
        ]

        # for Wikitravel Shared (wts:)
            # Which languages have a special order for putting interlanguage links,
            # and what order is it? If a language is not in interwiki_putfirst,
            # alphabetical order on language code is used. For languages that are in
            # interwiki_putfirst, interwiki_putfirst is checked first, and
            # languages are put in the order given there. All other languages are put
            # after those, in code-alphabetical order.
        self.interwiki_putfirst = {
            'ar': self.alphabetic,
            'ca': self.alphabetic,
            'de': self.alphabetic,
            'en': self.alphabetic,
            'eo': self.alphabetic,
            'es': self.alphabetic,
            'fi': self.alphabetic,
            'fr': self.alphabetic,
            'he': self.alphabetic,
            'hi': self.alphabetic,
            'hu': self.alphabetic,
            'it': self.alphabetic,
            'ja': self.alphabetic,
            'nl': self.alphabetic,
            'pl': self.alphabetic,
            'pt': self.alphabetic,
            'ro': self.alphabetic,
            'ru': self.alphabetic,
            'sv': self.alphabetic,
            'zh': self.alphabetic,
        }

        # for Wikitravel Shared (wts:), Previous DOTM, etc.
            # Allows crossnamespace interwiki linking.
            # Lists the possible crossnamespaces combinations
            # keys are originating NS
            # values are dicts where:
            #   keys are the originating langcode, or _default
            #   values are dicts where:
            #       keys are the languages that can be linked to from the lang+ns, or _default
            #       values are a list of namespace numbers
        self.crossnamespace[0] = {
            '_default': {
                '_default': [4],
                'wts': [4, 14],
            },
        }
        self.crossnamespace[4] = {
            '_default': {
                '_default': [0],
            },
        }
        self.crossnamespace[14] = {
            'wts': {
                '_default': [0], 
            },
        }

    # Wikitravel's bot control by checking /Run subpages.
    def bot_control(self,site):
        import urllib
        from wikipedia import Error, Page
        wt_username = urllib.quote(config.usernames[self.name][site.lang].encode('utf-8'))
        wt_namespace = urllib.quote(self.namespaces[2][site.lang].encode('utf-8'))
        wt_user_run = unicode(wt_namespace) + u':' + unicode(wt_username) + u'/Run'
        wt_page = Page(site, wt_user_run)
        wt_user_run_text = wt_page.get(get_redirect = True)
        wt_namespace = urllib.quote(self.namespaces[4][site.lang].encode('utf-8'))
        wt_script_policy = urllib.quote(self.wt_script_policy[site.lang].encode('utf-8'))
        wt_system_run = unicode(wt_namespace) + u':' + unicode(wt_script_policy) + u'/Run'
        wt_page = Page(site, wt_system_run)
        wt_system_run_text = wt_page.get(get_redirect = True)
        if 'yes' not in wt_user_run_text or 'yes' not in wt_system_run_text:
            raise Error('Bot stopped by /Run page on %s -- %s = %s , %s = %s'
                     % (site.lang, wt_user_run, wt_user_run_text, wt_system_run, wt_system_run_text))
        return True

    def hostname(self,code):
        return 'wikitravel.org'

    # fix for Wikitravel's mediawiki message setting
    def mediawiki_message(self,site):
        # (eo:)
        if site.lang == 'eo':
            site._mediawiki_messages['readonly_lag'] = u'The database has been automatically locked while the slave database servers catch up to the master'
        # (hi:)
        if site.lang == 'hi':
            site._mediawiki_messages['readonly'] = u'Database locked'
            site._mediawiki_messages['readonly_lag'] = u'The database has been automatically locked while the slave database servers catch up to the master'
        return site

    def scriptpath(self, code):
        # for Wikitravel Shared (wts:)
        if code == 'wts':
            return '/wiki/shared'
        else:
            return '/wiki/%s' % code

    def shared_image_repository(self, code):
        return ('wikitravel_shared', 'wikitravel_shared')

    # fix for Wikitravel's user page link.
    def user_page_link(self,site,index):
        site._isLoggedIn[index] = True
        site._userName[index] = config.usernames[self.name][site.lang].encode('utf-8')
        return site

    def version(self, code):
        return "1.11.2"

