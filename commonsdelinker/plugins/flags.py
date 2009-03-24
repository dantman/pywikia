__version__ = '$Id: $'

import re

class NlWiki(object):
    hook = 'gallery_replace'
    def __init__(self, CommonsDelinker):
        self.CommonsDelinker = CommonsDelinker
    def __call__(self, page, summary, image, replacement, match, groups):
        site = page.site()
        if (site.lang, site.family.name) == ('nl', 'wikipedia') and replacement.get() is None:
            commands = self.CommonsDelinker.SummaryCache.get(site, 'Vlaggen', default = '')
            
            flags = re.findall(r'(?s)\<\!\-\-begin\-flags (.*?)\-\-\>(.*?)\<\!\-\-end\-flags\-\-\>', commands)
            text = page.get()
            
            namespace = site.namespace(14)
            r_namespace = r'(?:[Cc]ategory)|(?:[%s%s]%s)' % \
                (namespace[0], namespace[0].lower(), namespace[1:])
                    
            for new_image, categories in flags:
                for category in categories.split('\n'):
                    if category.strip() == '': continue
                    
                    r_cat = r'\[\[\s*%s\s*\:\s*%s\s*(?:\|.*?)?\s*\]\]' % (r_namespace, 
                        re.sub(r'\\[ _]', '[ _]', re.escape(category.strip())))
                    if re.search(r_cat, text):
                        self.CommonsDelinker.output(
                            u'%s %s replaced by %s in category %s' % \
                            (self, image, new_image, category))
                        replacement.set(new_image.replace(' ', '_'))
            