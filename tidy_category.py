# -*- coding: cp1252 -*-
"""
Script to help a human to tidy up a category by moving its articles into
subcategories

Specify the category name on the command line. The program will
pick up the page, and look for all subcategories, and show them with
a number adjacent to them. It will then automatically loop over all pages
in the category. It will ask you to type the number of the appropriate
replacement, and perform the change robotically.

Multiple references in one page will be scanned in order, but typing 'n' on
any one of them will leave the complete page unchanged; it is not possible to
leave only one reference unchanged.

Important:
 * every category page must contain some text; otherwise an edit box will be
   displayed instead of an article list, and the bot won't work
 * this bot is written to work with the MonoBook skin, so make sure your bot
   account uses this skin
"""

# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.

import wikipedia, config, catlib
import re, sys

# This is a purely interactive robot. We set the delays lower.
wikipedia.get_throttle.setDelay(5)
wikipedia.put_throttle.setDelay(10)

# Summary message
msg={
    'en':'Robot: Changing category: %s',
    'de':'Bot: \xc4ndere Kategorie: %s',
    }


# This is a temporary knowledge base (dictionary data type) for all known
# supercategory-subcategory relationships, so that category pages don't need to
# be loaded over and over again

subclassDB={}

# for a given supercategory, return a list of all its subcategories.
# save this list in a temporary database so that it won't be loaded from the
# server next time it's required.
def get_subcats(supercat):
    # if we already know which subcategories exist here
    if subclassDB.has_key(supercat):
        return subclassDB[supercat]
    else:
        subcatlist = supercat.subcategories()
        # add to dictionary
        subclassDB[supercat] = subcatlist
        return subcatlist

# given an article which is in category original_cat, ask the user if it should
# be moved to one of original_cat's subcategories. Recursively run through
# subcategories' subcategories.
# NOTE: current_cat is only used for internal recursion. You should always use
# current_cat = original_cat.
def move_to_subcategory(article, original_cat, current_cat):
    print
    print 'Treating page ' + article.ascii_linkname() + ', currently in category ' + current_cat.ascii_linkname()
    subcatlist = get_subcats(current_cat)
    print
    if len(subcatlist) == 0:
        print 'This category has no subcategories.'
        print
    for i in range(len(subcatlist)):
        print '%d - Move to %s' % (i, subcatlist[i])
    print 'Enter - Save category as ' + current_cat.ascii_linkname()
    
    choice=raw_input("Choice: ")
    if choice == '':
        print 'Saving category as ' + current_cat.ascii_linkname()
        if current_cat == original_cat:
            print 'No changes necessarry.'
        else:
            # Save the changes
            cats = article.categories()
            cats.remove(original_cat)
            cats.append(current_cat)
            text = article.get()
            text = wikipedia.replaceCategoryLinks(text, cats)
            print "Changing page %s" %(article)
            article.put(text)
    else:
        try:
            choice=int(choice)
        except ValueError:
            pass
        # recurse into subcategory
        move_to_subcategory(article, original_cat, subcatlist[choice])
    
cat_title = raw_input('Which category do you want to tidy up? ')
catlink = catlib.CatLink(cat_title)

# get edit summary message
wikipedia.setAction(msg[wikipedia.chooselang(wikipedia.mylang,msg)] % cat_title)


articles = catlink.articles(recurse = 0)
if len(articles) == 0:
    print 'There are no articles in category ' + cat_title
else:
    for article in articles:
        print
        print '==================================================================='
        move_to_subcategory(article, catlink, catlink)