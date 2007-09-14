# -*- coding: utf-8  -*-
"""
"""

#
# (C) Francesco Cosoleto, 2006
#
# Distributed under the terms of the MIT license.
#

import sys, re, codecs, os, time, shutil
import wikipedia, config

from copyright import put, join_family_data, appdir, reports_cat

#
# Month + Year save method
append_date_to_wiki_save_path = True

#
# Add pubblication date to entries (template:botdate)
append_date_to_entries = False

msg_table = {
    'it': {'_default': [u'Pagine nuove', u'Nuove voci'],
           'feed': [u'Aggiunte a voci esistenti', u'Testo aggiunto in']},
    'en': {'_default': [u'New entries', u'New entries']}
}

wiki_save_path = {
  '_default': u'User:%s/Report' % config.usernames[wikipedia.getSite().family.name][wikipedia.getSite().lang],
  'it': u'Utente:RevertBot/Report'
}

template_cat = {
  '_default': [u'This template is used by copyright.py, a script part of [[:m:Using the python wikipediabot|PyWikipediaBot]].', u''],
  'it': [u'Questo template è usato dallo script copyright.py del [[:m:Using the python wikipediabot|PyWikipediaBot]].', u'Template usati da bot'],
}

wiki_save_path = wikipedia.translate(wikipedia.getSite(), wiki_save_path)
template_cat = wikipedia.translate(wikipedia.getSite(), template_cat)

separatorC = re.compile('(?m)^== +')

def set_template():

    site = wikipedia.getSite()
    url = "%s://%s%s" % (site.protocol, site.hostname(), site.path()

    botdate = u"""
<div style="text-align:right">{{{1}}}</div><noinclude>%s\n[[%s:%s]]</noinclude>
""" % (template_cat[0], site.namespace(14), template_cat[1])

    botbox = """
<div class=plainlinks style="text-align:right">[%s?title={{{1}}}&diff={{{2}}}&oldid={{{3}}} diff] - [%s?title={{{1}}}&action=history cron] - [%s?title=Special:Log&page={{{1}}} log]</div>
""" % url, url, url)

    if append_date_to_entries:
        p = wikipedia.Page(site, 'Template:botdate')
        if not p.exists()
            p.put(botdate)

def output_files_gen():
    for f in os.listdir(appdir):
        if 'output' in f and not '_pending' in f:
            m = re.search('output_(.*?)\.txt', f)
            if m:
                tag = m.group(1)
            else:
                tag = '_default'

            section_name_and_summary = wikipedia.translate(wikipedia.getSite(), msg_table)[tag]

            section = section_name_and_summary[0]
            summary = section_name_and_summary[1]

            yield appdir + f, section, summary

def read_output_file(filename):
    if os.path.isfile(filename + '_pending'):
        shutil.move(filename, filename + '_temp')
        ap = codecs.open(filename + '_pending', 'a', 'utf-8')
        ot = codecs.open(filename + '_temp', 'r', 'utf-8')
        ap.write(ot.read())
        ap.close()
        ot.close()
        os.remove(filename + '_temp')
    else:
        shutil.move(filename, filename + '_pending')

    f = codecs.open(filename + '_pending', 'r', 'utf-8')
    data = f.read()
    f.close()

    return data

if append_date_to_wiki_save_path:
    import date
    wiki_save_path += '_' + date.formats['MonthName'][wikipedia.getSite().language()](time.localtime()[1]) + '_' + str(time.localtime()[0])

page = wikipedia.Page(wikipedia.getSite(),wiki_save_path)

try:
    wikitext = page.get()
except wikipedia.NoPage:
    wikipedia.output("%s not found." % page.aslink())
    wikitext = '[[%s:%s]]\n' % (wikipedia.getSite().namespace(14), wikipedia.translate(wikipedia.getSite(), reports_cat))

final_summary = u''
output_files = list()

for f, section, summary in output_files_gen():
    wikipedia.output('File: \'%s\'\nSection: %s\n' % (f, section))

    output_data = read_output_file(f)
    output_files.append(f)

    entries = re.findall('=== (.*?) ===', output_data)

    if not entries:
        continue

    if append_date_to_entries:
        dt = time.strftime('%d-%m-%Y %H:%M', time.localtime())
        output_data = re.sub("(?m)^(=== \[\[.*?\]\] ===\n)", r"\1{{botdate|%s}}\n" % dt, output_data)

    m = re.search('(?m)^==\s*%s\s*==' % section, wikitext)
    if m:
        m_end = re.search(separatorC, wikitext[m.end():])
        if m_end:
            wikitext = wikitext[:m_end.start() + m.end()] + output_data + wikitext[m_end.start() + m.end():]
        else:
            wikitext += '\n' + output_data
    else:
        wikitext += '\n' + output_data

    if final_summary:
        final_summary += ' '
    final_summary += u'%s: %s' % (summary, ', '.join(entries))

if final_summary:
    wikipedia.output(final_summary + '\n')

    # if a page in 'Image' or 'Category' namespace is checked then fix
    # title section by adding ':' in order to avoid wiki code effects.

    wikitext = re.sub(u'(?i)=== \[\[%s:' % join_family_data('Image', 6), ur'== [[:\1:', wikitext)
    wikitext = re.sub(u'(?i)=== \[\[%s:' % join_family_data('Category', 14), ur'== [[:\1:', wikitext)

    # TODO:
    # List of frequent rejected address to improve upload process.

    wikitext = re.sub('http://(.*?)((forumcommunity|forumfree).net)',r'<blacklist>\1\2', wikitext)

    if len(final_summary)>=200:
        final_summary = final_summary[:200]
        final_summary = final_summary[:add_comment.rindex("[")-3] + "..."

    try:
        put(wikitext, comment = final_summary)
        for f in output_files:
            os.remove(f + '_pending')
            wikipedia.output("\'%s\' deleted." % f)
    except wikipedia.PageNotSaved:
        raise

wikipedia.stopme()
